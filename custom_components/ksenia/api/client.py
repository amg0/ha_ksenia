"""
API Client for ksenia.

Communicates with the Ksenia Lares alarm panel via HTTP GET requests
using HTTP Basic Authentication. All responses are XML.

For more information on creating API clients:
https://developers.home-assistant.io/docs/api_lib_index
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket

import aiohttp
from defusedxml import ElementTree


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


@dataclass(slots=True)
class KSeniaLaresScenario:
    """Représentation d'un scénario Ksenia Lares."""

    name: str
    id: int
    nopin: bool


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
      - /xml/partitions/partitionsDescription16IP.xml (fetched to get names)
      - /xml/partitions/partitionsStatus16IP.xml     (polled regularly)

    Attributes:
        _host: IP address or hostname of the Ksenia controller.
        _username: Username for HTTP Basic Auth.
        _password: Password for HTTP Basic Auth.
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
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

    async def async_get_partition_statuses(self) -> dict[str, str]:
        """
        Fetch current partition statuses from the Ksenia controller.

        Calls both description and status endpoints to return a mapping
        of partition names to their current status.

        Returns:
            A dictionary with partition name as key and status as value.

        Raises:
            KseniaLaresApiClientAuthenticationError: If authentication fails.
            KseniaLaresApiClientCommunicationError: If communication fails.
            KseniaLaresApiClientError: For other API errors.

        """
        # 1. Fetch descriptions to get names
        desc_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/partitions/partitionsDescription16IP.xml",
        )
        desc_root = ElementTree.fromstring(desc_xml)
        # Assuming partition elements contain the name in their text, similar to zones
        descriptions = [p.text or "" for p in desc_root.findall("partition") if p.text]

        # 2. Fetch statuses
        stat_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/partitions/partitionsStatus16IP.xml",
        )
        stat_root = ElementTree.fromstring(stat_xml)

        # 3. Combine results into a dictionary <name>:<status>
        statuses: dict[str, str] = {}
        for i, partition_el in enumerate(stat_root.findall("partition")):
            if i < len(descriptions):
                name = descriptions[i]
                statuses[name] = partition_el.text or "UNKNOWN"

        return statuses

    async def async_get_scenarios(self) -> list[KSeniaLaresScenario]:
        """
        Fetch available scenarios from the Ksenia controller.

        Retrieves descriptions and options, filtering to only keep scenarios where
        <abil> is TRUE.

        Returns:
            A list of dictionaries representing enabled scenarios, each containing
            'id', 'name', and 'nopin' boolean.

        Raises:
            KseniaLaresApiClientAuthenticationError: If credentials are invalid.
            KseniaLaresApiClientCommunicationError: If the host is unreachable.
            KseniaLaresApiClientError: For other API errors.

        """
        desc_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/scenarios/scenariosDescription.xml",
        )
        desc_root = ElementTree.fromstring(desc_xml)
        descriptions = [s.text or "" for s in desc_root.findall("scenario")]

        opt_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/scenarios/scenariosOptions.xml",
        )
        opt_root = ElementTree.fromstring(opt_xml)
        options = opt_root.findall("scenario")

        scenarios: list[KSeniaLaresScenario] = []
        for idx, name in enumerate(descriptions):
            if idx >= len(options):
                break
            opt = options[idx]
            abil_el = opt.find("abil")
            nopin_el = opt.find("nopin")

            abil = (abil_el.text or "").strip().upper() if abil_el is not None else ""
            nopin = (nopin_el.text or "").strip().upper() if nopin_el is not None else ""

            if abil == "TRUE":
                scenarios.append(KSeniaLaresScenario(name=name, id=idx, nopin=nopin == "TRUE"))

        return scenarios

    async def async_run_scenario(self, scenario_id: int | str, pin: str | None = None) -> str:
        """
        Run a given scenario (macro) with an optional PIN code.

        Args:
            scenario_id: The ID of the scenario to execute.
            pin: Optional system PIN code required to execute the scenario.

        Returns:
            The raw XML response text.

        Raises:
            KseniaLaresApiClientAuthenticationError: If credentials are invalid.
            KseniaLaresApiClientCommunicationError: If the host is unreachable.
            KseniaLaresApiClientError: For other API errors.

        """
        url = (
            f"{self._base_url}/xml/cmd/cmdOk.xml?cmd=setMacro&macroId={scenario_id}&redirectPage=/xml/cmd/cmdError.xml"
        )
        if pin is not None:
            url += f"&pin={pin}"

        return await self._api_wrapper(url=url)

    async def async_test_connection(self) -> list[str]:
        """
        Test the connection by fetching zone descriptions.

        Used during config flow validation.

        Raises:
            KseniaLaresApiClientAuthenticationError: If credentials are invalid.
            KseniaLaresApiClientCommunicationError: If the host is unreachable.
            KseniaLaresApiClientError: For other API errors.

        """
        return await self.async_get_zone_descriptions()

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
