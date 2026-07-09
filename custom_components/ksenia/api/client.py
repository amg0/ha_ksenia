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
from enum import StrEnum
import socket
from typing import TypedDict
from xml.etree import ElementTree as ET

import aiohttp


class AlarmInfo(TypedDict):
    """Basic KSenia Lares alarm information."""

    # mac: str | None
    host: str
    name: str
    model: str
    info: str
    version: str
    revision: str
    build: str


class ZoneStatus(StrEnum):
    """Status of alarm zone."""

    UNKNOWN = "UNKNOWN"
    ALARM = "ALARM"
    NORMAL = "NORMAL"
    NOT_USED = "NOT_USED"


class ZoneBypass(StrEnum):
    """Bypass of alarm zone."""

    UNKNOWN = "UNKNOWN"
    OFF = "UN_BYPASS"
    ON = "BYPASS"


@dataclass
class ZoneDescription:
    """Alarm zone."""

    description: str

    @property
    def enabled(self):
        """Return whether the zone is enabled."""
        return self.description is not None and self.description != ""


@dataclass
class ZoneStatusDescription:
    """Alarm zone."""

    status: ZoneStatus
    bypass: ZoneBypass


@dataclass
class KseniaLaresZone:
    """Represents a single alarm zone with its description and status."""

    index: int
    description: str
    statusdescription: ZoneStatusDescription
    # status: ZoneStatus
    # bypass: ZoneBypass

    @property
    def is_triggered(self) -> bool:
        """Return True if the zone is in a non-NORMAL state (motion detected)."""
        return self.statusdescription.status != ZoneStatus.NORMAL

    @property
    def enabled(self):
        """Return whether the zone is enabled."""
        return self.description is not None


class PartitionStatus(StrEnum):
    """Status of alarm partition."""

    UNKNOWN = "UNKNOWN"
    DISARMED = "DISARMED"
    ARMED = "ARMED"
    ARMED_IMMEDIATE = "ARMED_IMMEDIATE"
    ARMING = "EXIT"
    PENDING = "PREALARM"
    ALARM = "ALARM"


@dataclass
class KseniaPartition:
    """Alarm partition."""

    id: int
    description: str
    status: PartitionStatus

    @property
    def enabled(self):
        """Return whether the partition is enabled."""
        return self.description is not None


@dataclass
class KseniaScenario:
    """Alarm scenario."""

    id: int
    description: str
    enabled: bool
    no_pin: bool


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

    id: int
    name: str
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
        self._alarminfo = None
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

    async def async_get_alarm_info(self) -> AlarmInfo:
        """
        Fetch basic alarm information from the Ksenia controller.

        Returns:
            A dictionary containing alarm info: mac, host, name, info, version, revision, build.
        """
        response = await self._api_wrapper(
            url=f"{self._base_url}/xml/info/generalInfo.xml",
        )
        general_info_el = ET.fromstring(response)  # noqa: S314
        product_name = general_info_el.findtext("productName", default="") or ""
        # mac = get_mac_address(ip=self._ip)
        info: AlarmInfo = {
            # "mac": mac,
            "host": self._base_url,
            "name": product_name,
            "model": product_name.split()[-1],
            "info": general_info_el.findtext("info1", default="") or "",
            "version": general_info_el.findtext("productHighRevision", default="") or "",
            "revision": general_info_el.findtext("productLowRevision", default="") or "",
            "build": general_info_el.findtext("productBuildRevision", default="") or "",
        }

        return info

    async def async_get_zone_descriptions(self) -> list[ZoneDescription]:
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
        self._alarminfo = await self.async_get_alarm_info()
        xml_text = await self._api_wrapper(
            url=f"{self._base_url}/xml/zones/zonesDescription16IP.xml",
        )
        root = ET.fromstring(xml_text)  # noqa: S314
        return [ZoneDescription(description=zone.text or "") for zone in root.findall("zone")]

    async def async_get_zone_statuses(self) -> list[ZoneStatusDescription]:
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
        root = ET.fromstring(xml_text)  # noqa: S314
        statuses: list[ZoneStatusDescription] = []
        for zone in root.findall("zone"):
            status_el = zone.find("status")
            bypass_el = zone.find("bypass")
            statuses.append(
                ZoneStatusDescription(
                    status=ZoneStatus(status_el.text or "UNKNOWN") if status_el is not None else ZoneStatus.UNKNOWN,
                    bypass=ZoneBypass(bypass_el.text or "UNKNOWN") if bypass_el is not None else ZoneBypass.UNKNOWN,
                )
            )
        return statuses

    async def async_set_zone_bypass(self, zone_id: int, pin: str | None, bypass: bool) -> str:
        """
        Set the bypass state of a specific zone.

        Args:
            zone_id: The ID of the zone to modify.
            pin: The PIN for authentication.
            bypass: True to enable bypass, False to disable.

        Returns:
            The raw XML response text.
        """
        bypass_value = 1 if bypass else 0
        url = f"{self._base_url}/xml/cmd/cmdOk.xml?cmd=setByPassZone&zoneId={zone_id}&zoneValue={bypass_value}&redirectPage=/xml/cmd/cmdError.xml"
        # http://192.168.0.41:125/xml/cmd/cmdOk.xml?cmd=setByPassZone&pin=150618&zoneId=12&zoneValue=0&redirectPage=/xml/cmd/cmdError.xml&_=1783460468295
        if pin:
            url += f"&pin={pin}"

        return await self._api_wrapper(url=url)

    async def async_get_partition_statuses(self) -> dict[str, KseniaPartition]:
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
        desc_root = ET.fromstring(desc_xml)  # noqa: S314
        # Assuming partition elements contain the name in their text, similar to zones
        descriptions = [p.text or "" for p in desc_root.findall("partition") if p.text]

        # 2. Fetch statuses
        stat_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/partitions/partitionsStatus16IP.xml",
        )
        stat_root = ET.fromstring(stat_xml)  # noqa: S314

        # 3. Combine results into a dictionary <name>:<status>
        statuses: dict[str, KseniaPartition] = {}
        for i, partition_el in enumerate(stat_root.findall("partition")):
            if i < len(descriptions):
                name = descriptions[i]
                statuses[name] = KseniaPartition(
                    id=i, description=name, status=PartitionStatus(partition_el.text or "UNKNOWN")
                )

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
        desc_root = ET.fromstring(desc_xml)  # noqa: S314
        descriptions = [s.text or "" for s in desc_root.findall("scenario")]

        opt_xml = await self._api_wrapper(
            url=f"{self._base_url}/xml/scenarios/scenariosOptions.xml",
        )
        opt_root = ET.fromstring(opt_xml)  # noqa: S314
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
        if pin is not None and pin != "":
            url += f"&pin={pin}"

        return await self._api_wrapper(url=url)

    async def async_test_connection(self) -> list[ZoneDescription]:
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
