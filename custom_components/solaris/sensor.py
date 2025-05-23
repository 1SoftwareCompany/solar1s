"""Platform for Solaris sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.price_hour_sensor import PriceHourSensor
from .sensors.ibex_prices_last_updated_sensor import IbexPricesLastUpdatedSensor
from .sensors.current_price_sensor import CurrentPriceSensor, CurrentPriceSensorKWH
from .sensors.sold_energy_sensor import SoldEnergySensor
from .ibex_coordinator import IbexCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    coordinator = IbexCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    # Add sensors
    price_sensors = [PriceHourSensor(coordinator, i) for i in range(48)]
    async_add_entities(
        price_sensors
        + [
            IbexPricesLastUpdatedSensor(coordinator),
            CurrentPriceSensor(hass),
            CurrentPriceSensorKWH(hass),
            SoldEnergySensor(coordinator, "sensor.energy_price_now", "sensor.produced_energy"),
        ]
    )
