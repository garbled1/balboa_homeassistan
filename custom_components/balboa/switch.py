"""Support for Balboa Spa switches."""
from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity

from . import BalboaEntity
from .const import _LOGGER, AUX, DOMAIN, LIGHT, MISTER, SPA, TEMP_RANGE

CHANGE_FUNCTION = "change"
GET_FUNCTION = "get"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa switch devices."""
    spa = hass.data[DOMAIN][entry.entry_id][SPA]
    devs = []

    devs.append(BalboaSpaSwitch(hass, entry, TEMP_RANGE))
    for num, value in enumerate(spa.light_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(hass, entry, LIGHT, num))
    for num, value in enumerate(spa.aux_array, 1):
        if value:
            devs.append(BalboaSpaSwitch(hass, entry, AUX, num))
    if spa.have_mister():
        devs.append(BalboaSpaSwitch(hass, entry, MISTER))

    async_add_entities(devs, True)


class BalboaSpaSwitch(BalboaEntity, SwitchEntity):
    """Representation of a Balboa Spa switch device."""

    @property
    def type_functions(self):
        """Get the appropriate function for the type of switch"""
        return {
            AUX: {
                GET_FUNCTION: self._client.get_aux,
                CHANGE_FUNCTION: self._client.change_aux,
            },
            LIGHT: {
                GET_FUNCTION: self._client.get_light,
                CHANGE_FUNCTION: self._client.change_light,
            },
            MISTER: {
                GET_FUNCTION: self._client.get_mister,
                CHANGE_FUNCTION: self._client.change_mister,
            },
            TEMP_RANGE: {
                GET_FUNCTION: self._client.get_temprange,
                CHANGE_FUNCTION: self._client.change_temprange,
            },
        }

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        key = self._num - 1 if self._num else None
        return self.type_functions[self._type][GET_FUNCTION](key)

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
        new_state = (
            self._client.TEMPRANGE_LOW if self._type == TEMP_RANGE else self._client.OFF
        )
        return await self.change_switch(new_state)

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        new_state = (
            self._client.TEMPRANGE_HIGH if self._type == TEMP_RANGE else self._client.ON
        )
        return await self.change_switch(new_state)

    async def change_switch(self, new_state=None):
        key = self._num - 1 if self._num else None
        return await self.type_functions[self._type][CHANGE_FUNCTION](
            *[v for v in [key, new_state] if v is not None]
        )
