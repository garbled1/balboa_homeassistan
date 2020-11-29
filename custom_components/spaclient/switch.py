"""Support for Balboa Spa switches."""
import logging

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity

from . import BalboaEntity
from .const import AUX, DOMAIN, LIGHT, MISTER, SPA, TEMP_RANGE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa switch devices."""
    spa = hass.data[DOMAIN][entry.entry_id][SPA]
    devs = []

    devs.append(BalboaSpaSwitch(hass, entry, TEMP_RANGE))
    for num, value in enumerate(spa.light_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(
                hass, entry, LIGHT, num))
    for num, value in enumerate(spa.aux_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(
                hass, entry, AUX, num))
    if spa.have_mister():
        devs.append(BalboaSpaSwitch(hass, entry, MISTER))

    async_add_entities(devs, True)


class BalboaSpaSwitch(BalboaEntity, SwitchEntity):
    """Representation of a Balboa Spa switch device."""

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        if self._type == AUX:
            return self._client.get_aux(self._num-1)
        elif self._type == LIGHT:
            return self._client.get_light(self._num-1)
        elif self._type == MISTER:
            return self._client.get_mister()
        elif self._type == TEMP_RANGE:
            return self._client.get_temprange()

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_SWITCH

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._type == LIGHT:
            return "mdi:lightbulb" if self.is_on else "mdi:lightbulb-off"
        elif self._type == MISTER:
            return "mdi:weather-fog"
        elif self._type == TEMP_RANGE:
            return "mdi:thermometer-plus" if self.is_on else "mdi:thermometer-minus"
        else:
            return "mdi:flash"

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        if self._type == AUX:
            return await self._client.change_aux(self._num-1, self._client.OFF)
        elif self._type == LIGHT:
            return await self._client.change_light(self._num-1, self._client.OFF)
        elif self._type == MISTER:
            return await self._client.change_mister(self._client.OFF)
        elif self._type == TEMP_RANGE:
            return await self._client.change_temprange(self._client.TEMPRANGE_LOW)

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        if self._type == AUX:
            return await self._client.change_aux(self._num-1, self._client.ON)
        elif self._type == LIGHT:
            return await self._client.change_light(self._num-1, self._client.ON)
        elif self._type == MISTER:
            return self._client.change_mister(self._client.ON)
        elif self._type == TEMP_RANGE:
            return await self._client.change_temprange(self._client.TEMPRANGE_HIGH)
