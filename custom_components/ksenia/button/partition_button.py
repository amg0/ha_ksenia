"""
Run Scenario button for ksenia.

test
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.ksenia.api import KseniaLaresApiClientError
from custom_components.ksenia.api.client import KseniaLaresApiClient
from custom_components.ksenia.const import LOGGER
from custom_components.ksenia.entity import KseniaLaresEntity
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator

# ENTITY_DESCRIPTIONS = (
#     ButtonEntityDescription(
#         key="reset_filter",
#         translation_key="reset_filter",
#         icon="mdi:restart",
#         device_class=ButtonDeviceClass.RESTART,
#         entity_category=EntityCategory.CONFIG,
#         has_entity_name=True,
#     ),
# )


class KseniaLaresButton(ButtonEntity, KseniaLaresEntity):
    """Reset filter button class."""

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        api: KseniaLaresApiClient,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description)
        self._api = api

    async def async_press(self) -> None:
        """
        Handle the button press.

        This simulates resetting the filter timer. In a real integration,
        this would send an API command to reset the device's filter counter.

        Demo: This also affects the filter_life sensor - watch it jump to 100%!
        """
        scenarioid = int(self.entity_description.key)
        client = self._api
        scenario_list = self.coordinator.scenarios
        scenario = next((s for s in scenario_list if s.id == scenarioid), None)
        if scenario is not None:
            try:
                xml = await client.async_run_scenario(scenario_id=scenario.id, pin=None)
                LOGGER.debug("Scenario %s executed successfully. Response: %s", scenario.name, xml)
            except KseniaLaresApiClientError as exception:
                msg = f"Failed to reset filter: {exception}"
                raise HomeAssistantError(msg) from exception
