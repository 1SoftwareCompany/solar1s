from custom_components.solaris.const import DOMAIN

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.helpers.entity import DeviceInfo, EntityCategory


class PriceThresholdEntity(RestoreNumber):
    """Entity to set a price threshold for energy, with persistent value."""

    def __init__(self, unique_id: str, client_id: str, client_location: str) -> None:
        self._attr_name = f"Price threshold {client_id} {client_location}"
        self._attr_unique_id = f"{unique_id}_price_threshold"
        self._client_id = client_id
        self._location = client_location

        self._attr_min_value = 0.0
        self._attr_max_value = 10000.0
        self._attr_step = 0.01
        self._native_value = 0.0  # Default fallback
        self._attr_unit_of_measurement = "BGN/MWh"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_mode = NumberMode.BOX

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        restored_data = await self.async_get_last_number_data()

        if restored_data is not None and restored_data.native_value is not None:
            self._native_value = restored_data.native_value
        else:
            self._native_value = 0.0  # fallback default

    async def async_set_native_value(self, value: float) -> None:
        self._native_value = value
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._client_id}_{self._location}")},
            name=f"Solaris {self._client_id} - {self._location}",
            manufacturer="1Software Company",
            model="Solar1s Price Sensors",
        )

    @property
    def native_value(self) -> float:
        return self._native_value

    @property
    def available(self) -> bool:
        return True

    @property
    def native_min_value(self) -> float:
        return 0.0

    @property
    def native_max_value(self) -> float:
        return 10000.0

    @property
    def native_step(self) -> float:
        return 0.01
