"""Constants for ksenia."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "ksenia"
ATTRIBUTION = "Data provided by Ksenia Lares alarm panel"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Config entry data keys (in addition to homeassistant.const keys)
CONF_PIN = "pin"
CONF_REFRESH_PERIOD = "refresh_period"

# Default configuration values
DEFAULT_REFRESH_PERIOD = 15  # seconds
