"""
Base entity class for ksenia.

This module provides the base entity class that all integration entities inherit from.
It handles common functionality like device info, unique IDs, and coordinator integration.

For more information on entities:
https://developers.home-assistant.io/docs/core/entity
https://developers.home-assistant.io/docs/core/entity/index/#common-properties
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.const import ATTRIBUTION
from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator
from custom_components.ksenia.entity_utils.device_info import create_device_info
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class KseniaLaresEntity(CoordinatorEntity[KseniaLaresDataUpdateCoordinator]):
    """
    Base entity class for ksenia.

    All entities in this integration inherit from this class, which provides:
    - Automatic coordinator updates
    - Device info management
    - Unique ID generation
    - Attribution and naming conventions

    For more information:
    https://developers.home-assistant.io/docs/core/entity
    https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """
        Initialize the base entity.

        Args:
            coordinator: The data update coordinator for this entity.
            entity_description: The entity description defining characteristics.

        """
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"

        self._attr_device_info = create_device_info(
            config_entry=coordinator.config_entry,
            name="Ksenia Lares",  # coordinator.config_entry.title,
            manufacturer="Ksenia",
            model="Lares",
            # sw_version: str | None = None
        )
