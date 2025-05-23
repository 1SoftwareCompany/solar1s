"""Platform for Solaris sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.energy_price_sensor import EnergyPriceSensor
from .sensors.price_hour_sensor import PriceHourSensor
from .sensors.ibex_prices_last_updated_sensor import IbexPricesLastUpdatedSensor
from .sensors.current_price_sensor import CurrentPriceSensor, CurrentPriceSensorKWH
from .sensors.sold_energy_sensor import SoldEnergySensor
from .ibex_coordinator import IbexCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    # Retrieve the coordinator from hass.data
    coordinator: IbexCoordinator = hass.data["solaris"][entry.entry_id]

    # Retrieve configured sensor names from the config entry
    energy_price_sensor = entry.data.get("energy_price_sensor", "sensor.solar1s_all_prices")
    produced_energy_entity = entry.data.get("produced_energy_entity", "sensor.produced_energy")

    # Add sensors
    price_sensors = [PriceHourSensor(coordinator, i) for i in range(48)]
    async_add_entities(
        price_sensors
        + [
            EnergyPriceSensor(coordinator),
            IbexPricesLastUpdatedSensor(coordinator),
            CurrentPriceSensor(hass),
            CurrentPriceSensorKWH(hass),
            SoldEnergySensor(coordinator, energy_price_sensor, produced_energy_entity),
        ]
    )
