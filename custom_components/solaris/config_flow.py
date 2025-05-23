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

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Solaris", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_url", default="http://10.1.1.85:9200/metrics-ibex/_search"): str,
                vol.Required("username", default="elastic"): str,
                vol.Required("password", default="123qwe123qwe##asd"): str,
                vol.Optional(
                    "produced_energy_entity",
                    description={"suggested_value": None},
                ): selector({"entity": {"domain": "sensor"}}),  # Allow selecting a sensor entity
            }),
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data={
                    "api_url": user_input["api_url"],
                    "username": user_input["username"],
                    "password": user_input["password"],
                    "produced_energy_entity": user_input.get("produced_energy_entity"),
                },
            )

        # Retrieve the current configuration values
        current_config = self._get_reconfigure_entry().data

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required("api_url", default=current_config.get("api_url", "")): str,
                vol.Required("username", default=current_config.get("username", "")): str,
                vol.Required("password", default=current_config.get("password", "")): str,
                vol.Optional(
                    "produced_energy_entity",
                    default=current_config.get("produced_energy_entity"),
                ): selector({"entity": {"domain": "sensor"}}),  # Allow selecting a sensor entity
        }),
        )

    def _get_reconfigure_entry(self) -> config_entries.ConfigEntry:
        """Get the current config entry being reconfigured."""
        return self.hass.config_entries.async_get_entry(self.context["entry_id"])


class SolarisOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Solaris options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "produced_energy_entity",
                    default=self.config_entry.options.get("produced_energy_entity"),
                ): selector({"entity": {"domain": "sensor"}}),  # Allow selecting a sensor entity
            }),
        )