"""
Config flow schemas.

Schemas for the main configuration flow steps:
- User setup (host + credentials)
- Reconfiguration (credentials only)
- Reauthentication (credentials only)
"""

from collections.abc import Mapping
from typing import Any

import probatio

from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers import selector


def get_zones_schema(zone_names: list[str]) -> probatio.Schema:
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

    return probatio.Schema(schema_dict)


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> probatio.Schema:
    """
    Get schema for user step (initial setup).

    Collects the controller IP/host and user credentials.

    Args:
        defaults: Optional dictionary of default values to pre-populate the form.

    Returns:
        Probatio schema for host + credentials input.

    """
    defaults = defaults or {}
    return probatio.Schema(
        {
            probatio.Required(
                CONF_HOST,
                default=defaults.get(CONF_HOST, probatio.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            probatio.Required(
                CONF_PORT,
                default=defaults.get(CONF_PORT, 80),
            ): probatio.All(
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                probatio.Coerce(int),
            ),
            probatio.Required(
                CONF_USERNAME,
                default=defaults.get(CONF_USERNAME, probatio.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            probatio.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


def get_reconfigure_schema(username: str) -> probatio.Schema:
    """
    Get schema for reconfigure step.

    Allows updating the credentials only (not the host).

    Args:
        username: Current username to pre-fill in the form.

    Returns:
        Probatio schema for reconfiguration.

    """
    return probatio.Schema(
        {
            probatio.Required(
                CONF_USERNAME,
                default=username,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            probatio.Required(
                CONF_PASSWORD,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
        },
    )


def get_reauth_schema(username: str) -> probatio.Schema:
    """
    Get schema for reauthentication step.

    Args:
        username: Current username to pre-fill in the form.

    Returns:
        Probatio schema for reauthentication.

    """
    return probatio.Schema(
        {
            probatio.Required(
                CONF_USERNAME,
                default=username,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            probatio.Required(
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
