"""Support for Balboa Spa Pumps."""
from homeassistant.components.fan import (
    SUPPORT_PRESET_MODE,
    FanEntity,
)

from . import BalboaEntity
from .const import _LOGGER, DOMAIN, FAN_PRESET_MODE_OFF, FAN_PRESET_MODE_LOW, FAN_SUPPORTED_PRESET_MODES, PUMP, SPA
from typing import Any, final

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the spa's pumps as FAN entities."""
    spa = hass.data[DOMAIN][entry.entry_id][SPA]
    devs = []

    for key, value in enumerate(spa.pump_array, 1):
        if value:
            devs.append(BalboaSpaPump(hass, entry, key, value))

    async_add_entities(devs, True)


class BalboaSpaPump(BalboaEntity, FanEntity):
    """Representation of a Balboa Spa pump device."""

    def __init__(self, hass, entry, key, states):
        """Initialize the pump."""
        super().__init__(hass, entry, PUMP, key)
        self._preset_modes = FAN_SUPPORTED_PRESET_MODES if states > 1 else None
        self._supported_features = SUPPORT_PRESET_MODE if states > 1 else 0

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set speed of pump."""
        setto = FAN_SUPPORTED_PRESET_MODES.index(preset_mode)
        _LOGGER.debug(f"set {self.name} speed to {preset_mode}")
        await self._client.change_pump(self._num - 1, setto)

    # async def async_turn_on(self, preset_mode: str = None, **kwargs) -> None:
    #     """Turn on pump."""
    #     if preset_mode is None:
    #         preset_mode = FAN_PRESET_MODE_LOW
    #     await self.async_set_preset_mode(preset_mode)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
         """Turn on pump."""
         if preset_mode is None:
             preset_mode = FAN_PRESET_MODE_LOW
         await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off pump."""
        await self.async_set_preset_mode(FAN_PRESET_MODE_OFF)

    @property
    def preset_modes(self) -> list:
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    @property
    def preset_mode(self) -> str:
        """Get the active preset mode."""
        pstate = self._client.get_pump(self._num - 1)
        _LOGGER.debug(f"{self.name} speed is {FAN_SUPPORTED_PRESET_MODES[pstate]}")
        if pstate >= len(FAN_SUPPORTED_PRESET_MODES) or pstate < 0:
            return FAN_PRESET_MODE_OFF
        return FAN_SUPPORTED_PRESET_MODES[pstate]

    @property
    def is_on(self):
        """Return true if the pump is on."""
        pstate = self._client.get_pump(self._num - 1)
        return bool(pstate)

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:hydro-power"