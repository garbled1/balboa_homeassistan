"""Support for Balboa Spa binary sensors."""
import logging

from homeassistant.components.binary_sensor import (DEVICE_CLASS_MOVING,
                                                    BinarySensorEntity)
from homeassistant.const import CONF_NAME

from . import BalboaEntity
from .const import DOMAIN, SPA

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa's binary sensors."""
    spa = hass.data[DOMAIN][entry.entry_id][SPA]
    device = entry.data[CONF_NAME]
    devs = []

    devs.append(BalboaSpaBinarySensor(hass, spa, device, "Filter", 1))
    devs.append(BalboaSpaBinarySensor(hass, spa, device, "Filter", 2))
    if spa.have_circ_pump():
        devs.append(BalboaSpaBinarySensor(hass, spa, device, "Circ Pump"))
    async_add_entities(devs, True)


class BalboaSpaBinarySensor(BalboaEntity, BinarySensorEntity):
    """Representation of a Balboa Spa binary sensor device."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if self._entity == "Circ Pump":
            return self._client.get_circ_pump()
        if self._entity == "Filter":
            fmode = self._client.get_filtermode()
            if fmode == self._client.FILTER_OFF:
                return False
            if self._num == 1 and fmode != self._client.FILTER_2:
                return True
            if self._num == 2 and fmode >= self._client.FILTER_2:
                return True
            return False
        return False

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_MOVING

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._entity == "Circ Pump":
            return "mdi:hydro-power"
        return "mdi:autorenew"
