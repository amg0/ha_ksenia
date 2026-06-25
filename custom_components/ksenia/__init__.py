"""
Custom integration to integrate ksenia with Home Assistant.

Connects to the Ksenia Lares alarm panel over the local network,
fetching zone data to expose motion detection sensors.

For more details about this integration, please refer to:
https://github.com/amg0/ha_ksenia

For integration development guidelines:
https://developers.home-assistant.io/docs/creating_integration_manifest
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .api import KseniaLaresApiClient
from .const import CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD, DOMAIN, LOGGER
from .coordinator import KseniaLaresDataUpdateCoordinator
from .data import KseniaLaresData
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import KseniaLaresConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
]

# This integration is configured via config entries only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Set up the integration.

    Registers service actions at startup. Services must be registered here
    (not in async_setup_entry) to satisfy the Silver Quality Scale requirement.

    Args:
        hass: The Home Assistant instance.
        config: The Home Assistant configuration.

    Returns:
        True if setup was successful.

    """
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> bool:
    """
    Set up this integration using UI.

    Creates the API client using the host + credentials from the config entry,
    then initialises the coordinator with the configured refresh period from
    options (defaulting to DEFAULT_REFRESH_PERIOD seconds).

    Data flow:
      1. User enters host/username/password in config flow
      2. Credentials stored in entry.data
      3. API Client initialised with host + credentials
      4. Coordinator fetches zone descriptions (once) then polls zone statuses
      5. Binary sensor entities read zone data from coordinator.data

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.

    Returns:
        True if setup was successful.

    """
    refresh_period = entry.options.get(CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD)

    client = KseniaLaresApiClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    coordinator = KseniaLaresDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(seconds=refresh_period),
    )

    entry.runtime_data = KseniaLaresData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # Performs zone description fetch (_async_setup) then first zone status poll
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being unloaded.

    Returns:
        True if unload was successful.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> None:
    """
    Reload config entry when options change.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being reloaded.

    """
    await hass.config_entries.async_reload(entry.entry_id)
