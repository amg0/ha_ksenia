"""
Custom integration to integrate ksenia with Home Assistant.

Connects to the Ksenia Lares alarm panel over the local network,
fetching zone data to expose motion detection sensors.

For more details about this integration, please refer to:
https://github.com/amg0/ha_ksenia

For integration development guidelines:
https://developers.home-assistant.io/docs/creating_integration_manifest
"""

from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .api import KseniaLaresApiClient
from .const import CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD, DOMAIN, LOGGER, URL_BASE
from .coordinator import KseniaLaresDataUpdateCoordinator
from .data import KseniaLaresData
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import KseniaLaresConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

# This integration is configured via config entries only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


# small synchronous function to read the file content
def _get_manifest_data(path: Path) -> dict:
    """Lecture synchrone du manifest (exécutée dans un thread séparé)."""
    return json.loads(path.read_text(encoding="utf-8"))


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Set up the integration.

    Registers service actions at startup. Services must be registered here
    (not in async_setup_entry) to satisfy the Silver Quality Scale requirement.

    Args:
        hass: The Home Assistant instance.
        config: The Home Assistant configuration.

    Returns:
        True if setup was successful.

    """
    # Path(__file__) gives path of this file (__init__.py)
    # .parent gets the folder containing that file
    integration_dir = Path(__file__).parent
    manifest_path = integration_dir / "manifest.json"
    try:
        # manifest_path.read_text() ouvre, lit et ferme le fichier automatiquement
        # On utilise l'executor pour ne pas bloquer l'event loop [4]
        manifest_data = await hass.async_add_executor_job(_get_manifest_data, manifest_path)
        version = manifest_data.get("version", "unknown")
        name = manifest_data.get("name", "noname for Integration")

        LOGGER.info("Starting Integration %s (Version: %s)", name, version)
    except FileNotFoundError:
        LOGGER.error("File manifest.json cannot be found in %s", integration_dir)
    except ValueError as err:
        LOGGER.error("Erreur lors de la lecture du manifest : %s", err)

    await async_setup_services(hass)

    # 1. Cibler le dossier contenant le JS sur le disque
    frontend_dir = Path(__file__).parent / "frontend"
    LOGGER.debug(f"async_setup() - frontend dir {frontend_dir}")

    if frontend_dir.exists():
        # 2. Enregistrer la route HTTP statique avec la nouvelle API asynchrone
        # cache_headers=False est recommandé en développement. À passer à True en production.
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, str(frontend_dir), cache_headers=False)]
        )

        # 3. Enregistrer la carte dans les resources Lovelace (Nouvelle API)
        if "lovelace" in hass.data:
            lovelace = hass.data["lovelace"]

            # since HA 2026.2, resources is an attribute direct of object lovelace
            resources: ResourceStorageCollection | None = getattr(lovelace, "resources", None)

            if resources:
                # Action critique : forcer le chargement de la collection pour ne pas écraser les données existantes
                await resources.async_get_info()

                base_file_url = f"{URL_BASE}/ksenia-security-card.js"
                card_url = f"{base_file_url}?v={version}"

                resource_id = None
                needs_update = False

                # Parcourir les resources existantes pour identifier si la carte est déjà là
                for item in resources.async_items():
                    if item.get("url", "").startswith(base_file_url):
                        resource_id = item.get("id")
                        # Détecter si la version (paramètre v=...) a changé
                        if item.get("url") != card_url:
                            needs_update = True
                        break

                # Mettre à jour la resource existante ou la créer
                if resource_id and needs_update:
                    await resources.async_update_item(resource_id, {"res_type": "module", "url": card_url})
                    LOGGER.info("resource Lovelace updated successfully : %s", card_url)
                elif not resource_id:
                    await resources.async_create_item({"res_type": "module", "url": card_url})
                    LOGGER.info("New resource Lovelace added : %s", card_url)
        else:
            LOGGER.warning("Lovelace component is not loaded. impossible to add the resource.")

        LOGGER.info("Lovelace resource loaded with success : %s", card_url)
    else:
        LOGGER.warning("The frontend folder does not exist or is not reachable : %s", frontend_dir)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> bool:
    """
    Set up this integration using UI.

    Creates the API client using the host + credentials from the config entry,
    then initialises the coordinator with the configured refresh period from
    options (defaulting to DEFAULT_REFRESH_PERIOD seconds).

    Data flow:
      1. User enters host/username/password in config flow
      2. Credentials stored in entry.data
      3. API Client initialised with host + credentials
      4. Coordinator fetches zone descriptions (once) then polls zone statuses
      5. Binary sensor entities read zone data from coordinator.data

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.

    Returns:
        True if setup was successful.

    """
    refresh_period = entry.options.get(CONF_REFRESH_PERIOD, DEFAULT_REFRESH_PERIOD)

    client = KseniaLaresApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    coordinator = KseniaLaresDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(seconds=refresh_period),
    )

    entry.runtime_data = KseniaLaresData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # Performs zone description fetch (_async_setup) then first zone status poll
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being unloaded.

    Returns:
        True if unload was successful.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: KseniaLaresConfigEntry,
) -> None:
    """
    Reload config entry when options change.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being reloaded.

    """
    await hass.config_entries.async_reload(entry.entry_id)
