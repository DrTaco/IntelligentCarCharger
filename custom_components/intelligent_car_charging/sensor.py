from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import PERCENTAGE
from .const import DOMAIN, CONF_CHARGE_CURRENT, CONF_PHASES


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    async_add_entities([SolarEfficiencySensor(hass, entry)])


class SolarEfficiencySensor(SensorEntity):
    """Calculates what % of charging is coming from solar."""

    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_icon = "mdi:brightness-percent"
        self._attr_name = "Solar Charge Efficiency"
        self._attr_unique_id = f"{entry.entry_id}_solar_efficiency"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = "measurement"

    @property
    def native_value(self):
        """Return the efficiency percentage."""
        data = self._hass.data[DOMAIN].get(self._entry.entry_id)
        if not data or not data["is_charging"]:
            return 0

        # 1. Calculate how much power the car is currently pulling
        current_id = self._entry.data[CONF_CHARGE_CURRENT]
        phases = int(self._entry.data.get(CONF_PHASES, 1))

        current_state = self._hass.states.get(current_id)
        if not current_state:
            return 0

        car_amps = float(current_state.state)
        total_car_power = car_amps * 230 * phases

        # 2. Get the smoothed house power (P1 Meter)
        # If negative, we have solar excess. If positive, we are importing.
        house_power = data["smoothed_power"]

        # 3. Calculate the Solar portion
        # If house_power is -500, we have 500W extra solar.
        # If house_power is 200, we are using all solar + 200W grid.
        available_solar_for_car = total_car_power - max(0, house_power)

        if total_car_power <= 0:
            return 0

        efficiency = (available_solar_for_car / total_car_power) * 100
        return round(max(0, min(100, efficiency)), 1)

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry.entry_id)}, "name": "Intelligent Car Charging"}