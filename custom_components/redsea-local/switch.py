import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = hass.data[DOMAIN][entry.entry_id]["api"].get_factories("switch")
    async_add_entities(entities)
    hass.data[DOMAIN][entry.entry_id]["api"].add_entities(entities)


class RedSeaSwitchEntity(SwitchEntity):

    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self._device = device
        self._attr_is_on = False
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


class RedSeaDeviceModeSwitch(RedSeaSwitchEntity):

    def __init__(self, device, id, name, api):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._api = api

    async def async_turn_on(self, **kwargs):
        await self._api.set_reef_ato_autofill(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._api.set_reef_ato_autofill(False)
        self._attr_is_on = False
        self.async_write_ha_state()

    def handle_api_data(self, data):
        self._attr_is_on = data["configuration"]["auto_fill"]
        self._available = True
        self.async_write_ha_state()


class RedSeaReefMatAutoAdvanceSwitch(RedSeaSwitchEntity):

    def __init__(self, device, id, name, api):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._api = api

    async def async_turn_on(self, **kwargs):
        await self._api.set_reef_mat_autoadvance(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._api.set_reef_mat_autoadvance(False)
        self._attr_is_on = False
        self.async_write_ha_state()

    def handle_api_data(self, data):
        self._attr_is_on = data["auto_advance"]
        self._available = True
        self.async_write_ha_state()
