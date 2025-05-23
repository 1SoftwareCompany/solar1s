"""Sensor to hold all electricity prices from the API."""

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.util import dt as dt_util
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from typing import Any
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import parse_datetime
import logging

from ..ibex_coordinator import IbexCoordinator

_LOGGER = logging.getLogger(__name__)

class EnergyPriceSensor(SensorEntity):
    """Sensor to hold all electricity prices from the API."""

    _attr_has_entity_name = True
    _attr_name = "All Prices"
    _attr_unique_id = "all_energy_prices"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BGN/MWh"

    def __init__(self, coordinator: IbexCoordinator):
        """Initialize the All Prices sensor."""
        self.coordinator = coordinator

    @property
    def state(self) -> float | None:
        """Return the price for the current or next hour."""
        if not self.coordinator.data:
            return None
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        now = dt_util.now()
        for hit in hits:
            try:
                # Convert the timestamp to the local timezone
                timestamp = dt_util.as_local(parse_datetime(hit["_source"].get("@timestamp")))
                if timestamp and timestamp >= now:
                    return float(hit["_source"].get("price_bgn"))
            except (TypeError, ValueError):
                continue
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return all prices as state attributes."""
        if not self.coordinator.data:
            return {"prices": None}
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        prices = []
        for hit in hits:
            try:
                price = float(hit["_source"].get("price_bgn"))
                timestamp = hit["_source"].get("@timestamp")
                prices.append({"timestamp": timestamp, "price": price})
            except (TypeError, ValueError):
                continue
        return {"prices": prices}

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self.coordinator.last_update_success is not None

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

    async def async_update(self):
        """Request an update from the coordinator."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Handle when the entity is added to Home Assistant."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))