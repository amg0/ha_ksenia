"""
Options flow schemas.

Schemas for the options flow that allows users to modify settings
after initial configuration:
- refresh_period: Polling interval in seconds
- pin: Encrypted system PIN (secret)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.ksenia.const import CONF_PIN, CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD
from homeassistant.helpers import selector


def get_options_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for options flow.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for options configuration.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_REFRESH_PERIOD,
                default=defaults.get(CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=300,
                    step=5,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional(
                CONF_PIN,
                default=defaults.get(CONF_PIN, ""),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


__all__ = [
    "get_options_schema",
]
