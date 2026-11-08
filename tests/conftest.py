"""Global fixtures for ksenia tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ksenia.api.client import (
    AlarmInfo,
    KseniaLaresScenario,
    KseniaPartition,
    PartitionStatus,
    ZoneBypass,
    ZoneDescription,
    ZoneStatus,
    ZoneStatusDescription,
)
from custom_components.ksenia.const import CONF_ZONE_CONFIGURATIONS, DOMAIN
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations for testing."""
    return


@pytest.fixture
def mock_api() -> Generator[AsyncMock]:
    """Mock the KseniaLaresApiClient."""
    with (
        patch("custom_components.ksenia.KseniaLaresApiClient", autospec=True) as client_class,
        patch(
            "custom_components.ksenia.config_flow_handler.validators.credentials.KseniaLaresApiClient",
            new=client_class,
        ),
    ):
        client = client_class.return_value
        client.alarm_info = AlarmInfo(
            host="http://192.168.1.100:80",
            name="Ksenia Lares 48IP",
            model="48IP",
            info="Ksenia Security",
            version="3",
            revision="1",
            build="10",
        )
        client.async_get_alarm_info.return_value = client.alarm_info
        client.async_get_zone_descriptions.return_value = [
            ZoneDescription(description="Living Room Motion", index=0),
            ZoneDescription(description="Front Door", index=1),
        ]
        client.async_get_zone_statuses.return_value = [
            ZoneStatusDescription(status=ZoneStatus.NORMAL, bypass=ZoneBypass.OFF),
            ZoneStatusDescription(status=ZoneStatus.ALARM, bypass=ZoneBypass.ON),
        ]
        client.async_get_partition_statuses.return_value = {
            "Main House": KseniaPartition(id=0, description="Main House", status=PartitionStatus.DISARMED),
            "Garage": KseniaPartition(id=1, description="Garage", status=PartitionStatus.ARMED),
        }
        client.async_get_scenarios.return_value = [
            KseniaLaresScenario(id=0, name="Arm Away", nopin=False),
            KseniaLaresScenario(id=1, name="Disarm", nopin=True),
        ]
        client.async_get_logs.return_value = []
        client.async_test_connection.return_value = client.async_get_zone_descriptions.return_value
        yield client


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Ksenia Lares (192.168.1.100)",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: 80,
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "secret_password",
            CONF_ZONE_CONFIGURATIONS: {
                "Living Room Motion": BinarySensorDeviceClass.MOTION,
                "Front Door": BinarySensorDeviceClass.DOOR,
            },
        },
        options={},
        entry_id="mock_ksenia_entry",
        unique_id="192.168.1.100",
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_api: AsyncMock,
) -> MockConfigEntry:
    """Set up the Ksenia integration for testing."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
