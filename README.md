# 🚗 Intelligent Car Charging for Home Assistant

An intelligent, solar-aware EV charging integration for Home Assistant. This component monitors your house's power usage (P1 Meter) and automatically adjusts your car's charging current to maximize the use of excess solar energy.

![Logo](https://raw.githubusercontent.com/DRTaco/IntelligentCarCharger/main/custom_components/icons/logo.png)

## ✨ Features
* **Solar Excess Tracking:** Automatically starts charging when solar production exceeds 500W.
* **Phase-Aware Logic:** Supports both 1-phase and 3-phase electrical systems with accurate power-to-current calculations.
* **Smart Smoothing:** Uses a Simple Moving Average (SMA) to prevent the charger from reacting to temporary power spikes (e.g., turning on a kettle).
* **Hysteresis Timers:** * **2-minute delay** before starting to ensure solar production is stable.
    * **15-minute delay** before stopping to prevent rapid on/off cycles during cloudy periods.
* **Real-time Efficiency:** Provides a "Solar Charge Efficiency" sensor to show exactly what % of your charge is coming from the sun.

## 🛠 Installation

### Manual Installation
1.  Download the `intelligent_car_charging` folder.
2.  Copy the folder into your Home Assistant `custom_components/` directory.
3.  Restart Home Assistant.
4.  In the Home Assistant UI, go to **Settings > Devices & Services**.
5.  Click **Add Integration** and search for "Intelligent Car Charging".

## ⚙️ Configuration
During the setup flow, you will be asked to select:
* **Car Battery Sensor:** The sensor providing the car's state of charge (%).
* **Charging Current Entity:** The `number` or `input_number` used to control your car's Amps.
* **P1 Power Meter:** Your house's main power sensor (Watts). *Negative values are assumed to be solar export.*
* **Cable Connected Sensor:** A binary sensor that is `on` when the car is plugged in.
* **Electrical Phases:** Whether your charger uses 1 or 3 phases.

## 📊 Entities Created
| Entity | Type | Description |
| :--- | :--- | :--- |
| `switch.intelligent_charging_state` | Switch | Master toggle to enable/disable the automation logic. |
| `sensor.solar_charge_efficiency` | Sensor | Displays 0-100% solar utilization. |

## 🧠 How the Logic Works
1.  **Stable Solar:** If the cable is plugged in and smoothed export is > 500W for 2 minutes, the charger turns on at 1A (or your car's minimum).
2.  **Amperage Scaling:** * If export > (230W * phases), current increases by 1A.
    * If grid import > 100W, current decreases by 1A.
3.  **Sunset/Cloud Logic:** If the house imports power for more than 15 continuous minutes, charging is stopped to preserve battery/grid costs.

## 🤝 Contributing
Feel free to open issues or pull requests if you have suggestions for improving the smoothing algorithm or adding new features!