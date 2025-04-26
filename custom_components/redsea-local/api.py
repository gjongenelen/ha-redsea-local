import logging

import aiohttp

from .binary_sensor import RedSeaAtoLeakSensor, RedSeaAtoPumpRunningSensor, RedSeaAtoDesiredWaterLevelSensor
from .sensor import RedSeaAtoTempSensor, RedSeaTodayVolumeSensor, RedSeaWaterLevelSensor
from .switch import RedSeaDeviceModeSwitch

_LOGGER = logging.getLogger(__name__)


class RedSeaApi:
    factories = {}
    entities = []

    def __init__(self, device, ip, type):
        self.ip = ip
        self.type = type
        self.device = device

    def get_factories(self, platform):
        return self.factories[platform]

    def add_entities(self, entities):
        return self.entities.extend(entities)

    def update(self, data):
        _LOGGER.debug("API data: %s", self.entities)
        for entity in self.entities:
            entity.handle_api_data(data)

    async def get_data(self, url):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(
                    f'http://{self.ip}{url}',
                    headers={
                        "Content-Type": "application/json",
                    }
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def put_data(self, url, data):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.put(
                    f'http://{self.ip}{url}',
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                    }
            ) as response:
                response.raise_for_status()
                return await response.json()


class RedSeaAtoApi(RedSeaApi):
    def __init__(self, device, ip, type):
        super().__init__(device, ip, type)
        self.factories = {
            "binary_sensor": [
                RedSeaAtoLeakSensor(self.device, "water_leak", "Water leak"),
                RedSeaAtoPumpRunningSensor(self.device, "pump_running", "Pump running"),
                RedSeaAtoDesiredWaterLevelSensor(self.device, "desired_water_level", "Desired water level"),
            ],
            "sensor": [
                RedSeaAtoTempSensor(self.device, "temperature", "Temperature"),
                RedSeaTodayVolumeSensor(self.device, "today_volume", "Today volume"),
                RedSeaWaterLevelSensor(self.device, "water_level", "Water level"),
            ],
            "switch": [
                RedSeaDeviceModeSwitch(self.device, "mode", "Auto fill", self),
            ],
            "number": [
            ]
        }

    def set_reef_ato_autofill(self, enabled):
        return self.put_data("/configuration", {
            "auto_fill": enabled
        })

    async def fetch_data(self):
        data = await self.get_data("/dashboard")
        data["configuration"] = await self.get_data("/configuration")
        return data
