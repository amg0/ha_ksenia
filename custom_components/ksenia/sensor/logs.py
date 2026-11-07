"""Event logs sensor for ksenia.

Tracks system events and stores them in sensor attributes.
"""

from typing import TYPE_CHECKING, Any

from custom_components.ksenia.entity import KseniaLaresEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

if TYPE_CHECKING:
    from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator


class KseniaLogSensor(SensorEntity, KseniaLaresEntity):
    """Sensor that tracks Ksenia event logs."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor using a DataUpdateCoordinator."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> str:
        """Return the state of the sensor (latest event)."""
        if self.coordinator.data and (logs := self.coordinator.data.logs):
            return logs[0].event[:255]
        return "No logs"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the logs collection as nested data attributes."""
        if not self.coordinator.data or not self.coordinator.data.logs:
            return {}

        # Serialize the list of KseniaLog dataclasses into simple dictionaries
        return {
            "entries": [
                {
                    "id": log.log_id,
                    "type": log.log_type,
                    "timestamp": log.timestamp.isoformat(),
                    "event": log.event,
                    "generator": log.generator,
                    "means": log.means,
                }
                for log in self.coordinator.data.logs
            ]
        }
