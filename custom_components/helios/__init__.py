from datetime import timedelta
import ipaddress
import time
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.components.fan import (
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_OFF,
    SUPPORT_SET_SPEED,
    FanEntity,
)

import eazyctrl

DOMAIN = "helios"
CONF_NEXT_FILTER = "next_filter_change"
DEFAULT_NAME = "Helios"
SPEED_MAX = "max"

SIGNAL_HELIOS_STATE_UPDATE = "helios_state_update"
SCAN_INTERVAL = timedelta(seconds=60)

VALUE_TO_SPEED = {
    0: SPEED_OFF,
    1: SPEED_LOW,
    2: SPEED_MEDIUM,
    3: SPEED_HIGH,
    4: SPEED_MAX
}
SPEED_TO_VALUE = {v: k for k, v in VALUE_TO_SPEED.items()}

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(ipaddress.ip_address, cv.string),
                vol.Optional(CONF_NEXT_FILTER, default=None): cv.date,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    next_filter = conf.get(CONF_NEXT_FILTER)
    name = conf.get(CONF_NAME)

    client = eazyctrl.EazyController(host)
    state_proxy = HeliosStateProxy(hass, client)
    hass.data[DOMAIN] = {"client": client, "state_proxy": state_proxy, "next_filter": next_filter, "name": name}

    hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, {}, config))
    hass.async_create_task(async_load_platform(hass, "switch", DOMAIN, {}, config))
    hass.async_create_task(async_load_platform(hass, "fan", DOMAIN, {}, config))

    async_track_time_interval(hass, state_proxy.async_update, SCAN_INTERVAL)
    await
    state_proxy.async_update(0)

    return True


class HeliosStateProxy:
    def __init__(self, hass, client):
        self._hass = hass
        self._client = client
        self._auto = None
        self._speed = None
        self._percent = None

    def set_speed(self, speed: str):
        self._client.set_variable('v00101', '1')
        self._auto = False
        self._client.set_feature('fan_stage', SPEED_TO_VALUE[speed])
        self._speed = SPEED_TO_VALUE[speed]
        self.fetchPercent()

    def set_auto_mode(self, enabled: bool):
        self._client.set_variable('v00101', '0' if enabled else '1')
        self._auto = enabled
        self.fetchPercent()

    def get_speed(self):
        return self._speed

    def get_speed_percent(self):
        return self._percent

    def is_auto(self) -> bool:
        return self._auto

    async def async_update(self, event_time):
        self._auto = self._client.get_variable("v00101", 1, conversion=int) == 0
        self._speed = self._client.get_feature('fan_stage')
        self.fetchPercent()

    def fetchPercent(self):
        time.sleep(2)
        self._percent = self._client.get_variable("v00103", 2, conversion=int)
        async_dispatcher_send(self._hass, SIGNAL_HELIOS_STATE_UPDATE)
