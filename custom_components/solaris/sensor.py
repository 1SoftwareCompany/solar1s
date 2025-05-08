from homeassistant.components.sensor import SensorEntity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([EmployeeSensor()])

class EmployeeSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "Employee Mynkow"
        self._attr_unique_id = "employee_mynkow"
        self._attr_native_value = "active"
        self._attr_extra_state_attributes = {"name": "mynkow"}
