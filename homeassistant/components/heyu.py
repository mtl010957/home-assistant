"""
Support for CM11A/CM17A X10 Controller using heyu command.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/heyu/
"""
import logging
from subprocess import check_output, CalledProcessError, STDOUT

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP)
from subprocess import check_output
from homeassistant.const import (CONF_ID)

_LOGGER = logging.getLogger(__name__)

CONTROLLER = None

DOMAIN = 'heyu'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_ID, default=''): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the heyu component."""
    conf = config[DOMAIN]
    id = conf.get(CONF_ID)

    global CONTROLLER
    try:
        CONTROLLER = HeyuCtrl(id)
    except Exception:
        _LOGGER.exception("Heyu platform configuration error.")
        return False

    return True


class HeyuCtrl(object):
    """Heyu controller."""

    def __init__(self, id):
        """Initialize a Heyu controller."""
        super(HeyuCtrl, self).__init__()
        self._id = id

    @property
    def id(self):
        """Return the id of this CM10 when multiple devices are configured for heyu."""
        return self._id

    def x10_command(self, command):
        """Send a raw command to heyu.

        :param str command: The command to send to heyu
        """
        """Execute X10 command and check output."""
        if (self._id.__eq__('')):
            return check_output(['heyu'] + command.split(' '), stderr=STDOUT)
        else:
            return check_output(['heyu', self._id] + command.split(' '), stderr=STDOUT)

    def get_unit_status(self, code):
        """Get on/off status for given unit.
        
        :param str code: The unit code to get status from.
        :rtype int
        """
        output = check_output('heyu onstate ' + self._id + ' ' + code, shell=True)
        return int(output.decode('utf-8')[0])