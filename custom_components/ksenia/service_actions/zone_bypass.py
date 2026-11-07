"""Zone Bypass service action handler for ksenia."""

from typing import TYPE_CHECKING

from custom_components.ksenia.api.client import ZoneBypass
from custom_components.ksenia.const import CONF_PIN, DOMAIN, LOGGER
from custom_components.ksenia.data import KseniaLaresConfigEntry
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_handle_zone_bypass(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
    call: ServiceCall,
) -> None:
    """Handle the zone_bypass service action."""

    entity_id_raw = call.data.get("entity_id")

    # 1. Validation of ID presence
    if not entity_id_raw:
        LOGGER.error("zone_bypass action called without entity_id")
        raise ServiceValidationError("The 'entity_id' argument is required.")

    entity_id = entity_id_raw[0] if isinstance(entity_id_raw, list) else entity_id_raw

    # Resolve the config entry owning this entity when registered in the entity registry
    entity_registry = er.async_get(hass)
    if (entity_entry := entity_registry.async_get(entity_id)) and entity_entry.config_entry_id:
        if entity_entry.platform != DOMAIN:
            raise ServiceValidationError(f"Entity {entity_id} does not belong to domain {DOMAIN}.")
        resolved_entry = hass.config_entries.async_get_entry(entity_entry.config_entry_id)
        if resolved_entry is not None:
            entry = resolved_entry

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
        xml = await client.async_set_zone_bypass(zone_id=zone_index + 1, pin=pin, bypass=bypass_target)
        if "cmdSent" not in xml:
            LOGGER.warning("Zone bypass for %s may have been rejected. Response: %s", entity_id, xml)
        else:
            LOGGER.info(
                "Success executing bypass for zone %s (index %s, target: %s)", entity_id, zone_index, bypass_target
            )

        # Force immediate data refresh after executing the bypass so entity states update
        await coordinator.async_refresh()

    except Exception as err:
        LOGGER.exception("Error during async_set_zone_bypass API call for %s: %s", entity_id, err)
        raise HomeAssistantError(f"Failed to execute Ksenia bypass: {err}") from err
