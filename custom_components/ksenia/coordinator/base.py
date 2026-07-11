"""
Core DataUpdateCoordinator implementation for ksenia.

The coordinator fetches zone descriptions once during _async_setup()
(which runs before the first data refresh) and then only polls
zone statuses on each subsequent update.

For more information on coordinators:
https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from custom_components.ksenia.api import KseniaLaresApiClientAuthenticationError, KseniaLaresApiClientError
from custom_components.ksenia.api.client import (
    KSeniaLaresScenario,
    KseniaPartition,
    ZoneBypass,
    ZoneDescription,
    ZoneStatus,
    ZoneStatusDescription,
)
from custom_components.ksenia.const import LOGGER
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .coordinator_data import KseniaLaresCoordinatorData, KseniaLaresZone

if TYPE_CHECKING:
    from custom_components.ksenia.data import KseniaLaresConfigEntry


class KseniaLaresDataUpdateCoordinator(DataUpdateCoordinator[KseniaLaresCoordinatorData]):
    """
    Class to manage fetching data from the Ksenia Lares alarm panel.

    Two-phase data fetching:
      1. _async_setup(): Fetches zone descriptions once to discover all zones.
      2. _async_update_data(): Polls zone statuses on each refresh interval.

    For more information:
    https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities

    Attributes:
        config_entry: The config entry for this integration instance.
    """

    config_entry: KseniaLaresConfigEntry

    def __init__(
        self,
        hass,
        logger,
        name: str,
        config_entry: KseniaLaresConfigEntry,
        update_interval: timedelta,
    ) -> None:
        """
        Initialize the coordinator.

        Args:
            hass: The Home Assistant instance.
            logger: Logger to use for debug/warning messages.
            name: Name for this coordinator.
            config_entry: The config entry being coordinated.
            update_interval: How often to refresh zone statuses.

        """
        super().__init__(
            hass=hass,
            logger=logger,
            name=name,
            config_entry=config_entry,
            update_interval=update_interval,
            always_update=False,
        )
        # Zone descriptions, populated during _async_setup
        self._zone_descriptions: list[ZoneDescription] = []
        self._partitions_data: dict[str, KseniaPartition] = {}
        self._scenarios: list[KSeniaLaresScenario] = []

    async def _async_setup(self) -> None:
        """
        Fetch zone descriptions once at coordinator startup.

        This runs automatically during async_config_entry_first_refresh(),
        before the first data fetch. It discovers all configured zones
        by their descriptions so entities can be created with proper names.

        Raises:
            ConfigEntryAuthFailed: If authentication fails.
            UpdateFailed: If zone descriptions cannot be fetched.

        """
        client = self.config_entry.runtime_data.client
        try:
            self._zone_descriptions = await client.async_get_zone_descriptions()
            self._partitions_data = await client.async_get_partition_statuses()
            self._scenarios = await client.async_get_scenarios()
            LOGGER.debug(
                "Fetched %d zone descriptions, %d partitions , %d scenarios for %s",
                len(self._zone_descriptions),
                len(self._partitions_data),
                len(self._scenarios),
                self.config_entry.entry_id,
            )
        except KseniaLaresApiClientAuthenticationError as exception:
            LOGGER.warning("Authentication error during setup - %s", exception)
            raise ConfigEntryAuthFailed(
                translation_domain="ksenia",
                translation_key="authentication_failed",
            ) from exception
        except KseniaLaresApiClientError as exception:
            LOGGER.exception("Error during setup")
            raise UpdateFailed(
                translation_domain="ksenia",
                translation_key="update_failed",
            ) from exception

    @property
    def zone_descriptions(self) -> list[ZoneDescription]:
        """Return the list of zone descriptions fetched at setup."""
        return self._zone_descriptions

    @property
    def partitions(self) -> dict[str, KseniaPartition]:
        """Return the partition statuses property."""
        return self._partitions_data

    @property
    def scenarios(self) -> list[KSeniaLaresScenario]:
        """Return the scenarios."""
        return self._scenarios

    async def _async_update_data(self) -> KseniaLaresCoordinatorData:
        """
        Poll zone and partition statuses from the Ksenia Lares panel.

        Called automatically on each update_interval tick. Updates the
        status and bypass state for every zone. Zone descriptions remain
        unchanged from the initial setup fetch.

        Returns:
            KseniaLaresCoordinatorData containing updated zone list and partition statuses.

        Raises:
            ConfigEntryAuthFailed: If authentication fails (triggers reauth).
            UpdateFailed: If status polling fails (auto-retry).

        """
        client = self.config_entry.runtime_data.client
        try:
            statuses = await client.async_get_zone_statuses()
            self._partitions_data = await client.async_get_partition_statuses()
            logs = await client.async_get_logs()
        except KseniaLaresApiClientAuthenticationError as exception:
            LOGGER.warning("Authentication error during status update - %s", exception)
            raise ConfigEntryAuthFailed(
                translation_domain="ksenia",
                translation_key="authentication_failed",
            ) from exception
        except KseniaLaresApiClientError as exception:
            LOGGER.exception("Error communicating with API during status update")
            raise UpdateFailed(
                translation_domain="ksenia",
                translation_key="update_failed",
            ) from exception

        zones: list[KseniaLaresZone] = []
        for idx, zonedescription in enumerate(self._zone_descriptions):
            if idx < len(statuses):
                zone_status = statuses[idx]
                zones.append(
                    KseniaLaresZone(
                        index=idx,
                        description=zonedescription.description,
                        statusdescription=ZoneStatusDescription(
                            status=ZoneStatus(zone_status.status), bypass=ZoneBypass(zone_status.bypass)
                        ),
                    )
                )
            # else:
            #     zones.append(
            #         KseniaLaresZone()
            #     )

        return KseniaLaresCoordinatorData(
            zones=zones, partitions=self._partitions_data, alarminfo=client.alarm_info, logs=logs
        )
