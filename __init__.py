"""The Balboa Spa integration."""
import asyncio
import logging
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from pybalboa import BalboaSpaWifi
from homeassistant.const import (CONF_HOST, CONF_NAME)
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, BALBOA_PLATFORMS

_LOGGER = logging.getLogger(__name__)

BALBOA_CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [BALBOA_CONFIG_SCHEMA])
    }, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: dict):
    """Configure the Balboa Spa component using flow only."""
    if DOMAIN in config:
        for entry in config[DOMAIN]:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=entry
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Balboa Spa from a config entry."""
    host = entry.data[CONF_HOST]

    spa = BalboaSpaWifi(host)
    hass.data[DOMAIN][entry.entry_id] = spa

    connected = await spa.connect()
    if not connected:
        _LOGGER.error("Failed to connect to spa at %s", host)
        return False

    # Start listening to the spa babble
    # The spa basically spams anyone who connects to the correct port with
    # messages.  Pybalboa simply updates it's internal states, and you can
    # more or less ask for data whenever you want.
    hass.async_create_task(spa.listen())
    hass.async_create_task(spa.check_connection_status())

    # Now that the spa is being listened to, wait for the configuration to load
    await spa.spa_configured()

    # At this point we have a configured spa.
    forward_setup = hass.config_entries.async_forward_entry_setup
    for component in BALBOA_PLATFORMS:
        hass.async_create_task(forward_setup(entry, component))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    spa = hass.data[DOMAIN][entry.entry_id]
    spa.disconnect()

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in BALBOA_PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
