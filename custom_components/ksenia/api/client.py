"""
API Client for ksenia.

Communicates with the Ksenia Lares alarm panel via HTTP GET requests
using HTTP Basic Authentication. All responses are XML.

For more information on creating API clients:
https://developers.home-assistant.io/docs/api_lib_index
"""

from __future__ import annotations

import asyncio
import socket

import aiohttp
from defusedxml import ElementTree

from homeassistant.const import CONF_PORT

class KseniaLaresApiClientError(Exception):
    """Base exception to indicate a general API error."""


class KseniaLaresApiClientCommunicationError(
    KseniaLaresApiClientError,
):
    """Exception to indicate a communication error with the API."""


class KseniaLaresApiClientAuthenticationError(
    KseniaLaresApiClientError,
):
    """Exception to indicate an authentication error with the API."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """
    Verify that the API response is valid.

    Raises appropriate exceptions for authentication and HTTP errors.

    Args:
        response: The aiohttp ClientResponse to verify.

    Raises:
        KseniaLaresApiClientAuthenticationError: For 401/403 errors.
        aiohttp.ClientResponseError: For other HTTP errors.

    """
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise KseniaLaresApiClientAuthenticationError(msg)
    response.raise_for_status()


class KseniaLaresApiClient:
    """
    API Client for the Ksenia Lares alarm panel.

    Communicates with the Ksenia controller over the local network
    using HTTP Basic Authentication. All responses are parsed as XML.

    Endpoints used:
      - /xml/zones/zonesDescription16IP.xml  (fetched once at init)
      - /xml/zones/zonesStatus16IP.xml       (polled regularly)

    Attributes:
        _host: IP address or hostname of the Ksenia controller.
        _username: Username for HTTP Basic Auth.
        _password: Password for HTTP Basic Auth.
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        port: int,
    ) -> None:
        """
        Initialize the API Client with connection details.

        Args:
            host: The IP address or hostname of the Ksenia controller.
            username: The username for HTTP Basic Authentication.
            password: The password for HTTP Basic Authentication.
            session: The aiohttp ClientSession to use for requests.

        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._session = session

    @property
    def _base_url(self) -> str:
        """Return the base URL for API requests."""
        return f"http://{self._host}:{self._port}"

    def _auth(self) -> aiohttp.BasicAuth:
        """Return the BasicAuth object for requests."""
        return aiohttp.BasicAuth(self._username, self._password)

    async def async_get_zone_descriptions(self) -> list[str]:
        """
        Fetch zone descriptions from the Ksenia controller.

        Called once during coordinator setup to discover zone names.
        Returns a list of zone name strings in index order.

        Returns:
            List of zone description strings.

        Raises:
            KseniaLaresApiClientAuthenticationError: If authentication fails.
            KseniaLaresApiClientCommunicationError: If communication fails.
            KseniaLaresApiClientError: For other API errors.

        """
        xml_text = await self._api_wrapper(
            url=f"{self._base_url}/xml/zones/zonesDescription16IP.xml",
        )
        root = ElementTree.fromstring(xml_text)
        return [zone.text or "" for zone in root.findall("zone")]

    async def async_get_zone_statuses(self) -> list[dict[str, str]]:
        """
        Fetch current zone statuses from the Ksenia controller.

        Called on every polling interval. Returns a list of dicts,
        one per zone, with 'status' and 'bypass' keys.

        Returns:
            List of zone status dicts with keys 'status' and 'bypass'.

        Raises:
            KseniaLaresApiClientAuthenticationError: If authentication fails.
            KseniaLaresApiClientCommunicationError: If communication fails.
            KseniaLaresApiClientError: For other API errors.

        """
        xml_text = await self._api_wrapper(
            url=f"{self._base_url}/xml/zones/zonesStatus16IP.xml",
        )
        root = ElementTree.fromstring(xml_text)
        statuses: list[dict[str, str]] = []
        for zone in root.findall("zone"):
            status_el = zone.find("status")
            bypass_el = zone.find("bypass")
            statuses.append(
                {
                    "status": status_el.text or "UNKNOWN" if status_el is not None else "UNKNOWN",
                    "bypass": bypass_el.text or "UNKNOWN" if bypass_el is not None else "UNKNOWN",
                }
            )
        return statuses

    async def async_test_connection(self) -> None:
        """
        Test the connection by fetching zone descriptions.

        Used during config flow validation.

        Raises:
            KseniaLaresApiClientAuthenticationError: If credentials are invalid.
            KseniaLaresApiClientCommunicationError: If the host is unreachable.
            KseniaLaresApiClientError: For other API errors.

        """
        await self.async_get_zone_descriptions()

    async def _api_wrapper(self, url: str) -> str:
        """
        Wrapper for GET requests with error handling.

        Args:
            url: The URL to request.

        Returns:
            The raw response text (XML).

        Raises:
            KseniaLaresApiClientAuthenticationError: If authentication fails.
            KseniaLaresApiClientCommunicationError: If communication fails.
            KseniaLaresApiClientError: For other API errors.

        """
        try:
            async with asyncio.timeout(10):
                response = await self._session.get(
                    url=url,
                    auth=self._auth(),
                )
                _verify_response_or_raise(response)
                return await response.text()

        except KseniaLaresApiClientError:
            raise
        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise KseniaLaresApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise KseniaLaresApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Something really wrong happened! - {exception}"
            raise KseniaLaresApiClientError(msg) from exception
