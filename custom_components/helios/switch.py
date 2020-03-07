from homeassistant.components.switch import SwitchDevice
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import (
    DOMAIN,
    SIGNAL_HELIOS_STATE_UPDATE
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    state_proxy = hass.data[DOMAIN]["state_proxy"]
    async_add_entities([HeliosAutoSwitch(state_proxy)])

class HeliosAutoSwitch(SwitchDevice):
    def __init__(self, state_proxy):
        self._state_proxy = state_proxy

    @property
    def name(self) -> str:
        return "Auto Mode"

    @property
    def icon(self):
        return "mdi:auto-fix"

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        return self._state_proxy.is_auto()

    async def async_turn_on(self, **kwargs):
        self._state_proxy.set_auto_mode(True)

    async def async_turn_off(self, **kwargs):
        self._state_proxy.set_auto_mode(False)

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_HELIOS_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)
aa