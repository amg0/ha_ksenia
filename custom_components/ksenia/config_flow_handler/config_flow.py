"""
Config flow for ksenia.

This module implements the main configuration flow including:
- Initial user setup (host + credentials)
- Reconfiguration of credentials
- Reauthentication flow

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.ksenia.config_flow_handler.schemas import (
    get_reauth_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.ksenia.config_flow_handler.schemas.options import get_options_schema
from custom_components.ksenia.config_flow_handler.validators import validate_credentials
from custom_components.ksenia.const import DOMAIN, LOGGER
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.loader import async_get_loaded_integration

if TYPE_CHECKING:
    from custom_components.ksenia.config_flow_handler.options_flow import KseniaLaresOptionsFlow

# Map exception types to error keys for user-facing messages
ERROR_MAP = {
    "KseniaLaresApiClientAuthenticationError": "auth",
    "KseniaLaresApiClientCommunicationError": "connection",
}


class KseniaLaresConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for ksenia.

    This class manages the configuration flow for the integration, including
    initial setup, reconfiguration, and reauthentication.

    Supported flows:
    - user: Initial setup via UI (host + username + password)
    - reconfigure: Update credentials (username + password only)
    - reauth: Handle expired credentials
    - options_setup: Set initial options after credential validation

    For more details:
    https://developers.home-assistant.io/docs/config_entries_config_flow_handler
    """

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> KseniaLaresOptionsFlow:
        """
        Get the options flow for this handler.

        Returns:
            The options flow instance for modifying integration options.

        """
        from custom_components.ksenia.config_flow_handler.options_flow import KseniaLaresOptionsFlow  # noqa: PLC0415

        return KseniaLaresOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle a flow initialized by the user.

        Collects host IP, username, and password. Validates connectivity
        before transitioning to the options setup step. Uses the host as the unique ID.

        Args:
            user_input: The user input from the config flow form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an entry.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_PORT],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_authentication_error(exception)
            else:
                # Use the host IP as unique ID so each panel can only be added once
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                # Store credentials temporarily for the next step in the flow
                self._temp_data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    "port": user_input[CONF_PORT],
                }

                return self.async_show_form(
                    step_id="init_option",
                    data_schema=get_options_schema(),
                )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, "Integration documentation URL is not set in manifest.json"

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={
                "documentation_url": integration.documentation,
            },
        )

    async def async_step_init_option(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the final step of the configuration flow to set initial options before creating the entry."""
        if user_input is not None:
            base_data = getattr(self, "_temp_data", {})
            return self.async_create_entry(
                title=f"Ksenia Lares ({base_data.get(CONF_HOST)})",
                data=base_data,
                options=user_input,
            )

        return self.async_show_form(
            step_id="init_option",
            data_schema=get_options_schema(),
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reconfiguration of the integration.

        Allows users to update their credentials without removing and re-adding
        the integration. The host cannot be can be changed here; use delete + re-add.

        Args:
            user_input: The user input from the reconfigure form, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    host=entry.data[CONF_HOST],
                    port=entry.data["port"],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_authentication_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(entry.data.get(CONF_USERNAME, "")),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reauthentication when credentials are invalid.

        This flow is automatically triggered when the coordinator catches
        an authentication error (ConfigEntryAuthFailed).

        Args:
            entry_data: The existing entry data (unused, per convention).

        Returns:
            The result of the reauth_confirm step.

        """
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reauthentication confirmation.

        Shows the reauthentication form and processes updated credentials.
        The existing host is preserved.

        Args:
            user_input: The user input with updated credentials, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_credentials(
                    self.hass,
                    host=entry.data[CONF_HOST],
                    port=entry.data[CONF_PORT],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_authentication_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=get_reauth_schema(entry.data.get(CONF_USERNAME, "")),
            errors=errors,
            description_placeholders={
                "username": entry.data.get(CONF_USERNAME, ""),
            },
        )

    def _map_authentication_error(self, exception: Exception) -> str:
        """
        Map API exceptions to user-facing error keys.

        Args:
            exception: The exception that was raised.

        Returns:
            The error key for display in the config flow form.

        """
        LOGGER.warning("Error in config flow: %s", exception)
        exception_name = type(exception).__name__
        return ERROR_MAP.get(exception_name, "unknown")


__all__ = ["KseniaLaresConfigFlowHandler"]
