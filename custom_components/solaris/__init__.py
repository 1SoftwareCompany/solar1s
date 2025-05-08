from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}

    # Load the sensor platform
    hass.async_create_task(
        async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True