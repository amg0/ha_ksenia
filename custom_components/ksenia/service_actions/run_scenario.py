"""Run scenario service action handler for ksenia."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import CONF_PIN, DOMAIN, LOGGER
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_handle_run_scenario(
    hass: HomeAssistant,
    call: ServiceCall,
) -> None:
    """
    Handle the run_scenario service action call.

    Args:
        hass: Home Assistant instance
        call: Service call data

    Raises:
        HomeAssistantError: If entity resolution or scenario execution fails.
    """
    scenario_name = call.data.get("scenario_name")
    if not scenario_name:
        raise HomeAssistantError("Parameter scenario_name is required")

    entity_id_raw = call.data.get("entity_id")
    if not entity_id_raw:
        raise HomeAssistantError("Target entity (entity_id) is required")

    if isinstance(entity_id_raw, list):
        entity_id = entity_id_raw[0]
    else:
        entity_id = entity_id_raw

    # Resolve the entity to get its config entry
    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)
    if not entity_entry:
        raise HomeAssistantError(f"Entity {entity_id} not found in entity registry")

    if entity_entry.platform != DOMAIN:
        raise HomeAssistantError(f"Entity {entity_id} does not belong to domain {DOMAIN}")

    config_entry_id = entity_entry.config_entry_id
    if not config_entry_id:
        raise HomeAssistantError(f"No config entry found for entity {entity_id}")

    entry = hass.config_entries.async_get_entry(config_entry_id)
    if not entry:
        raise HomeAssistantError(f"Config entry {config_entry_id} not found")

    client = entry.runtime_data.client

    # Fetch scenarios to find the matching name
    try:
        scenarios = await client.async_get_scenarios()
    except Exception as exception:
        raise HomeAssistantError(f"Failed to fetch scenarios from Ksenia controller: {exception}") from exception

    target_scenario = None
    for scenario in scenarios:
        if scenario["name"] == scenario_name:
            target_scenario = scenario
            break

    if not target_scenario:
        # Fallback to case-insensitive match
        for scenario in scenarios:
            if str(scenario["name"]).lower() == str(scenario_name).lower():
                target_scenario = scenario
                break

    if not target_scenario:
        raise HomeAssistantError(f"Scenario '{scenario_name}' not found on Ksenia controller")

    scenario_id = target_scenario["id"]
    nopin = target_scenario.get("nopin", True)
    pin = entry.options.get(CONF_PIN)

    if not nopin and not pin:
        raise HomeAssistantError(f"Scenario '{scenario_name}' requires a PIN, but no PIN is configured in options")

    LOGGER.info("Executing scenario '%s' (ID: %s)", scenario_name, scenario_id)

    try:
        await client.async_run_scenario(scenario_id=scenario_id, pin=pin if not nopin else None)
    except Exception as exception:
        raise HomeAssistantError(f"Failed to execute scenario '{scenario_name}': {exception}") from exception

    LOGGER.info("Scenario '%s' executed successfully", scenario_name)
