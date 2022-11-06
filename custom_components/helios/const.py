import datetime
from homeassistant.const import CONF_HOST, CONF_NAME

DOMAIN = 'helios'
DEFAULT_NAME = "Helios"

SIGNAL_HELIOS_STATE_UPDATE = "helios_state_update"
SCAN_INTERVAL = datetime.timedelta(seconds=60)

PRESET_MODE_OFF = "off"
PRESET_MODE_LOW = "low"
PRESET_MODE_MEDIUM = "medium"
PRESET_MODE_HIGH = "high"
PRESET_MODE_MAX = "max"

VALUE_TO_SPEED = {
    0: PRESET_MODE_OFF,
    1: PRESET_MODE_LOW,
    2: PRESET_MODE_MEDIUM,
    3: PRESET_MODE_HIGH,
    4: PRESET_MODE_MAX
}

SPEED_TO_VALUE = {v: k for k, v in VALUE_TO_SPEED.items()}

SUPPORTED_PRESET_MODES = [
    PRESET_MODE_OFF,
    PRESET_MODE_LOW,
    PRESET_MODE_MEDIUM,
    PRESET_MODE_HIGH,
    PRESET_MODE_MAX
]

