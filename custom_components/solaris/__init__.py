from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass, config_entry):
    return True