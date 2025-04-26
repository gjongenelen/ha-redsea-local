import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import *
from .const import DOMAIN

PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN][entry.entry_id] = {}

    apiFn = None

    if entry.data["type"] == "reef-ato":
        apiFn = RedSeaAtoApi

    if entry.data["type"] == "reef-mat":
        apiFn = RedSeaReefMatApi

    if apiFn == None:
        _LOGGER.error("Unsupported device type: %s", entry.data["type"])
        return False

    apiI = apiFn({
        "id": entry.data["device_id"],
        "name": entry.data["device_name"],
        "model": entry.data["device_model"],
        "manufacturer": entry.data["device_manufacturer"]
    }, entry.data["ip"], entry.data["type"])

    hass.data[DOMAIN][entry.entry_id]["api"] = apiI

    stop_event = asyncio.Event()

    async def poll_data():
        while not stop_event.is_set():
            try:
                data = await apiI.fetch_data()
                _LOGGER.info("Fetched data successfully for %s, %s", entry.data["device_name"], data)
                _LOGGER.info(apiI.entities)
                apiI.update(data)
            except Exception as e:
                _LOGGER.warning("Failed to fetch_data: %s", e)
            await asyncio.sleep(15)

    task = asyncio.create_task(poll_data())

    hass.data[DOMAIN][entry.entry_id]["stop_event"] = stop_event
    hass.data[DOMAIN][entry.entry_id]["task"] = task

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.error("%s API factories: %s", entry.data["type"], apiI.entities)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    data = hass.data[DOMAIN].pop(entry.entry_id)
    data["stop_event"].set()
    data["task"].cancel()
    try:
        await data["task"]
    except asyncio.CancelledError:
        pass
    return True
