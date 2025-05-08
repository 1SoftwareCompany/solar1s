from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from datetime import timedelta
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

API_URL = "http://10.1.1.85:9200/metrics-ibex/_search"
USERNAME = "elastic"
PASSWORD = "123qwe123qwe##asd"

class ElectricityPriceCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            _LOGGER,
            name="electricity_prices",
            update_interval=timedelta(minutes=5),
        )

    async def _async_update_data(self):
        payload = {
            "size": 48,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now-3h/d",
                        "lte": "now+1d+20h/d",
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
                        return data
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

class ElectricityPriceSensor(SensorEntity):
    def __init__(self, coordinator, index):
        self.coordinator = coordinator
        self.index = index
        self._attr_unique_id = f"energy_price_{index:02}"
        self._attr_name = f"Energy Price Hour {index:02}"
        self._attr_unit_of_measurement = "BGN"

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def state(self):
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        if hits and len(hits) > self.index:
            price = hits[self.index].get("_source", {}).get("price_bgn")
            try:
                return float(price)
            except (TypeError, ValueError):
                return float("nan")  # or return None
        return float("nan")  # or return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = ElectricityPriceCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    sensors = [ElectricityPriceSensor(coordinator, i) for i in range(48)]
    async_add_entities(sensors)
