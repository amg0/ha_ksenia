"""Service actions package for ksenia."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import DOMAIN, LOGGER
from custom_components.ksenia.service_actions.example_service import async_handle_reload_data
from custom_components.ksenia.service_actions.run_scenario import async_handle_run_scenario
from custom_components.ksenia.service_actions.zone_bypass import async_handle_zone_bypass
from homeassistant.core import ServiceCall

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

# Service action names - only used within service_actions module
SERVICE_EXAMPLE_ACTION = "example_action"
SERVICE_RELOAD_DATA = "reload_data"
SERVICE_RUN_SCENARIO = "run_scenario"
SERVICE_ZONE_BYPASS = "zone_bypass"


async def async_setup_services(hass: HomeAssistant) -> None:
    """
    Register services for the integration.

    Services are registered at component level (in async_setup) rather than
    per config entry. This is a Silver Quality Scale requirement and ensures:
    - Service validation works correctly
    - Services are available even without config entries
    - Helpful error messages are provided

    Service handlers iterate over all config entries to find the relevant one.
    """

    async def handle_reload_data(call: ServiceCall) -> None:
        """Handle the reload_data service call."""
        # Find all config entries for this domain
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            LOGGER.warning("No config entries found for %s", DOMAIN)
            return

        # Reload data for all entries
        for entry in entries:
            await async_handle_reload_data(hass, entry, call)

    async def handle_run_scenario(call: ServiceCall) -> None:
        """Handle the run_scenario service call."""
        await async_handle_run_scenario(hass, call)

    async def handle_zone_bypass(call: ServiceCall) -> None:
        """Handle the zone_bypass service call."""
        # Find all config entries for this domain
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            LOGGER.warning("No config entries found for %s", DOMAIN)
            return

        # for each entry, handle the zone bypass service call
        for entry in entries:
            await async_handle_zone_bypass(hass, entry, call)

    # Register services (only once at component level)
    if not hass.services.has_service(DOMAIN, SERVICE_RELOAD_DATA):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RELOAD_DATA,
            handle_reload_data,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RUN_SCENARIO):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RUN_SCENARIO,
            handle_run_scenario,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_ZONE_BYPASS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ZONE_BYPASS,
            handle_zone_bypass,
        )

    LOGGER.debug("Services registered for %s", DOMAIN)
