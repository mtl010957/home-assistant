"""
Support for X10 lights over heyu.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.heyu/
"""
import logging
from subprocess import check_output, CalledProcessError, STDOUT

import voluptuous as vol

from homeassistant.components import heyu
from homeassistant.const import (CONF_NAME, CONF_ID, CONF_DEVICES)
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv

DEPENDENCIES = ['heyu']
_LOGGER = logging.getLogger(__name__)

SUPPORT_HEYU = SUPPORT_BRIGHTNESS

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [
        {
            vol.Required(CONF_ID): cv.string,
            vol.Required(CONF_NAME): cv.string,
        }
    ]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the x10 Light over heyu platform."""
    lights = config.get(CONF_DEVICES)
    add_devices([HeyuLight(
        hass, heyu.CONTROLLER, light) for light in lights])


class HeyuLight(Light):
    """Representation of an X10 Light."""

    def __init__(self, hass, ctrl, light):
        """Initialize an X10 Light."""
        self._controller = ctrl
        self._name = light['name']
        self._id = light['id']
        self._brightness = 0
        self._state = False

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_HEYU

    def turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        dim = int((255.00 - self._brightness) / 255.00 * 22.00)
        self._state = True
        """Heyu obdim only works for lamp modules, if we get an exception it's likely an appliance module so just turn in on"""
        try:
            self._controller.x10_command('obdim ' + self._id + ' ' + str(dim))
        except:
            self._controller.x10_command('on ' + self._id)
            _LOGGER.warning("Heyu returned error on dimming command, falling back to plain on command.")

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._controller.x10_command('off ' + self._id)
        self._state = False

    def update(self):
        """Fetch update state."""
        self._state = bool(self._controller.get_unit_status(self._id))
