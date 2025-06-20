import logging

import aiohttp

from .binary_sensor import *
from .sensor import *
from .switch import *

_LOGGER = logging.getLogger(__name__)


class RedSeaApi:

    def __init__(self, device, ip, type):
        self.ip = ip
        self.type = type
        self.device = device
        self.factories = {}
        self.entities = []

    def get_factories(self, platform):
        return self.factories[platform]

    def add_entities(self, entities):
        return self.entities.extend(entities)

    def update(self, data):
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


class RedSeaReefMatApi(RedSeaApi):
    def __init__(self, device, ip, type):
        super().__init__(device, ip, type)
        self.factories = {
            "binary_sensor": [
                RedSeaReefMatIsInternetConnectedSensor(self.device, "is_internet_connected", "Internet connected"),
                RedSeaReefMatIsECSensorConnectedSensor(self.device, "is_ec_sensor_connected", "EC sensor connected"),
                RedSeaReefMatUncleanSensor(self.device, "unclean_sensor", "Unclean sensor"),
                
            ],
            "sensor": [
                RedSeaReefMatDayToEndOfRollSensor(self.device, "days_till_end_of_roll", "Days till end of roll"),
                RedSeaReefMatTodayUsageSensor(self.device, "today_usage", "Today usage"),
                RedSeaReefMatDailyAverageUsageSensor(self.device, "daily_average_usage", "Daily average usage"),
                
            ],
            "switch": [
                RedSeaReefMatAutoAdvanceSwitch(self.device, "auto_advance", "Auto advance", self),
            ],
            "number": [
            ]
        }
        _LOGGER.error("ReefMat API factories: %s", self.factories)

    def set_reef_mat_autoadvance(self, enabled):
        return self.put_data("/configuration", {
            "auto_advance": enabled
        })

    async def fetch_data(self):
        data = await self.get_data("/dashboard")
        return data
