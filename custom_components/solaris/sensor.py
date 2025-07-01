"""Platform for Solaris sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.earnings_sensor import EarningsSensor
from .sensors.hourly_earnings_sensor import HourlyEarningsSensor


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    # Retrieve configured sensor names from the config entry
    unique_id = entry.unique_id
    client_id = entry.data.get("client_id")
    client_location = entry.data.get("client_location")
    energy_price_entity = entry.data.get("energy_price_entity")
    produced_energy_entity = entry.data.get("produced_energy_entity")

    # Add sensors
    price_sensors = [
        PVHourlyEarningsSensor(
            hass,
            unique_id,
            client_id,
            client_location,
            produced_energy_entity,
            energy_price_entity,
        )
    ]
    async_add_entities(price_sensors)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    unique_id = entry.unique_id
    client_id = entry.data.get("client_id")
    client_location = entry.data.get("client_location")
    energy_price_entity = entry.data.get("energy_price_entity")
    produced_energy_entity = entry.data.get("produced_energy_entity")

    # Create a uniquely identified sensor
    earnings = EarningsSensor(
        unique_id=unique_id,
        client_id=client_id,
        client_location=client_location,
        energy_price_entity=energy_price_entity,
        produced_energy_entity=produced_energy_entity,
    )

    hourly = HourlyEarningsSensor(
        hass,
        unique_id,
        client_id,
        client_location,
        produced_energy_entity,
        energy_price_entity,
    )

    async_add_entities([hourly])
