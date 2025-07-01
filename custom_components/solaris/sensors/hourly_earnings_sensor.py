from zoneinfo import ZoneInfo

from custom_components.solaris.const import DOMAIN

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity


class HourlyEarningsSensor(SensorEntity, RestoreEntity):
    def __init__(
        self,
        hass,
        unique_id: str,
        client_id: str,
        client_location: str,
        yield_entity_id,
        price_entity_id,
    ):
        self.unique_id = f"{unique_id}_hourly_earnings"
        self.client_id = client_id
        self.client_location = client_location
        self._attr_name = f"Hourly Earnings {self.client_id} {self.client_location}"
        self._attr_native_unit_of_measurement = "BGN"
        self._attr_unique_id = self.unique_id
        self._yield_entity = yield_entity_id
        self._price_entity = price_entity_id
        self._value = 0.0
        self._hass = hass
        self._callbacks_set = False

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._callbacks_set = True

        @callback
        def _on_yield_update(entity_id, old_state, new_state):
            try:
                yield_kwh = float(new_state.state)

                updated_time_utc = new_state.last_updated

                cet = ZoneInfo("Europe/Paris")
                updated_time_cet = updated_time_utc.astimezone(cet)

                # Round DOWN to the current full hour
                current_hour_time = updated_time_cet.replace(
                    minute=0, second=0, microsecond=0
                )
                current_hour_iso = current_hour_time.isoformat()

                # Get the price list
                price_entity = self._hass.states.get(self._price_entity)
                if not price_entity:
                    self._value = 0.0
                    return

                prices = price_entity.attributes.get("prices", [])
                price_match = next(
                    (p["price"] for p in prices if p["timestamp"] == current_hour_iso),
                    None,
                )

                if price_match is None:
                    self._value = 0.0
                    return

                price_kwh = float(price_match) / 1000  # Convert from MWh to kWh
                self._value = round(yield_kwh * price_kwh, 3)

                self.async_write_ha_state()
                self._hass.bus.async_fire(self.unique_id, {"value": self._value})

            except Exception as e:
                self._value = 0.0

        unsub = async_track_state_change(
            self._hass, self._yield_entity, _on_yield_update
        )
        self.async_on_remove(unsub)

    @property
    def native_value(self):
        return self._value

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
