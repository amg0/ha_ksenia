"""Partition binary sensor for ksenia."""

from __future__ import annotations

from custom_components.ksenia.api.client import PartitionStatus
from custom_components.ksenia.const import ATTRIBUTION, DOMAIN
from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator
from custom_components.ksenia.entity import KseniaLaresEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription


class KseniaLaresPartitionBinarySensor(BinarySensorEntity, KseniaLaresEntity):
    """Binary sensor representing a Ksenia Lares partition status.

    Reports state 'on' (unlocked) when the partition status is DISARMED.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        partition_name: str,
    ) -> None:
        """Initialize the partition binary sensor."""
        super().__init__(coordinator, entity_description)
        self._partition_name = partition_name
        self._attr_name = partition_name
        self._coordinator = coordinator

    @property
    def available(self) -> bool:
        """Return True if coordinator last update succeeded."""
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        """Return True if partition is unlocked (status is DISARMED)."""
        partition = self._coordinator.partitions.get(self._partition_name)
        if partition is None:
            return False
        return partition.status == PartitionStatus.DISARMED

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional partition state attributes."""
        partition = self._coordinator.partitions.get(self._partition_name, None)

        return {"partition_status": str(partition.status if partition else "UNKNOWN"), "integration": DOMAIN}
