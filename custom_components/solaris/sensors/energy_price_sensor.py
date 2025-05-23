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
        """Return the price for the current time."""
        if not self.coordinator.data:
            return None

        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        now = dt_util.now()  # Current time in the local timezone
        _LOGGER.debug("Current local time: %s", now)

        for i in range(len(hits) - 1):
            try:
                # Parse the current and next timestamps
                current_timestamp = parse_datetime(hits[i]["_source"].get("@timestamp"))
                next_timestamp = parse_datetime(hits[i + 1]["_source"].get("@timestamp"))

                if not current_timestamp or not next_timestamp:
                    continue

                # Convert timestamps to local timezone
                current_timestamp_local = dt_util.as_local(current_timestamp)
                next_timestamp_local = dt_util.as_local(next_timestamp)

                _LOGGER.debug(
                    "Checking range: %s - %s", current_timestamp_local, next_timestamp_local
                )

                # Check if 'now' is between the current and next timestamps
                if current_timestamp_local <= now < next_timestamp_local:
                    price = float(hits[i]["_source"].get("price_bgn"))
                    _LOGGER.debug("Selected price: %s", price)
                    return price
            except (TypeError, ValueError) as e:
                _LOGGER.error("Error parsing price or timestamp: %s", e)
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