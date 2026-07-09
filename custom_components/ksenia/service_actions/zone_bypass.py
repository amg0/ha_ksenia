"""Zone Bypass service action handler for ksenia."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.api.client import ZoneBypass
from custom_components.ksenia.const import CONF_PIN, LOGGER
from custom_components.ksenia.data import KseniaLaresConfigEntry
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_handle_zone_bypass(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
    call: ServiceCall,
) -> None:
    """Handle the zone_bypass service action."""

    entity_id = call.data.get("entity_id")

    # 1. Validation of ID presence
    if not entity_id:
        LOGGER.error("zone_bypass action called without entity_id")
        raise ServiceValidationError("The 'entity_id' argument is required.")

    # 2. Secure retrieval of the state object
    state_obj = hass.states.get(entity_id)
    if not state_obj:
        LOGGER.error("Entity not found for ID: %s", entity_id)
        raise ServiceValidationError(f"The entity {entity_id} does not exist in the state machine.")

    # 3. Extract and validate attributes
    attributes = state_obj.attributes
    zone_id = attributes.get("index")

    if zone_id is None:
        LOGGER.error("Entity %s has no 'index' attribute for bypass", entity_id)
        raise ServiceValidationError(f"Entity {entity_id} is not a valid zone (missing index).")

    try:
        zone_index = int(zone_id)
    except (ValueError, TypeError) as err:
        LOGGER.error("Zone index '%s' for %s is not a valid integer", zone_id, entity_id)
        raise ServiceValidationError(f"The index attribute '{zone_id}' must be an integer.") from err

    # 4. Logic to determine bypass state
    # Get the current state to toggle or force
    raw_bypass = attributes.get("bypass")
    try:
        cur_bypass = ZoneBypass(raw_bypass)
        # If bypass is OFF, we want to enable it (True), otherwise disable it (False)
        bypass_target = bool(cur_bypass == ZoneBypass.OFF)
    except ValueError:
        LOGGER.warning("Unknown bypass value '%s' for %s, falling back to default", raw_bypass, entity_id)
        bypass_target = True

    # 5. Access to integration resources
    coordinator = entry.runtime_data.coordinator
    client = entry.runtime_data.client
    pin = entry.options.get(CONF_PIN)

    # 6. Execute action with exception handling

    try:
        # index + 1 because the API expects 1-based indexing for zones
        await client.async_set_zone_bypass(zone_id=zone_index + 1, pin=pin, bypass=bypass_target)
        LOGGER.info("Success executing bypass for zone %s (index %s, target: %s)", entity_id, zone_index, bypass_target)

        # Force immediate data refresh after executing the scenario, so that the state of entities is updated
        # await coordinator.async_request_refresh()
        await coordinator.async_refresh()

    except Exception as err:
        LOGGER.exception("Error during async_set_zone_bypass API call for %s: %s", entity_id, err)
        raise HomeAssistantError(f"Failed to execute Ksenia bypass: {err}") from err
