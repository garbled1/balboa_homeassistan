"""Constants for the Balboa Spa integration."""
from homeassistant.components.climate.const import HVAC_MODE_HEAT, HVAC_MODE_OFF

DOMAIN = "balboa"
BALBOA_PLATFORMS = ["climate"]
CLIMATE_SUPPORTED_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
