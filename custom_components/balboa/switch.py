"""Support for Balboa Spa switches."""
import logging

from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchDevice
from homeassistant.const import CONF_NAME

from . import BalboaEntity
from .const import DOMAIN as BALBOA_DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa switch devices."""
    spa = hass.data[BALBOA_DOMAIN][entry.entry_id]
    device = entry.data[CONF_NAME]
    devs = []

    for num, value in enumerate(spa.light_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(
                hass, spa, device, 'Light', num))
    for num, value in enumerate(spa.aux_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(
                hass, spa, device, 'Aux', num))
    if spa.have_mister():
        devs.append(BalboaSpaSwitch(hass, spa, device, "Mister"))

    async_add_entities(devs, True)


class BalboaSpaSwitch(BalboaEntity, SwitchDevice):
    """Representation of a Balboa Spa switch device."""

    def __init__(self, hass, client, device, entity, num=None):
        """Initialize the switch."""
        super().__init__(hass, client, device, entity, num)
        self.getdata = {
            'Light': client.get_light,
            'Aux': client.get_aux,
        }
        self.switch_change = {
            'Light': self._client.change_light,
            'Aux': self._client.change_aux,
        }

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        if self._entity == 'Mister':
            return self._client.get_mister()
        return self.getdata[self._entity](self._num-1)

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_SWITCH

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._entity == 'Mister':
            return "mdi:weather-fog"
        if self._entity == 'Light':
            return "mdi:lightbulb"
        return "mdi:flash"

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        if self._entity == 'Mister':
            return self._client.change_mister(self._client.OFF)
        await self.switch_change[self._entity](self._num-1, self._client.OFF)

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        if self._entity == 'Mister':
            return self._client.change_mister(self._client.ON)
        await self.switch_change[self._entity](self._num-1, self._client.ON)
