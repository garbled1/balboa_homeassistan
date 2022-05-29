[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

# Balboa Spa Client integration for home-assistant
Home assistant integration for a spa equipped with a Balboa BP system and a
bwa™ Wi-Fi Module (50350).

## Configuration

There is a config flow for the spa.  After installing, 
go to integrations in HACS, hit + to setup a new integration, search for "Balboa Spa Client",
select that, and add the IP address or hostname of your spa's wifi adapter.

If you have a blower, it will be listed as a "fan" in the climate device for
the spa.  Currently the code assumes you have a 3-speed blower, if you only
have a 1-speed, only use LOW and OFF.

## Screenshots

![Screenshots](Screenshot_spa.png)

## Related Projects

* https://github.com/garbled1/pybalboa - Python library for local spa control
* https://github.com/plmilord/Hass.io-custom-component-spaclient - Another HASS custom component (and source of "spaclient" logos)
* https://github.com/ccutrer/balboa_worldwide_app - Fountain of knowledge for most of the messages sent from the spa wifi module
* https://github.com/natekspencer/BwaSpaManager - A SmartThings cloud-based solution
