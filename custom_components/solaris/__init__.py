"""The Solaris integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady

from .ibex_coordinator import IbexCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solaris from a config entry."""
    hass.data.setdefault("solaris", {})

    # Initialize the coordinator
    coordinator = IbexCoordinator(hass)
    hass.data["solaris"][entry.entry_id] = coordinator

    # Perform the first refresh to load data
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to initialize coordinator: {err}") from err

    # Forward entry setups to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data["solaris"].pop(entry.entry_id)
    return unload_ok