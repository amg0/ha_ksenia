"""Test integration setup and teardown."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant


@pytest.mark.unit
async def test_setup_and_unload_entry(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test setting up and unloading the integration."""
    entry = init_integration
    assert entry.state is ConfigEntryState.LOADED

    # Binary sensor connectivity should exist
    conn_state = hass.states.get("binary_sensor.ksenia_lares_api_connection")
    assert conn_state is not None
    assert conn_state.state == "on"

    # Zone sensors
    motion_state = hass.states.get("binary_sensor.ksenia_lares_living_room_motion")
    assert motion_state is not None
    assert motion_state.state == "off"

    door_state = hass.states.get("binary_sensor.ksenia_lares_front_door")
    assert door_state is not None
    assert door_state.state == "on"
    assert door_state.attributes.get("bypass") == "BYPASS"

    # Unload
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
