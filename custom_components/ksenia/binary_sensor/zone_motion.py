"""Zone motion sensor for ksenia.

Each alarm zone is exposed as a motion binary sensor.
Motion is detected when the zone status is anything other than NORMAL.
"""

from custom_components.ksenia.const import ATTRIBUTION, DOMAIN
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
        self._zone_index = zone.index
        # Use the zone description as the entity name
        self._attr_name = zone.description
        self._attr_device_class = entity_description.device_class

    @property
    def _zone(self) -> KseniaLaresZone | None:
        """Return current zone data from coordinator."""
        if self.coordinator.data is None:
            return None
        zones = self.coordinator.data.zones
        if self._zone_index < len(zones) and zones[self._zone_index].index == self._zone_index:
            return zones[self._zone_index]
        return next((z for z in zones if z.index == self._zone_index), None)

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
            "index": str(zone.index),
            "zone_status": str(zone.statusdescription.status),
            "bypass": str(zone.statusdescription.bypass),
            "integration": DOMAIN,
        }
