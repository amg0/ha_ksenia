"""Connectivity binary sensor for ksenia.

Reports whether the last coordinator update successfully reached the
Ksenia Lares alarm panel.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.ksenia.const import DOMAIN
from custom_components.ksenia.entity import KseniaLaresEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription

if TYPE_CHECKING:
    from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator


class KseniaLaresConnectivitySensor(BinarySensorEntity, KseniaLaresEntity):
    """Connectivity sensor showing whether the Ksenia panel is reachable."""

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def is_on(self) -> bool:
        """Return true if the last coordinator update was successful."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        base_attributes = {
            "update_interval": str(self.coordinator.update_interval),
            "integration": DOMAIN,
        }
        alarm_info = self.coordinator.data.alarminfo
        return base_attributes | alarm_info
