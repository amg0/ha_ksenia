"""Sensor platform for ksenia.

Provides:
- Event logs sensor that tracks Ksenia alarm system events
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import EntityCategory

from .logs import KseniaLogSensor

if TYPE_CHECKING:
    from custom_components.ksenia.data import KseniaLaresConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform.

    Creates a single log sensor that tracks all system events.
    """
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        [
            KseniaLogSensor(
                coordinator=coordinator,
                entity_description=SensorEntityDescription(
                    key="ksenia_logs",
                    translation_key="logs",
                    entity_category=EntityCategory.DIAGNOSTIC,
                    has_entity_name=True,
                ),
            ),
        ],
    )
