"""Number platform for Solaris."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .sensors.price_threshold import PriceThresholdEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    unique_id = entry.unique_id
    client_id = entry.data.get("client_id")
    client_location = entry.data.get("client_location")

    priceThreshold = PriceThresholdEntity(
        unique_id=unique_id, client_id=client_id, client_location=client_location
    )

    async_add_entities([priceThreshold])
