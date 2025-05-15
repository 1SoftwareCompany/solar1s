from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.core import callback
from homeassistant.util import dt as dt_util
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
)
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.event import async_track_time_change
from datetime import datetime, timedelta, timezone
from homeassistant.util.dt import parse_datetime
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

API_URL = "http://10.1.1.85:9200/metrics-ibex/_search"
USERNAME = "elastic"
PASSWORD = "123qwe123qwe##asd"

class IbexCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch and manage electricity price data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="electricity_prices",
            update_interval=timedelta(minutes=5),
        )
        self._last_success = None  # Track the last successful update time
        self._store = Store(hass, 1, "custom_energy_price_cache.json")  # Persistent storage
        self._previous_data = None  # Cache for the last successful data

    async def _async_update_data(self) -> dict:
        """Fetch data from the API and handle errors."""
        payload = {
            "size": 48,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now/d",
                        "lte": "now+1d/d",
                        "time_zone": "+03:00"
                    }
                }
            },
            "sort": [{"@timestamp": {"order": "asc"}}]
        }

        headers = {"Content-Type": "application/json"}

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.post(API_URL, json=payload, headers=headers, auth=aiohttp.BasicAuth(USERNAME, PASSWORD)) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"HTTP error: {response.status}")
                        data = await response.json()
                        self._last_success = datetime.now(timezone.utc)  # Update with timezone-aware datetime
                        await self._store_data(data)  # Save the data to persistent storage
                        self._previous_data = data  # Cache the data in memory
                        return data
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            if self._previous_data:
                _LOGGER.debug("Using cached data due to API failure")
                return self._previous_data  # Use cached data if available
            raise UpdateFailed("No data available and API request failed") from err

    async def _store_data(self, data: dict) -> None:
        """Store data persistently."""
        await self._store.async_save(data)

    async def _load_data(self) -> dict | None:
        """Load data from persistent storage."""
        return await self._store.async_load()

    async def async_config_entry_first_refresh(self) -> None:
        """Load cached data on startup before the first refresh."""
        cached_data = await self._load_data()
        if cached_data:
            _LOGGER.debug("Loaded cached data on startup")
            self._previous_data = cached_data

    @property
    def last_success_time(self) -> datetime | None:
        """Return the datetime of the last successful update."""
        return self._last_success

class PriceHourSensor(SensorEntity):
    """Sensor for hourly electricity prices."""

    def __init__(self, coordinator, index):
        """Initialize the hourly price sensor."""
        self.coordinator = coordinator
        self.index = index
        self._attr_unique_id = f"energy_price_{index:02}"
        self._attr_name = f"Energy Price Hour {index:02}"
        self._attr_native_unit_of_measurement = "BGN/MWh"
        self._attr_device_class = "monetary"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self.coordinator.last_update_success is not None

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None  # Return None if no data is available
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        if hits and len(hits) > self.index:
            price = hits[self.index].get("_source", {}).get("price_bgn")
            try:
                return float(price)
            except (TypeError, ValueError):
                return None  # Use None for invalid state
        return None  # Use None if no data for the index

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {
                "start_timestamp": None,
                "end_timestamp": None,
            }  # Return empty attributes if no data is available
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        if hits and self.index < len(hits):
            try:
                hit = hits[self.index]
                ts = hit["_source"].get("@timestamp")
                start = parse_datetime(ts)
                end = start + timedelta(hours=1) if start else None
                return {
                    "start_timestamp": start.isoformat() if start else None,
                    "end_timestamp": end.isoformat() if end else None,
                }
            except Exception as e:
                _LOGGER.error("Failed to parse timestamps for hour %s: %s", self.index, e)
        return {
            "start_timestamp": None,
            "end_timestamp": None,
        }

    async def async_update(self):
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Handle when the entity is added to Home Assistant."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class IbexPricesLastUpdatedSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Ibex Prices Last Updated"
        self._attr_unique_id = "ibex_price_last_updated"
        self._attr_device_class = "timestamp"

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the last successful update time in local timezone."""
        last_success = self.coordinator.last_success_time
        if last_success:
            # Convert the UTC datetime to local timezone
            return last_success.isoformat()
        return None

    @property
    def device_info(self):
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class CurrentPriceSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Current Price"
    _attr_unique_id = "energy_price_now"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BGN/MWh"

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

        # Update hourly
        async_track_time_change(hass, self._update, minute=0, second=0)

        # Update when any of the hourly sensors change
        async_track_state_change_event(hass, self._watched_entities(), self._update)

    def _watched_entities(self) -> list[str]:
        return [f"sensor.energy_price_hour_{i:02d}" for i in range(48)]

    async def _update(self, *args):
        """Trigger an update and write the new state."""
        self.async_write_ha_state()

    @property
    def state(self) -> float | None:
        now_hour = dt_util.now().hour
        entity_id = f"sensor.energy_price_hour_{now_hour:02d}"
        state = self.hass.states.get(entity_id)
        if state and state.state not in (None, "unknown", "unavailable"):
            try:
                return float(state.state)
            except ValueError:
                return None
        return None

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def should_poll(self) -> bool:
        return False  # This is a calculated, event-driven sensor

    @property
    def device_info(self):
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Solaris sensors."""
    coordinator = IbexCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()  # Load cached data on startup

    price_sensors = [PriceHourSensor(coordinator, i) for i in range(48)]
    last_updated_sensor = IbexPricesLastUpdatedSensor(coordinator)

    async_add_entities(price_sensors + [last_updated_sensor])

    # Delay adding CurrentPriceSensor until all others are registered
    async def _add_current_price_sensor(_now):
        async_add_entities([CurrentPriceSensor(hass)])

    hass.loop.call_later(1, lambda: hass.async_create_task(_add_current_price_sensor(None)))
