"""
Button platform for ksenia.

to run scenario
"""

from typing import TYPE_CHECKING

from custom_components.ksenia.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.button.const import ButtonDeviceClass

from .scenario_button import KseniaLaresButton

if TYPE_CHECKING:
    from custom_components.ksenia.data import KseniaLaresConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
# ENTITY_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (*RESET_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        KseniaLaresButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=ButtonEntityDescription(
                key=f"{scenario.id}",
                translation_key="scenario",
                device_class=ButtonDeviceClass.RESTART,
                has_entity_name=True,
            ),
            scenario_name=scenario.name,
        )
        for scenario in coordinator.scenarios
    )
