import datetime
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.components.fan import (
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_OFF
)

DOMAIN = 'helios'
DEFAULT_NAME = "Helios"

SPEED_MAX = "max"

CONF_NEXT_FILTER = "next_filter_change"

SIGNAL_HELIOS_STATE_UPDATE = "helios_state_update"
SCAN_INTERVAL = datetime.timedelta(seconds=60)

VALUE_TO_SPEED = {
    0: SPEED_OFF,
    1: SPEED_LOW,
    2: SPEED_MEDIUM,
    3: SPEED_HIGH,
    4: SPEED_MAX
}
SPEED_TO_VALUE = {v: k for k, v in VALUE_TO_SPEED.items()}
