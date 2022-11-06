from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from homeassistant.components.fan import (
    FanEntityFeature,
    FanEntity,
)

from .const import (
    DOMAIN,
    SUPPORTED_PRESET_MODES,
    PRESET_MODE_OFF,
    PRESET_MODE_MEDIUM,
    SIGNAL_HELIOS_STATE_UPDATE
)

async def async_setup_entry(hass, entry, async_add_entities):
    state_proxy = hass.data[DOMAIN]["state_proxy"]
    name = hass.data[DOMAIN]["name"]
    async_add_entities([HeliosFan(state_proxy, name)])

class HeliosFan(FanEntity):
    def __init__(self, state_proxy, name):
        self._state_proxy = state_proxy
        self._attr_name = name

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass, SIGNAL_HELIOS_STATE_UPDATE, self._update_callback
        )

    @callback
    def _update_callback(self):
        self.async_schedule_update_ha_state(True)

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs) -> None:
        self._state_proxy.set_speed(preset_mode if not preset_mode is None else PRESET_MODE_MEDIUM)

    async def async_turn_off(self, **kwargs) -> None:
        self._state_proxy.set_speed(PRESET_MODE_OFF)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        self._state_proxy.set_speed(preset_mode)

    @property
    def name(self):
        return self._attr_name

    @property
    def is_on(self) -> bool:
        speed = self._state_proxy.get_speed()
        return speed != None and speed > 0

    @property
    def percentage(self) -> str:
        percentage = self._state_proxy.get_speed_percent()
        if percentage == None:
            return 0

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of available preset modes."""
        return SUPPORTED_PRESET_MODES

    @property
    def supported_features(self) -> int:
        return FanEntityFeature.PRESET_MODE
