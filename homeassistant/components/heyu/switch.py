"""
Support for X10 switches over heyu.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.heyu/
"""
import logging

import voluptuous as vol

from homeassistant.components import heyu
from homeassistant.const import (CONF_PLATFORM, CONF_NAME, CONF_ID, CONF_DEVICES)
from homeassistant.components.switch import (
    SwitchDevice, PLATFORM_SCHEMA)
import homeassistant.helpers.config_validation as cv

DEPENDENCIES = ['heyu']
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PLATFORM): heyu.DOMAIN,
    vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [
        {
            vol.Required(CONF_ID): cv.string,
            vol.Required(CONF_NAME): cv.string,
        }
    ]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the x10 Switch over heyu platform."""
    switches = config.get(CONF_DEVICES)
    add_devices([HeyuSwitch(
        hass, heyu.CONTROLLER, switch) for switch in switches])


class HeyuSwitch(SwitchDevice):
    """Representation of an X10 Switch."""

    def __init__(self, hass, ctrl, switch):
        """Initialize an X10 Switch."""
        self._controller = ctrl
        self._name = switch['name']
        self._id = switch['id']
        self._state = False

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        self._controller.x10_command('on ' + self._id)
        """Assume it worked, we get no feedback..."""
        self._state = True

    def turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        self._controller.x10_command('off ' + self._id)
        """Assume it worked, we get no feedback..."""
        self._state = False

    def update(self):
        """Fetch update state."""
        self._state = bool(self._controller.get_unit_status(self._id))

