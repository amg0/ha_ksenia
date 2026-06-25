"""
Options flow for ksenia.

Allows users to modify the polling refresh period and the system PIN
after the initial configuration.

For more information:
https://developers.home-assistant.io/docs/config_entries_options_flow_handler
"""

from __future__ import annotations

from typing import Any

from custom_components.ksenia.config_flow_handler.schemas import get_options_schema
from homeassistant import config_entries


class KseniaLaresOptionsFlow(config_entries.OptionsFlow):
    """
    Handle options flow for the integration.

    Allows configuring:
    - refresh_period: Zone status polling interval (seconds)
    - pin: Encrypted system PIN for scenario execution (secret)

    For more information:
    https://developers.home-assistant.io/docs/config_entries_options_flow_handler
    """

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Manage the options for the integration.

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an options entry.

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry.options),
        )


__all__ = ["KseniaLaresOptionsFlow"]
