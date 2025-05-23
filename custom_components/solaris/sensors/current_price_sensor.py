"""Sensors for current energy prices."""

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_change
from homeassistant.util import dt as dt_util
import logging

_LOGGER = logging.getLogger(__name__)


class CurrentPriceSensor(SensorEntity):
    """Sensor for the current energy price per MWh."""

    _attr_has_entity_name = True
    _attr_name = "Current Price MWh"
    _attr_unique_id = "energy_price_now"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BGN/MWh"

    def __init__(self, hass: HomeAssistant):
        """Initialize the Current Price Sensor."""
        self.hass = hass

        # Update hourly
        async_track_time_change(hass, self._update, minute=0, second=0)

        # Update when any of the hourly sensors change
        async_track_state_change_event(hass, self._watched_entities(), self._update)

    def _watched_entities(self) -> list[str]:
        """Return the list of hourly price sensors to watch."""
        return [f"sensor.energy_price_hour_{i:02d}" for i in range(48)]

    async def _update(self, *args):
        """Trigger an update and write the new state."""
        self.async_write_ha_state()

    @property
    def state(self) -> float | None:
        """Return the current price per MWh."""
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
        """Return the unique ID of the sensor."""
        return self._attr_unique_id

    @property
    def should_poll(self) -> bool:
        """Indicate that this sensor does not require polling."""
        return False

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }


class CurrentPriceSensorKWH(SensorEntity):
    """Sensor for the current energy price per kWh."""

    _attr_has_entity_name = True
    _attr_name = "Current Price kWh"
    _attr_unique_id = "energy_price_now_kwh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BGN/kWh"

    def __init__(self, hass: HomeAssistant):
        """Initialize the Current Price Sensor for kWh."""
        self.hass = hass

        # Update hourly
        async_track_time_change(hass, self._update, minute=0, second=0)

        # Update when any of the hourly sensors change
        async_track_state_change_event(hass, self._watched_entities(), self._update)

    def _watched_entities(self) -> list[str]:
        """Return the list of hourly price sensors to watch."""
        return [f"sensor.energy_price_hour_{i:02d}" for i in range(48)]

    async def _update(self, *args):
        """Trigger an update and write the new state."""
        self.async_write_ha_state()

    @property
    def state(self) -> float | None:
        """Return the current price per kWh."""
        now_hour = dt_util.now().hour
        entity_id = f"sensor.energy_price_hour_{now_hour:02d}"
        state = self.hass.states.get(entity_id)
        if state and state.state not in (None, "unknown", "unavailable"):
            try:
                return float(state.state) / 1000
            except ValueError:
                return None
        return None

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._attr_unique_id

    @property
    def should_poll(self) -> bool:
        """Indicate that this sensor does not require polling."""
        return False

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }