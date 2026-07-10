"""
Config flow schemas.

Schemas for the main configuration flow steps:
- User setup (host + credentials)
- Reconfiguration (credentials only)
- Reauthentication (credentials only)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers import selector


def get_zones_schema(zone_names: list[str]) -> vol.Schema:
    """
    Get schema for the zones configuration step.

    Args:
        zone_names: List of zone descriptions.

    Manually provide a dictionary where each key is the zone index (as string)
    and the value is the selected type.
    """
    schema_dict = {}
    for _index, name in enumerate(zone_names):
        # We include the name in the key so the user knows which zone they are configuring.
        # The format will be "index: name" (e.g., "0: Zone 1")
        key = f"{name}"
        schema_dict[key] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    BinarySensorDeviceClass.MOTION,
                    BinarySensorDeviceClass.DOOR,
                    BinarySensorDeviceClass.WINDOW,
                    BinarySensorDeviceClass.SMOKE,
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            ),
        )

    return vol.Schema(schema_dict)


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for user step (initial setup).

    Collects the controller IP/host and user credentials.

    Args:
        defaults: Optional dictionary of default values to pre-populate the form.

    Returns:
        Voluptuous schema for host + credentials input.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST,
                default=defaults.get(CONF_HOST, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_PORT,
                default=defaults.get(CONF_PORT, 80),
            ): vol.All(
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Coerce(int),
            ),
            vol.Required(
                CONF_USERNAME,
                default=defaults.get(CONF_USERNAME, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


def get_reconfigure_schema(username: str) -> vol.Schema:
    """
    Get schema for reconfigure step.

    Allows updating the credentials only (not the host).

    Args:
        username: Current username to pre-fill in the form.

    Returns:
        Voluptuous schema for reconfiguration.

    """
    return vol.Schema(
        {
            vol.Required(
                CONF_USERNAME,
                default=username,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_PASSWORD,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


def get_reauth_schema(username: str) -> vol.Schema:
    """
    Get schema for reauthentication step.

    Args:
        username: Current username to pre-fill in the form.

    Returns:
        Voluptuous schema for reauthentication.

    """
    return vol.Schema(
        {
            vol.Required(
                CONF_USERNAME,
                default=username,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_PASSWORD,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


__all__ = [
    "get_reauth_schema",
    "get_reconfigure_schema",
    "get_user_schema",
    "get_zones_schema",
]
