"""
Button platform for ksenia.

to run scenario
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.button import ButtonDeviceClass, ButtonEntityDescription

from .partition_button import KseniaLaresButton

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
            api=entry.runtime_data.client,
            entity_description=ButtonEntityDescription(
                key=f"{scenario.id}",
                name=f"{scenario.name}",
                # translation_key="reset_filter",
                icon="mdi:alarm-light-outline",
                device_class=ButtonDeviceClass.RESTART,
                # entity_category=EntityCategory.CONFIG,
                has_entity_name=True,
            ),
        )
        for scenario in coordinator.scenarios
    )
