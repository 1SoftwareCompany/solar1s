from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform
from .const import DOMAIN

async def async_setup_platform(hass: HomeAssistant, config, async_add_entities, discovery_info=None):
    async_add_entities([EmployeeSensor()], True)

class EmployeeSensor(Entity):
    def __init__(self):
        self._name = "mynkow"
        self._state = "active"

    @property
    def name(self):
        return f"Employee {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return "employee_mynkow"

    @property
    def extra_state_attributes(self):
        return {
            "name": self._name
        }