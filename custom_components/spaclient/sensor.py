"""Support for Balboa Spa sensors."""
import logging

from homeassistant.const import CONF_NAME

from . import BalboaEntity
from .const import DOMAIN, SPA

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa's sensors."""
    spa = hass.data[DOMAIN][entry.entry_id][SPA]
    device = entry.data[CONF_NAME]
    devs = []

    devs.append(BalboaSpaSensor(hass, spa, device, "Time"))
    async_add_entities(devs, True)


class BalboaSpaSensor(BalboaEntity):
    """Representation of a Balboa Spa sensor device."""

    @property
    def state(self):
        """Return the value of the sensor."""
        return f'{self._client.time_hour:02d}:{self._client.time_minute:02d}'

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return 'mdi:clock'
