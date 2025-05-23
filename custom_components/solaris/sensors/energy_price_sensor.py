"""Sensor to hold all electricity prices from the API."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from typing import Any


class EnergyPriceSensor(SensorEntity):
    """Sensor to hold all electricity prices from the API."""

    _attr_has_entity_name = True
    _attr_name = "All Prices"
    _attr_unique_id = "all_energy_prices"
    _attr_device_class = "monetary"
    _attr_native_unit_of_measurement = "BGN/MWh"

    def __init__(self, coordinator: Any):
        """Initialize the All Prices sensor."""
        self.coordinator = coordinator

    @property
    def state(self) -> float | None:
        """Return the price for the current time."""
        if not self.coordinator.data:
            return None

        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        now = dt_util.now()
        for i in range(len(hits) - 1):
            try:
                current_timestamp = dt_util.parse_datetime(hits[i]["_source"].get("@timestamp"))
                next_timestamp = dt_util.parse_datetime(hits[i + 1]["_source"].get("@timestamp"))

                if not current_timestamp or not next_timestamp:
                    continue

                current_timestamp_local = dt_util.as_local(current_timestamp)
                next_timestamp_local = dt_util.as_local(next_timestamp)

                if current_timestamp_local <= now < next_timestamp_local:
                    return float(hits[i]["_source"].get("price_bgn"))
            except (TypeError, ValueError):
                continue

        return None