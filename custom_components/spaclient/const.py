"""Constants for the Balboa Spa Client integration."""
from homeassistant.components.climate.const import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
)
from homeassistant.components.fan import SPEED_HIGH, SPEED_LOW, SPEED_OFF

CLIMATE_SUPPORTED_FANSTATES = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
CLIMATE_SUPPORTED_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
CONF_SYNC_TIME = "sync_time"
DEFAULT_SYNC_TIME = False
DOMAIN = "balboa"
FAN_SUPPORTED_SPEEDS = [SPEED_OFF, SPEED_LOW, SPEED_HIGH]
PLATFORMS = ["climate", "switch", "binary_sensor", "fan", "sensor"]
SPA = "spa"
UNSUB = "unsub"

AUX = "Aux"
CIRC_PUMP = "Circ Pump"
CLIMATE = "Climate"
FILTER = "Filter"
LIGHT = "Light"
MISTER = "Mister"
PUMP = "Pump"
TEMP_RANGE = "Temp Range"
