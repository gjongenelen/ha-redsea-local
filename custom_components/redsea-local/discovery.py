import asyncio
import logging
import aiohttp
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)

class Discovery:
    def __init__(self, ip):
        self.ip = ip

    async def get_type(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(
                    f"http://{self.ip}/description.xml",
            ) as response:
                response.raise_for_status()
                data = await response.text()
                _LOGGER.debug("Discovery response: %s", data)

                root = ET.fromstring(data)
                ns = {'upnp': 'urn:schemas-upnp-org:device-1-0'}
                device = root.find("upnp:device", namespaces=ns)
                if device is None:
                    raise ValueError("Device element not found in XML")

                id = device.findtext("upnp:serialNumber", namespaces=ns)
                name = device.findtext("upnp:friendlyName", namespaces=ns)
                model = device.findtext("upnp:modelName", namespaces=ns)
                manufacturer = device.findtext("upnp:manufacturer", namespaces=ns)
                device_type = device.findtext("upnp:deviceType", namespaces=ns)
                return id, name, model, manufacturer, device_type
