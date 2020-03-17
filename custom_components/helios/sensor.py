from datetime import datetime, date

from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from . import (
    DOMAIN,
    SIGNAL_HELIOS_STATE_UPDATE
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    client = hass.data[DOMAIN]["client"]
    state_proxy = hass.data[DOMAIN]["state_proxy"]

    sensors = [
        HeliosTempSensor(client, "Outside Air", "temp_outside_air"),
        HeliosTempSensor(client, "Supply Air", "temp_supply_air"),
        HeliosTempSensor(client, "Extract Air", "temp_extract_air"),
        HeliosTempSensor(client, "Exhaust Air", "temp_outgoing_air"),
        HeliosSensor(client, "Extract Air Humidity", "v02136", 2, "%", "mdi:water-percent"),
        HeliosSensor(client, "Supply Air Speed", "v00348", 4, "rpm", "mdi:fan"),
        HeliosSensor(client, "Extract Air Speed", "v00349", 4, "rpm", "mdi:fan"),
        HeliosFanSpeedSensor(state_proxy),
    ]

    if hass.data[DOMAIN]["next_filter"] is not None:
        sensors.append(HeliosDaysSensor("Next Filter Change in", hass.data[DOMAIN]["next_filter"]))

    async_add_entities(
        sensors,
        update_before_add=False
    )

class HeliosTempSensor(Entity):
    def __init__(self, client, name, metric):
        self._state = None
        self._name = name
        self._metric = metric
        self._client = client

    def update(self):
        self._state = self._client.get_feature(self._metric)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

class HeliosSensor(Entity):
    def __init__(self, client, name, var, var_length, units, icon):
        self._state = None
        self._name = name
        self._variable = var
        self._var_length = var_length
        self._units = units
        self._icon = icon
        self._client = client

    def update(self):
        self._state = self._client.get_variable(
            self._variable,
            self._var_length,
            conversion=int
        )

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._units

class HeliosFanSpeedSensor(Entity):
    def __init__(self, state_proxy):
        self._state_proxy = state_proxy

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

    @property
    def name(self):
        return "Fan Speed"

    @property
    def state(self):
        return self._state_proxy.get_speed_percent()

    @property
    def icon(self):
        return "mdi:fan"

    @property
    def unit_of_measurement(self):
        return "%"

class HeliosDaysSensor(Entity):
    def __init__(self, name, date_to):
        self._date_to = date_to
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return (self._date_to-date.today()).days

    @property
    def unit_of_measurement(self):
        return 'days'
