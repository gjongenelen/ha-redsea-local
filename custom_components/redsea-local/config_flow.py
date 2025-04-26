import logging

import voluptuous as vol
from homeassistant import config_entries
from .discovery import Discovery

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN


class RedSeaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({
                vol.Required("ip"): str,
            }), errors=errors)

        discovery = Discovery(user_input["ip"])

        id, name, model, manufacturer, type = await discovery.get_type()

        return self.async_create_entry(
            title=name,
            data={
                "ip": user_input["ip"],
                "type": type,
                "device_id": id,
                "device_name": name,
                "device_model": model,
                "device_manufacturer": manufacturer,


            },
        )
