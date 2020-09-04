"""Support for Balboa Spa Pumps."""
import logging

from homeassistant.components.fan import (
    SPEED_LOW,
    SPEED_OFF,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import CONF_NAME

from . import BalboaEntity
from .const import DOMAIN as BALBOA_DOMAIN, FAN_SUPPORTED_SPEEDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa's pumps as FAN entities."""
    spa = hass.data[BALBOA_DOMAIN][entry.entry_id]
    device = entry.data[CONF_NAME]
    devs = []

    for num, value in enumerate(spa.pump_array, 1):
        if value:
            devs.append(BalboaSpaPump(hass, spa, device, num, value))

    async_add_entities(devs, True)


class BalboaSpaPump(BalboaEntity, FanEntity):
    """Representation of a Balboa Spa pump device."""

    def __init__(self, hass, client, device, num, states):
        """Initialize the switch."""
        super().__init__(hass, client, device, 'Pump', num)
        self._speed_list = FAN_SUPPORTED_SPEEDS if states > 1 else None
        self._supported_features = SUPPORT_SET_SPEED if states > 1 else 0

    async def async_set_speed(self, speed: str) -> None:
        """Set speed of pump."""
        setto = FAN_SUPPORTED_SPEEDS.index(speed)
        _LOGGER.debug(f'set {self.name} speed to {speed}')
        await self._client.change_pump(self._num-1, setto)

    async def async_turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on pump."""
        if speed is None:
            speed = SPEED_LOW
        await self.async_set_speed(speed)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off pump."""
        await self.async_set_speed(SPEED_OFF)

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    @property
    def speed(self) -> str:
        """Return the current speed."""
        pstate = self._client.get_pump(self._num-1)
        _LOGGER.debug(f'{self.name} speed is {FAN_SUPPORTED_SPEEDS[pstate]}')
        if pstate >= len(FAN_SUPPORTED_SPEEDS) or pstate < 0:
            return SPEED_OFF
        return FAN_SUPPORTED_SPEEDS[pstate]

    @property
    def is_on(self):
        """Return true if the pump is on."""
        pstate = self._client.get_pump(self._num-1)
        return bool(pstate)

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:hydro-power"
