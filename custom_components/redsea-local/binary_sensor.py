import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass


from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    entities = hass.data[DOMAIN][entry.entry_id]["api"].get_factories("binary_sensor")
    async_add_entities(entities)
    hass.data[DOMAIN][entry.entry_id]["api"].add_entities(entities)
class RedSeaBinarySensor(BinarySensorEntity):
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

class RedSeaAtoLeakSensor(RedSeaBinarySensor):
    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._attr_device_class = BinarySensorDeviceClass.MOISTURE
        self._attr_is_on = False

    def handle_api_data(self, data):
        self._attr_is_on = data["leak_sensor"]["status"] != "dry"
        self._available = data["leak_sensor"]["connected"] and data["leak_sensor"]["enabled"]
        self.async_write_ha_state()

class RedSeaAtoPumpRunningSensor(RedSeaBinarySensor):
    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_is_on = False

    def handle_api_data(self, data):
        self._attr_is_on = data["is_pump_on"]
        self._available = True
        self.async_write_ha_state()

class RedSeaAtoDesiredWaterLevelSensor(RedSeaBinarySensor):
    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._attr_is_on = False

    def handle_api_data(self, data):
        self._attr_is_on = data["water_level"].startswith("desired")
        self._available = data["ato_sensor"]["connected"]
        self.async_write_ha_state()