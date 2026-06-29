"""Service actions package for ksenia."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import DOMAIN, LOGGER
from custom_components.ksenia.service_actions.example_service import (
    async_handle_example_action,
    async_handle_reload_data,
)
from custom_components.ksenia.service_actions.run_scenario import async_handle_run_scenario
from homeassistant.core import ServiceCall

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

# Service action names - only used within service_actions module
SERVICE_EXAMPLE_ACTION = "example_action"
SERVICE_RELOAD_DATA = "reload_data"
SERVICE_RUN_SCENARIO = "run_scenario"


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

    async def handle_example_action(call: ServiceCall) -> None:
        """Handle the example_action service call."""
        # Find all config entries for this domain
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            LOGGER.warning("No config entries found for %s", DOMAIN)
            return

        # Use first entry (or implement logic to select specific entry)
        entry = entries[0]
        await async_handle_example_action(hass, entry, call)

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

    # Register services (only once at component level)
    if not hass.services.has_service(DOMAIN, SERVICE_EXAMPLE_ACTION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXAMPLE_ACTION,
            handle_example_action,
        )

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

    LOGGER.debug("Services registered for %s", DOMAIN)
