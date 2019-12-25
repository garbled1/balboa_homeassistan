"""Support for Balboa Spa Wifi adaptor."""
import logging
from typing import List

from pybalboa import BalboaSpaWifi
from .const import CLIMATE_SUPPORTED_MODES, DOMAIN as BALBOA_DOMAIN
from . import BalboaEntity

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateDevice
from homeassistant.components.climate.const import (
    DOMAIN,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_PRESET_MODE,
)
from homeassistant.const import (
    CONF_NAME,
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up of the spa is done through async_setup_entry."""
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    spa = hass.data[BALBOA_DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    devs = []
    devs.append(BalboaSpaClimate(hass, spa, name))
    async_add_entities(devs, True)


class BalboaSpaClimate(BalboaEntity, ClimateDevice):
    """Representation of a Balboa Spa."""

    @property
    def supported_features(self):
        """Return the list of supported features."""
        _LOGGER.debug("features")
        features = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

        return features

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of supported HVAC modes."""
        _LOGGER.debug("hvac_modes")
        return CLIMATE_SUPPORTED_MODES

    @property
    def hvac_mode(self) -> str:
        """Return the current HVAC mode."""
        mode = self._client.get_heatmode()
        if mode == self._client.HEATMODE_READY:
            return HVAC_MODE_HEAT
        elif mode == self._client.HEATMODE_RNR:
            return HVAC_MODE_AUTO
        return HVAC_MODE_OFF

    @property
    def hvac_action(self) -> str:
        """Return the current operation mode."""
        state = self._client.get_heatstate()
        if state == self._client.ON:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def name(self):
        """Return the name of the spa."""
        _LOGGER.debug("name")
        return f'{self._name}'

    @property
    def precision(self):
        """Return the precision of the system.

        Balboa spas return data in C or F depending on how the display is set,
        because ultimately, we are just reading the display.
        In C, we have half-degree accuracy, in F, whole degree.
        """
        _LOGGER.debug("prec")
        tscale = self._client.get_tempscale()
        if tscale == self._client.TSCALE_C:
            return PRECISION_HALVES
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return the unit of measurement, as defined by the API."""
        _LOGGER.debug("Tu")
        tscale = self._client.get_tempscale()
        if tscale == self._client.TSCALE_C:
            return TEMP_CELSIUS
        return TEMP_FAHRENHEIT

    @property
    def current_temperature(self):
        """Return the current temperature."""
        _LOGGER.debug("curtem")
        return self._client.get_curtemp()

    @property
    def target_temperature(self):
        """Return the target temperature we try to reach."""
        _LOGGER.debug("tartem = %f", self._client.curtemp)
        _LOGGER.debug("self_client = %s", str(self._client))
        return self._client.get_settemp()

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature supported by the spa."""
        _LOGGER.debug("asked for mintemp")
        trange = self._client.get_temprange()
        scale = self._client.get_tempscale()
        xx = self._client.temprange
        _LOGGER.debug("trange = %d scale = %d xx=%d", trange, scale, xx)
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
        _LOGGER.debug("settemp")
        await self._client.send_temp_change(int(kwargs[ATTR_TEMPERATURE]))

    async def async_set_preset_mode(self, preset_mode) -> None:
        """Set new preset mode."""
        modelist = self._client.get_heatmode_stringlist()
        if preset_mode in modelist:
            await self._client.change_heatmode(modelist.index(preset_mode))
