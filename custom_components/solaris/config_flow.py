"""Config flow for Solaris integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)


class SolarisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solaris."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        if user_input is not None:
            # Compose the unique_id from client_id and client_location
            unique_id = f"{user_input['client_id']}::{user_input['client_location']}"
            await self.async_set_unique_id(unique_id)

            # Abort if an entry with this unique_id already exists
            self._abort_if_unique_id_configured()

            # Use a friendly title like "Client A - Roof" if needed
            title = f"{user_input['client_id']} - {user_input['client_location']}"
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_location"): str,
                    vol.Required(
                        "produced_energy_entity",
                        description={"suggested_value": None},
                    ): selector(
                        {"entity": {"domain": "sensor", "device_class": "energy"}}
                    ),
                    vol.Required(
                        "energy_price_entity",
                        description={"suggested_value": None},
                    ): selector(
                        {"entity": {"domain": "sensor", "device_class": "monetary"}}
                    ),
                }
            ),
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data={
                    "produced_energy_entity": user_input.get("produced_energy_entity"),
                },
            )

        # Retrieve the current configuration values
        current_config = self._get_reconfigure_entry().data

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "produced_energy_entity",
                        default=current_config.get("produced_energy_entity"),
                    ): selector(
                        {"entity": {"domain": "sensor"}}
                    ),  # Allow selecting a sensor entity
                }
            ),
        )

    def _get_reconfigure_entry(self) -> config_entries.ConfigEntry:
        """Get the current config entry being reconfigured."""
        return self.hass.config_entries.async_get_entry(self.context["entry_id"])


class SolarisOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Solaris options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "produced_energy_entity",
                        default=self.config_entry.options.get("produced_energy_entity"),
                    ): selector(
                        {"entity": {"domain": "sensor"}}
                    ),  # Allow selecting a sensor entity
                }
            ),
        )
