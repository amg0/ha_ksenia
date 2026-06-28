"""Binary sensor platform for ksenia.

Provides:
- One motion binary sensor per alarm zone (dynamic, from coordinator data)
- One API connectivity binary sensor (diagnostic)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntityDescription
from homeassistant.const import EntityCategory

from .connectivity import KseniaLaresConnectivitySensor
from .zone_motion import KseniaLaresZoneMotionSensor

if TYPE_CHECKING:
    from custom_components.ksenia.data import KseniaLaresConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform.

    Creates one motion or door sensor per zone discovered at coordinator setup,
    plus a single connectivity diagnostic sensor.
    """
    coordinator = entry.runtime_data.coordinator
    zone_configuration: dict[str, BinarySensorDeviceClass] = entry.data["zone_configurations"]
    # Create one motion sensor per zone (discovered during coordinator _async_setup)
    zone_entities = [
        KseniaLaresZoneMotionSensor(
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=f"{zone.description}",
                # translation_key="api_connectivity",
                device_class=zone_configuration.get(zone.description, BinarySensorDeviceClass.MOTION),
                # entity_category=EntityCategory.DIAGNOSTIC,
                # icon="mdi:api",
                has_entity_name=True,
            ),
            zone=zone,
        )
        for zone in coordinator.data.zones
    ]

    # Create the API connectivity diagnostic sensor
    connectivity_entities = [
        KseniaLaresConnectivitySensor(
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key="api_connectivity",
                translation_key="api_connectivity",
                device_class=BinarySensorDeviceClass.CONNECTIVITY,
                entity_category=EntityCategory.DIAGNOSTIC,
                icon="mdi:api",
                has_entity_name=True,
            ),
        )
    ]

    async_add_entities([*zone_entities, *connectivity_entities])
