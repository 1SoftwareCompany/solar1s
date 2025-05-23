"""Sensor to calculate the sold energy in BGN per hour."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import EntityCategory


class SoldEnergySensor(SensorEntity):
    """Sensor to calculate the sold energy in BGN per hour."""

    def __init__(self, coordinator, energy_price_sensor: str, produced_energy_entity: str):
        """Initialize the Sold Energy sensor."""
        self.coordinator = coordinator
        self.energy_price_sensor = energy_price_sensor
        self.produced_energy_entity = produced_energy_entity
        self._attr_name = "Sold Energy BGN"
        self._attr_unique_id = "sold_energy_bgn"
        self._attr_device_class = "monetary"
        self._attr_native_unit_of_measurement = "BGN"

    @property
    def state(self) -> float | None:
        """Calculate and return the sold energy in BGN."""
        energy_price_state = self.hass.states.get(self.energy_price_sensor)
        if not energy_price_state or energy_price_state.state in (None, "unknown", "unavailable"):
            return None

        produced_energy_state = self.hass.states.get(self.produced_energy_entity)
        if not produced_energy_state or produced_energy_state.state in (None, "unknown", "unavailable"):
            return None

        try:
            price_per_mwh = float(energy_price_state.state)
            produced_energy_kwh = float(produced_energy_state.state)
            price_per_kwh = price_per_mwh / 1000
            sold_energy_bgn = price_per_kwh * produced_energy_kwh
            return round(sold_energy_bgn, 2)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "produced_energy_entity": self.produced_energy_entity,
            "energy_price_sensor": self.energy_price_sensor,
        }