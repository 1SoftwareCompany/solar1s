from homeassistant.config_entries import ConfigFlow
from .const import DOMAIN

class SolarisConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="Solaris", data={})
