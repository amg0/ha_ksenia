"""
Run Scenario button for ksenia.

test
"""

from typing import TYPE_CHECKING

from custom_components.ksenia.api import KseniaLaresApiClientError
from custom_components.ksenia.const import CONF_PIN, DOMAIN, LOGGER
from custom_components.ksenia.entity import KseniaLaresEntity
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.ksenia.coordinator import KseniaLaresDataUpdateCoordinator


class KseniaLaresButton(ButtonEntity, KseniaLaresEntity):
    """Scenario execution button class."""

    def __init__(
        self,
        coordinator: KseniaLaresDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
        scenario_name: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entity_description)
        self._attr_name = scenario_name

    async def async_press(self) -> None:
        """Execute the Ksenia scenario when the button is pressed."""
        scenario_id = int(self.entity_description.key)
        scenario_list = self.coordinator.scenarios
        scenario = next((s for s in scenario_list if s.id == scenario_id), None)
        if scenario is None:
            msg = f"Scenario ID {scenario_id} not found"
            raise HomeAssistantError(msg)

        pin = None if scenario.nopin else self.coordinator.config_entry.options.get(CONF_PIN)
        if not scenario.nopin and not pin:
            msg = f"Scenario '{scenario.name}' requires a PIN, but no PIN is configured in options"
            raise HomeAssistantError(msg)

        try:
            xml = await self.coordinator.config_entry.runtime_data.client.async_run_scenario(
                scenario_id=scenario.id,
                pin=pin,
            )
        except KseniaLaresApiClientError as exception:
            msg = f"Failed to call Ksenia API: {exception}"
            raise HomeAssistantError(msg) from exception

        if "cmdSent" in xml:
            LOGGER.info("Scenario %s executed successfully. Response: %s", scenario.name, xml)
            await self.coordinator.async_request_refresh()
        else:
            LOGGER.warning("Scenario %s execution failed. Response: %s", scenario.name, xml)
            msg = f"Scenario '{scenario.name}' was rejected by the Ksenia controller"
            raise HomeAssistantError(msg)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional zone state attributes."""

        return {
            "integration": DOMAIN,
        }
