from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import parse_datetime
from homeassistant.helpers.entity import EntityCategory
import logging

_LOGGER = logging.getLogger(__name__)


class PriceHourSensor(CoordinatorEntity, SensorEntity):
    """Sensor for hourly electricity prices."""

    def __init__(self, coordinator, index: int):
        """Initialize the hourly price sensor."""
        super().__init__(coordinator)
        self.index = index
        self._attr_unique_id = f"energy_price_{index:02}"
        self._attr_name = f"Energy Price Hour {index:02}"
        self._attr_native_unit_of_measurement = "BGN/MWh"
        self._attr_device_class = "monetary"

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

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return self.coordinator.last_update_success is not None

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        hits = self.coordinator.data.get("hits", {}).get("hits", [])
        if hits and len(hits) > self.index:
            price = hits[self.index].get("_source", {}).get("price_bgn")
            try:
                return float(price)
            except (TypeError, ValueError):
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {"start_timestamp": None, "end_timestamp": None}
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
        return {"start_timestamp": None, "end_timestamp": None}