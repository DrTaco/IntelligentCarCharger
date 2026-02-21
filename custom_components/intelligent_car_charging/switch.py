from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    # We create one switch for this config entry
    async_add_entities([IntelligentChargingSwitch(entry)])

class IntelligentChargingSwitch(SwitchEntity):
    """Representation of the Charging Logic Switch."""

    def __init__(self, entry):
        self._entry = entry
        self._attr_icon = "mdi:ev-station"
        self._attr_name = "Intelligent Charging State"
        self._attr_unique_id = f"{entry.entry_id}_charger_switch"
        self._attr_is_on = False  # Default state

    @property
    def device_info(self):
        """Link this switch to the integration 'Device'."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Intelligent Car Charging",
        }

    async def async_turn_on(self, **kwargs):
        """Turn the intelligent logic on."""
        self._attr_is_on = True
        self.async_write_ha_state()
        # Trigger your charging logic here

    async def async_turn_off(self, **kwargs):
        """Turn the intelligent logic off."""
        self._attr_is_on = False
        self.async_write_ha_state()
        # Stop your charging logic here