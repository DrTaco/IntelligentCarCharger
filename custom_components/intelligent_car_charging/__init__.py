import logging
from collections import deque
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.const import STATE_ON, Platform

from .const import (
    DOMAIN,
    CONF_BATTERY_ENTITY,
    CONF_CHARGE_CURRENT,
    CONF_POWER_USAGE,
    CONF_CABLE_CONNECTED,
    CONF_PHASES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intelligent Car Charging from a config entry."""

    # 1. Initialize data storage for coordination between platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "smoothed_power": 0.0,
        "is_charging": False,
        "active_timers": {"turn_on": None, "turn_off": None}
    }

    # Extract config data
    power_id = entry.data[CONF_POWER_USAGE]
    current_id = entry.data[CONF_CHARGE_CURRENT]
    cable_id = entry.data[CONF_CABLE_CONNECTED]
    battery_id = entry.data[CONF_BATTERY_ENTITY]
    phases = int(entry.data.get(CONF_PHASES, 1))

    # Internal state for smoothing
    power_buffer = deque(maxlen=10)
    # The unique ID for the switch we created in switch.py
    switch_entity_id = f"switch.intelligent_charging_state"

    async def apply_charge_logic(smoothed_power):
        """Adjusts the charge current (Amps) based on solar excess."""
        # Only adjust if the master switch is ON
        if not hass.states.is_state(switch_entity_id, STATE_ON):
            return

        current_state = hass.states.get(current_id)
        if not current_state:
            return

        try:
            actual_amps = int(float(current_state.state))
            wattage_per_amp = 230 * phases

            # Logic: If solar excess > 1.2x the step, increase Amps
            if smoothed_power < -(wattage_per_amp + 100):
                new_amps = actual_amps + 1
            # If we are importing more than 100W from grid, decrease Amps
            elif smoothed_power > 100 and actual_amps > 1:
                new_amps = actual_amps - 1
            else:
                new_amps = actual_amps

            if new_amps != actual_amps:
                _LOGGER.debug("Adjusting charge current to %s A", new_amps)
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": current_id, "value": new_amps}
                )
        except (ValueError, TypeError):
            pass

    async def monitor_power_update(event):
        """The main observer: manages smoothing, timers, and coordination."""
        new_state = event.data.get("new_state")
        if not new_state or new_state.state in ("unknown", "unavailable"):
            return

        try:
            # Update smoothing
            power_buffer.append(float(new_state.state))
            smoothed_power = sum(power_buffer) / len(power_buffer)

            # Update shared data for the Efficiency Sensor
            is_charging = hass.states.is_state(switch_entity_id, STATE_ON)
            hass.data[DOMAIN][entry.entry_id]["smoothed_power"] = smoothed_power
            hass.data[DOMAIN][entry.entry_id]["is_charging"] = is_charging

            cable_plugged = hass.states.is_state(cable_id, STATE_ON)
            batt_state = hass.states.get(battery_id)
            batt_level = float(batt_state.state) if batt_state else 100

            timers = hass.data[DOMAIN][entry.entry_id]["active_timers"]

            # TIMER: 2-MINUTE TURN ON (Solar < -500W, Cable In, Battery < 100%)
            if smoothed_power < -500 and cable_plugged and not is_charging and batt_level < 100:
                if timers["turn_on"] is None:
                    _LOGGER.info("Stable solar detected. Starting 2min countdown to start charging.")

                    async def turn_on_action(_):
                        await hass.services.async_call("switch", "turn_on", {"entity_id": switch_entity_id})
                        # Start at 1A (or 6A depending on car)
                        await hass.services.async_call("number", "set_value", {"entity_id": current_id, "value": 1})
                        timers["turn_on"] = None

                    timers["turn_on"] = async_call_later(hass, 120, turn_on_action)
            else:
                if timers["turn_on"]:
                    timers["turn_on"]()  # Cancel
                    timers["turn_on"] = None

            # TIMER: 15-MINUTE TURN OFF (Importing > 0W)
            if smoothed_power >= 0 and is_charging:
                if timers["turn_off"] is None:
                    _LOGGER.info("Grid import detected. Starting 15min countdown to stop charging.")

                    async def turn_off_action(_):
                        await hass.services.async_call("switch", "turn_off", {"entity_id": switch_entity_id})
                        timers["turn_off"] = None

                    timers["turn_off"] = async_call_later(hass, 900, turn_off_action)
            else:
                if timers["turn_off"]:
                    timers["turn_off"]()  # Cancel
                    timers["turn_off"] = None

            # Run Amp adjustment logic
            await apply_charge_logic(smoothed_power)

        except (ValueError, TypeError) as err:
            _LOGGER.error("Error in power monitoring: %s", err)

    # Register the listener
    entry.async_on_unload(
        async_track_state_change_event(hass, [power_id], monitor_power_update)
    )

    # Forward setup to Switch and Sensor platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)