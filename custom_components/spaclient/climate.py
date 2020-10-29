"""Support for Balboa Spa Wifi adaptor."""
import logging
from typing import List
import math

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_AUTO,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_NAME,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

# from pybalboa import BalboaSpaWifi
from . import BalboaEntity
from .const import (
    CLIMATE_SUPPORTED_FANSTATES,
    CLIMATE_SUPPORTED_MODES,
    DOMAIN as BALBOA_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa climate device."""
    spa = hass.data[BALBOA_DOMAIN][entry.entry_id]
    device = entry.data[CONF_NAME]
    async_add_entities([BalboaSpaClimate(hass, spa, device, "Climate")], True)


class BalboaSpaClimate(BalboaEntity, ClimateEntity):
    """Representation of a Balboa Spa Climate device."""

    @property
    def supported_features(self):
        """Return the list of supported features."""
        features = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

        if self._client.have_blower():
            features |= SUPPORT_FAN_MODE

        return features

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of supported HVAC modes."""
        return CLIMATE_SUPPORTED_MODES

    @property
    def hvac_mode(self) -> str:
        """Return the current HVAC mode."""
        mode = self._client.get_heatmode()
        if mode == self._client.HEATMODE_READY or mode == self._client.HEATMODE_RNR:
            return HVAC_MODE_HEAT
        return HVAC_MODE_AUTO

    @property
    def hvac_action(self) -> str:
        """Return the current operation mode."""
        state = self._client.get_heatstate()
        if state >= self._client.ON:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def fan_modes(self) -> List[str]:
        """Return the list of available fan modes."""
        return CLIMATE_SUPPORTED_FANSTATES

    @property
    def fan_mode(self) -> str:
        """Return the current fan mode."""
        fanmode = self._client.get_blower()
        if fanmode is None:
            return FAN_OFF
        if fanmode == self._client.BLOWER_OFF:
            return FAN_OFF
        if fanmode == self._client.BLOWER_LOW:
            return FAN_LOW
        if fanmode == self._client.BLOWER_MEDIUM:
            return FAN_MEDIUM
        if fanmode == self._client.BLOWER_HIGH:
            return FAN_HIGH

    @property
    def icon(self):
        return "mdi:hot-tub"

    @property
    def precision(self) -> float:
        """Return the precision of the system."""
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
            return PRECISION_HALVES
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return the unit of measurement, as defined by the API."""
        tscale = self._client.get_tempscale()
        if tscale == self._client.TSCALE_C:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._client.get_curtemp()

    @property
    def target_temperature(self):
        """Return the target temperature we try to reach."""
        return self._client.get_settemp()

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature supported by the spa."""
        trange = self._client.get_temprange()
        scale = self._client.get_tempscale()
        return self._client.tmin[trange][scale]

    @property
    def max_temp(self) -> int:
        """Return the minimum temperature supported by the spa."""
        trange = self._client.get_temprange()
        scale = self._client.get_tempscale()
        return self._client.tmax[trange][scale]

    @property
    def preset_modes(self):
        """Return the valid preset modes."""
        return self._client.get_heatmode_stringlist()

    @property
    def preset_mode(self):
        """Return current preset mode."""
        return self._client.get_heatmode(True)

    async def async_set_temperature(self, **kwargs):
        """Set a new target temperature."""
        temperature = kwargs[ATTR_TEMPERATURE]
        spa_unit = self._client.get_tempscale()
        if spa_unit != self.get_temp_unit():
            if spa_unit == self._client.TSCALE_F:
                temperature = math.floor(temperature + 0.5)
            else:
                temperature = .5 * round(temperature / .5)
        await self._client.send_temp_change(temperature)

    async def async_set_preset_mode(self, preset_mode) -> None:
        """Set new preset mode."""
        modelist = self._client.get_heatmode_stringlist()
        if preset_mode in modelist:
            await self._client.change_heatmode(modelist.index(preset_mode))

    async def async_set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        if fan_mode == FAN_OFF:
            await self._client.change_blower(self._client.BLOWER_OFF)
        elif fan_mode == FAN_LOW:
            await self._client.change_blower(self._client.BLOWER_LOW)
        elif fan_mode == FAN_MEDIUM:
            await self._client.change_blower(self._client.BLOWER_MEDIUM)
        elif fan_mode == FAN_HIGH:
            await self._client.change_blower(self._client.BLOWER_HIGH)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode.

        AUTO = REST
        HEAT = READY
        """
        if hvac_mode == HVAC_MODE_HEAT:
            await self._client.change_heatmode(self._client.HEATMODE_READY)
        else:
            await self._client.change_heatmode(self._client.HEATMODE_REST)

    def get_temp_unit(self):
        """Return the balboa equivalent temperature unit of the system."""
        if self.hass.config.units.temperature_unit == TEMP_CELSIUS:
            return self._client.TSCALE_C
        return self._client.TSCALE_F