"""Sensor to calculate the earnings from sold energy."""

from custom_components.solaris.const import DOMAIN

from homeassistant.components.sensor import SensorEntity


class EarningsSensor(SensorEntity):
    """Sensor to calculate the sold energy in BGN per hour."""

    def __init__(
        self,
        unique_id: str,
        client_id: str,
        client_location: str,
        energy_price_entity: str,
        produced_energy_entity: str,
    ):
        """Initialize the Earnings sensor."""
        self.unique_id = f"{unique_id}_earnings"
        self.client_id = client_id
        self.client_location = client_location
        self.energy_price_entity = energy_price_entity
        self.produced_energy_entity = produced_energy_entity
        self._attr_name = f"Earnings {self.client_id} {self.client_location}"
        self._attr_unique_id = self.unique_id
        self._attr_device_class = "monetary"
        self._attr_native_unit_of_measurement = "BGN"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, f"{self.client_id}_{self.client_location}")},
            "name": f"Solaris {self.client_id} - {self.client_location}",
            "manufacturer": "1Software Company",
            "model": "Solar1s Price Sensors",
            "entry_type": "service",
        }

    @property
    def state(self) -> float | None:
        """Calculate and return the sold energy in BGN."""
        energy_price_state = self.hass.states.get(self.energy_price_entity)
        if not energy_price_state or energy_price_state.state in (
            None,
            "unknown",
            "unavailable",
        ):
            return None

        produced_energy_state = self.hass.states.get(self.produced_energy_entity)
        if not produced_energy_state or produced_energy_state.state in (
            None,
            "unknown",
            "unavailable",
        ):
            return None

        try:
            price_per_mwh = float(energy_price_state.state)
            produced_energy_kwh = float(produced_energy_state.state)
            price_per_kwh = price_per_mwh / 1000
            sold_energy_bgn = price_per_kwh * produced_energy_kwh
            return round(sold_energy_bgn, 3)
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "client_id": self.client_id,
            "client_location": self.client_location,
            "produced_energy": self.produced_energy_entity,
            "energy_price": self.energy_price_entity,
        }
