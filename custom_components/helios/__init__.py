from datetime import timedelta
import ipaddress
import time
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    FanEntity,
)

from .const import (
    DOMAIN,
    SPEED_OFF,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_HIGH,
    SPEED_MAX,
    VALUE_TO_SPEED,
    SPEED_TO_VALUE,
    SIGNAL_HELIOS_STATE_UPDATE,
    SCAN_INTERVAL,
    CONF_HOST,
    CONF_NAME,
)

import eazyctrl

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["config"] = config.get(DOMAIN) or {}
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    host = config_entry.data[CONF_HOST]
    name = config_entry.data[CONF_NAME]

    client = eazyctrl.EazyController(host)
    state_proxy = HeliosStateProxy(hass, client)
    hass.data[DOMAIN] = {"client": client, "state_proxy": state_proxy, "name": name}

    def handle_fan_boost(call):
        duration = call.data.get('duration', 60)
        speed = call.data.get('speed', 'high')
        if int(duration) > 0:
            hass.data[DOMAIN]['state_proxy'].start_boost_mode(speed, duration)
        else:
            hass.data[DOMAIN]['state_proxy'].stop_boost_mode()

    hass.services.async_register(DOMAIN, "fan_boost", handle_fan_boost)
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "sensor"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "switch"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "fan"))

    async_track_time_interval(hass, state_proxy.async_update, SCAN_INTERVAL)
    await state_proxy.async_update(0)
    return True

class HeliosStateProxy:
    def __init__(self, hass, client):
        self._hass = hass
        self._client = client
        self._auto = None
        self._speed = None
        self._percent = None
        self._boost_time = 0

    def set_speed(self, speed: str):
        self._client.set_variable('v00101', '1')
        self._auto = False
        self._client.set_feature('fan_stage', SPEED_TO_VALUE[speed])
        self._speed = SPEED_TO_VALUE[speed]
        self.fetchPercent()

    def start_boost_mode(self, speed: str, time: int):
        self._client.set_variable('v00093', '0')
        self._client.set_variable('v00092', SPEED_TO_VALUE[speed])
        self._client.set_variable('v00091', time)
        self._client.set_variable('v00094', '1')
        self.fetchPercent()

    def stop_boost_mode(self):
        self._client.set_variable('v00094', '0')
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

    def get_boost_time(self) -> int:
        return self._boost_time

    async def async_update(self, event_time):
        self._auto = self._client.get_variable("v00101", 1, conversion=int) == 0
        self._speed = self._client.get_feature('fan_stage')
        self.fetchPercent()

    def fetchPercent(self):
        time.sleep(2)
        self._boost_time = self._client.get_variable("v00093", 3, conversion=int)
        self._percent = self._client.get_variable("v00103", 3, conversion=int)
        async_dispatcher_send(self._hass, SIGNAL_HELIOS_STATE_UPDATE)
