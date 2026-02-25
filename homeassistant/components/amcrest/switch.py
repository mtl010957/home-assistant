"""Support for Amcrest Switches."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import CONF_NAME, CONF_SWITCHES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DATA_AMCREST, DEVICES

if TYPE_CHECKING:
    from . import AmcrestDevice

_LOGGER = logging.getLogger(__name__)

PRIVACY_MODE_KEY = "privacy_mode"

SWITCH_TYPES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key=PRIVACY_MODE_KEY,
        name="Privacy Mode",
        icon="mdi:eye-off",
    ),
)

SWITCH_KEYS: list[str] = [desc.key for desc in SWITCH_TYPES]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up amcrest platform switches."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DATA_AMCREST][DEVICES][name]
    switches = discovery_info[CONF_SWITCHES]
    async_add_entities(
        [
            AmcrestSwitch(name, device, description)
            for description in SWITCH_TYPES
            if description.key in switches
        ],
        True,
    )


class AmcrestSwitch(SwitchEntity):
    """Representation of an Amcrest Camera Switch."""

    def __init__(
        self,
        name: str,
        device: AmcrestDevice,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize switch."""
        self._api = device.api
        self.entity_description = entity_description
        self._channel = device.channel
        self._attr_name = f"{name} {entity_description.name}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._api.available

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_turn_switch(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_turn_switch(False)

    async def _async_turn_switch(self, mode: bool) -> None:
        """Set privacy mode."""
        lower_str = str(mode).lower()
        await self._api.async_command(
            f"configManager.cgi?action=setConfig&LeLensMask[0].Enable={lower_str}"
        )

    async def async_update(self) -> None:
        """Get the latest data and updates the state."""
        if not self.available:
            return
        _LOGGER.debug("Updating %s switch", self.name)

        switch_type = self.entity_description.key

        try:        
            """Set unique ID"""
            if self._attr_unique_id is None and (
                serial_number := (await self._api.async_serial_number)
            ):
                self._attr_unique_id = f"{serial_number}-{switch_type}-{self._channel}"

            """Update switch."""
            io_res = (await self._api.async_privacy_config()).splitlines()[0].split("=")[1]
            self._attr_is_on = io_res == "true"
        except AmcrestError as error:
            log_update_error(_LOGGER, "update", self.name, "sensor", error)

