"""Test Ksenia config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.ksenia.api.client import ZoneDescription
from custom_components.ksenia.const import DOMAIN
from homeassistant import config_entries
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


@pytest.mark.unit
async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test full successful user config flow."""
    with patch(
        "custom_components.ksenia.config_flow_handler.config_flow.validate_credentials",
        new_callable=AsyncMock,
    ) as mock_validate:
        mock_validate.return_value = [
            ZoneDescription(description="Living Room Motion", index=0),
            ZoneDescription(description="Front Door", index=1),
        ]

        # Step 1: user credentials
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 80,
                CONF_USERNAME: "admin",
                CONF_PASSWORD: "secret_password",
            },
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "init_option"

        # Step 2: options
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "refresh_period": 15,
                "pin": "1234",
            },
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "zone_init"

        # Step 3: zones configuration
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "Living Room Motion": BinarySensorDeviceClass.MOTION,
                "Front Door": BinarySensorDeviceClass.DOOR,
            },
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Ksenia Lares (192.168.1.100)"
        assert result["data"][CONF_HOST] == "192.168.1.100"
        assert result["options"]["refresh_period"] == 15
