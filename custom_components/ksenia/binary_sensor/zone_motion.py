"""Zone motion sensor for ksenia.

Each alarm zone is exposed as a motion binary sensor.
Motion is detected when the zone status is anything other than NORMAL.
"""

from __future__ import annotations

from custom_components.ksenia.const import ATTRIBUTION
from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator, KseniaLaresZone
from custom_components.ksenia.entity.base import KseniaLaresEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription


class KseniaLaresZoneMotionSensor(BinarySensorEntity, KseniaLaresEntity):
    """
    Motion sensor entity for a single Ksenia alarm zone.

    Reports motion (is_on=True) when the zone status is not NORMAL.
    The entity is created dynamically from the zone descriptions fetched
    during coordinator setup.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        zone: KseniaLaresZone,
    ) -> None:
        """
        Initialize the zone motion sensor.

        Args:
            coordinator: The data update coordinator for this entity.
            zone: The zone data (index + description) for this sensor.

        """
        super().__init__(coordinator, entity_description)
        # self._coordinator = coordinator
        self._zone_index = zone.index
        # Unique ID: entry_id + zone index so renaming zones doesn't break entities
        # self._attr_unique_id = f"{coordinator.config_entry.entry_id}_zone_{zone.index}"
        # Use the zone description as the entity name
        self._attr_name = zone.description
        self._attr_device_class = entity_description.device_class
        # self._attr_device_info = DeviceInfo(
        #     identifiers={
        #         (
        #             coordinator.config_entry.domain,
        #             coordinator.config_entry.entry_id,
        #         ),
        #     },
        #     name=coordinator.config_entry.title,
        #     manufacturer="Ksenia",
        #     model="Lares",
        # )

    @property
    def _zone(self) -> KseniaLaresZone | None:
        """Return current zone data from coordinator."""
        if self.coordinator.data is None:
            return None
        zones = self.coordinator.data.zones
        if self._zone_index < len(zones):
            return zones[self._zone_index]
        return None

    @property
    def available(self) -> bool:
        """Return True if coordinator last update succeeded."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Return True if zone is in a non-NORMAL state (motion detected)."""
        zone = self._zone
        if zone is None:
            return False
        return zone.is_triggered

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional zone state attributes."""
        zone = self._zone
        if zone is None:
            return {}
        return {
            "zone_status": str(zone.status),
            "bypass": str(zone.bypass),
        }

    async def async_added_to_hass(self) -> None:
        """Register coordinator listener when added to HA."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
