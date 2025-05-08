from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_registry import async_get as async_get_registry

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from homeassistant.helpers import entity_platform
import logging

_LOGGER = logging.getLogger(__name__)
DOMAIN = "solaris"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    _LOGGER.info("Setting up OneSoft Solaris integration")

    # Register the entity directly
    async def setup_entities():
        async_add_entities = hass.helpers.entity_component.async_add_entities

        class EmployeeEntity(Entity):
            def __init__(self):
                self._attr_name = "Employee Mynkow"
                self._attr_unique_id = "employee_mynkow"
                self._attr_state = "active"
                self._attr_extra_state_attributes = {"name": "mynkow"}

            @property
            def name(self):
                return self._attr_name

            @property
            def state(self):
                return self._attr_state

            @property
            def extra_state_attributes(self):
                return self._attr_extra_state_attributes

            @property
            def unique_id(self):
                return self._attr_unique_id

        await hass.helpers.entity_component.async_add_entities([EmployeeEntity()])

    hass.async_create_task(setup_entities())

    return True
