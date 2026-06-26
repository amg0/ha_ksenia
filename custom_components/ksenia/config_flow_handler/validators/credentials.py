"""
Credential validators.

Validation functions for user credentials and authentication against
the Ksenia Lares alarm panel.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.api import KseniaLaresApiClient
from homeassistant.helpers.aiohttp_client import async_create_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


import aiohttp
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

class CannotConnect(KseniaLaresApiClientCommunicationError):
    """Exception to indicate that the connection cannot be established."""

class InvalidAuth(KseniaLaresApiClientAuthenticationError):
    """Exception to indicate invalid credentials."""

async def validate_credentials(hass: HomeAssistant, host: str, username: str, password: str, port: int) -> None:
    """
    Validate user credentials by testing the connection to the Ksenia panel.

    Args:
        hass: Home Assistant instance.
        host: The IP address or hostname of the Ksenia controller.
        username: The username to validate.
        password: The password to validate.

    Raises:
        KseniaLaresApiClientAuthenticationError: If credentials are invalid.
        KseniaLaresApiClientCommunicationError: If communication fails.
        KseniaLaresApiClientError: For other API errors.

    """
    client = KseniaLaresApiClient(
        host=host,
        username=username,
        password=password,
        session=async_create_clientsession(hass),
    )
    await client.async_test_connection()


__all__ = [
    "validate_credentials",
]
