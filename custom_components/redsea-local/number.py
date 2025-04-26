import logging
from homeassistant.components.number import NumberEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    entities = hass.data[DOMAIN][entry.entry_id]["api"].get_factories("number")
    async_add_entities(entities)
    hass.data[DOMAIN][entry.entry_id]["api"].add_entities(entities)

class RedSeaNumberEntity(NumberEntity):

    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self._attr_name = name
        self._device = device
        self._attr_native_value = 0
        self._available = False

    @property
    def available(self):
        return self._available

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["id"])},
            "name": self._device["name"],
            "manufacturer": self._device["manufacturer"],
            "model": self._device["model"],
        }
