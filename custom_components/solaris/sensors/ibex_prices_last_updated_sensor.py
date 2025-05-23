"""Sensor for tracking the last update time of Ibex prices."""

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
from homeassistant.util.dt import parse_datetime, as_local
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)


class IbexPricesLastUpdatedSensor(SensorEntity):
    """Sensor for tracking the last update time of Ibex prices."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = "Ibex Prices Last Updated"
        self._attr_unique_id = "ibex_price_last_updated"
        self._attr_device_class = "timestamp"

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self.coordinator.last_update_success

    @property
    def state(self) -> str | None:
        """Return the last successful update time in local timezone."""
        last_success = self.coordinator.last_success_time
        if last_success:
            return as_local(last_success).isoformat()
        return None

    @property
    def device_info(self) -> dict:
        """Return device information."""
        return {
            "identifiers": {("solaris", "mynkow")},
            "name": "Solar1s",
            "manufacturer": "1SoftwareCompany",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }