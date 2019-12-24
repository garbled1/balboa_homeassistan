"""Support for Balboa Spa Wifi adaptor."""
import logging

from pybalboa import BalboaSpaWifi
from .const import DOMAIN

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateDevice
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    CONF_NAME,
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
    TEMP_FARENHEIT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up of the spa is done through async_setup_entry."""
    pass


async def async_setup_entry(hass, entry, async_add_entities):
    spa = hass.data[DOMAIN][entry.entry_id]
    name = entry.data[CONF_NAME]
    devs = []
    devs.append(BalboaSpa(spa, name))
    async_add_entities(devs, True)


class BalboaSpa(ClimateDevice):
    """Representation of a Balboa Spa."""

    def __init__(self, client, name):
        """Initialize the spa."""
        self._client = client
        self._name = name

    def update(self):
        """Update the data from the spa."""
        pass

    @property
    def supported_features(self):
        """Return the list of supported features."""
        features = SUPPORT_TARGET_TEMPERATURE

        return features

    @property
    def name(self):
        """Return the name of the spa."""
        return f'{self._name}'

    @property
    def unique_id(self):
        """Set unique_id for sensor."""
        return f'{self._name}-{self._client.get_macaddr()}'

    @property
    def precision(self):
        """Return the precision of the system.

        Balboa spas return data in C or F depending on how the display is set,
        because ultimately, we are just reading the display.
        In C, we have half-degree accuracy, in F, whole degree.
        """
        tscale = self._client.get_tempscale()
        if tscale == self._client.TSCALE_C:
            return PRECISION_HALVES
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return the unit of measurement, as defined by the API."""
        tscale = self._client.get_tempscale()
        if tscale == self._client.TSCALE_C:
            return TEMP_CELSIUS
        return TEMP_FARENHEIT

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._client.get_curtemp()

    @property
    def target_temperature(self):
        """Return the target temperature we try to reach."""
        return self._client.get_settemp()

    async def async_set_temperature(self, **kwargs):
        """Set a new target temperature."""
        await self._client.send_temp_change()
