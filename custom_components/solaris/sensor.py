from homeassistant.components.sensor import SensorEntity

class EmployeeSensor(SensorEntity):
    def __init__(self):
        self._attr_name = "Employee Mynkow"
        self._attr_unique_id = "employee_mynkow"
        self._attr_native_value = "active"
        self._attr_extra_state_attributes = {"name": "mynkow"}
