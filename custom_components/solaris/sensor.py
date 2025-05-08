from homeassistant.components.sensor import SensorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([EmployeeSensor()])

class EmployeeSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "Employee Mynkow"
        self._attr_unique_id = "employee_mynkow"
        self._attr_native_value = "active"
        self._attr_extra_state_attributes = {"name": "mynkow"}
