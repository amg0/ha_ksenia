"""Constants for ksenia."""

from logging import Logger, getLogger
from pathlib import Path
from typing import Final

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "ksenia"
ATTRIBUTION = "Data provided by Ksenia Lares alarm panel"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Config entry data keys (in addition to homeassistant.const keys)
CONF_PIN = "pin"
CONF_REFRESH_PERIOD = "refresh_period"
CONF_ZONE_LIST = "zones"
CONF_ZONE_CONFIGURATIONS = "zone_configurations"


# Default configuration values
DEFAULT_REFRESH_PERIOD = 15  # seconds

# Read version from manifest.json
MANIFEST_PATH = Path(__file__).parent / "manifest.json"
# with Path.open(MANIFEST_PATH, encoding="utf-8") as f:
#     INTEGRATION_VERSION: Final[str] = json.load(f).get("version", "0.0.0")


# Base URL for frontend resources
URL_BASE: Final[str] = "/ksenia"

# List of JavaScript modules to register
# JSMODULES: Final[list[dict[str, str]]] = [
#     {
#         "name": "KSenia Card",
#         "filename": "ksenia-security-card.js",
#         "version": INTEGRATION_VERSION,
#     },
#     # Add editor if needed
#     # {
#     #     "name": "Your Card Editor",
#     #     "filename": "your-card-editor.js",
#     #     "version": INTEGRATION_VERSION,
#     # },
# ]
