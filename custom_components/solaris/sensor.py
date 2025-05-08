from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType, ConfigType
from typing import Any

async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities):
    async_add_entities([EmployeeSensor()])

class EmployeeSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "Employee Mynkow"
        self._attr_unique_id = "employee_mynkow"
        self._attr_native_value = "active"
        self._attr_extra_state_attributes = {"name": "mynkow"}
