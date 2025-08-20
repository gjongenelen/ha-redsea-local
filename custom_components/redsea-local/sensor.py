import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    entities = hass.data[DOMAIN][entry.entry_id]["api"].get_factories("sensor")
    _LOGGER.error("Entities: %s", entities[0].name)
    async_add_entities(entities)
    hass.data[DOMAIN][entry.entry_id]["api"].add_entities(entities)
    _LOGGER.error("Entities2: %s", hass.data[DOMAIN][entry.entry_id]["api"].entities[0].name)

class RedSeaSensor(SensorEntity):
    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self._device = device
        self._state = None
        self._available = False

    @property
    def state(self):
        return self._state

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

    @property
    def unit_of_measurement(self):
        return getattr(self, "_unit", None)

class RedSeaAtoTempSensor(RedSeaSensor):
    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._unit = UnitOfTemperature.CELSIUS

    def handle_api_data(self, data):
        self._state = data["ato_sensor"]["current_read"]
        self._available = data["ato_sensor"]["connected"] and data["ato_sensor"]["is_temp_enabled"]
        self.async_write_ha_state()

class RedSeaTodayVolumeSensor(RedSeaSensor):

    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._unit = "mL"
        self._attr_device_class = SensorDeviceClass.WATER
        self._state = 0

    def handle_api_data(self, data):
        self._state = data["today_volume_usage"]
        self._available = True
        self.async_write_ha_state()

class RedSeaWaterLevelSensor(RedSeaSensor):

    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)

    def handle_api_data(self, data):
        self._state = data["water_level"]
        self._available = data["ato_sensor"]["connected"]
        self.async_write_ha_state()

class RedSeaReefMatDayToEndOfRollSensor(RedSeaSensor):

    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._unit = "days"

    def handle_api_data(self, data):
        self._state = data["days_till_end_of_roll"]
        self._available = True
        self.async_write_ha_state()

class RedSeaReefMatTodayUsageSensor(RedSeaSensor):

    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._unit = "cm"

    def handle_api_data(self, data):
        self._state = data["today_usage"]
        self._available = True
        self.async_write_ha_state()

class RedSeaReefMatDailyAverageUsageSensor(RedSeaSensor):

    def __init__(self, device, id, name):
        super().__init__(device, f'{device["id"]}_{id}', name)
        self._unit = "cm"

    def handle_api_data(self, data):
        self._state = data["daily_average_usage"]
        self._available = True
        self.async_write_ha_state()