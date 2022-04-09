import datetime
from homeassistant.const import CONF_HOST, CONF_NAME

DOMAIN = 'helios'
DEFAULT_NAME = "Helios"

SPEED_OFF = "off"
SPEED_LOW = "low"
SPEED_MEDIUM = "medium"
SPEED_HIGH = "high"
SPEED_MAX = "max"

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
