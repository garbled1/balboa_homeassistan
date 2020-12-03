"""Support for Balboa Spa sensors."""
import logging

from . import BalboaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa's sensors."""
    async_add_entities([BalboaSpaSensor(hass, entry, "Time")], True)


class BalboaSpaSensor(BalboaEntity):
    """Representation of a Balboa Spa sensor device."""

    @property
    def state(self):
        """Return the value of the sensor."""
        return f"{self._client.time_hour:02d}:{self._client.time_minute:02d}"

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:clock"
