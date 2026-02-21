import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_BATTERY_ENTITY, CONF_CHARGE_CURRENT, CONF_POWER_USAGE, CONF_PHASES

class IntelligentChargingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Car Charger", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BATTERY_ENTITY): str,
                vol.Required(CONF_CHARGE_CURRENT): str,
                vol.Required(CONF_POWER_USAGE): str,
                vol.Required(CONF_PHASES, default="1"): vol.In(["1", "3"]),
            })
        )