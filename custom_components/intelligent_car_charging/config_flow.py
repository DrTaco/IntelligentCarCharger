import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import (
    DOMAIN,
    CONF_BATTERY_ENTITY,
    CONF_CABLE_CONNECTED,
    CONF_CHARGE_CURRENT,
    CONF_POWER_USAGE,
    CONF_PHASES
)

class IntelligentChargingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Car Charger", data=user_input)

        # Define the schema with sophisticated selectors
        DATA_SCHEMA = vol.Schema({
            # This creates a dropdown filtered for % battery sensors
            vol.Required(CONF_BATTERY_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    device_class="battery",
                    domain="sensor",
                    multiple=False,
                )
            ),


            vol.Required(CONF_CABLE_CONNECTED): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="binary_sensor",
                    device_class="connectivity",
                )
            ),

            # Selector for Charge Current (Amps)
            vol.Required(CONF_CHARGE_CURRENT): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    device_class="current",
                    domain="sensor",
                )
            ),
            # Selector for Power Usage (Watts/kW)
            vol.Required(CONF_POWER_USAGE): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    device_class="power",
                    domain="sensor",
                )
            ),
            # Dropdown for Phase Selection
            vol.Required(CONF_PHASES, default=1): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "1", "label": "Single Phase (1-Phase)"},
                        {"value": "3", "label": "Three Phase (3-Phase)"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)