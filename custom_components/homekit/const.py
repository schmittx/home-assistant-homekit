# Custom Component
"""Constants used be the HomeKit component."""

from __future__ import annotations

from homeassistant.const import CONF_DEVICES
from homeassistant.util.signal_type import SignalTypeFormat

# #### Misc ####
DEBOUNCE_TIMEOUT = 0.5
DEVICE_PRECISION_LEEWAY = 6
DOMAIN = "homekit"
PERSIST_LOCK_DATA = f"{DOMAIN}_persist_lock"
HOMEKIT_FILE = ".homekit.state"
SHUTDOWN_TIMEOUT = 30
CONF_ENTRY_INDEX = "index"
EMPTY_MAC = "00:00:00:00:00:00"
SIGNAL_RELOAD_ENTITIES: SignalTypeFormat[tuple[str, ...]] = SignalTypeFormat(
    "homekit_reload_entities_{}"
)

# ### Codecs ####
VIDEO_CODEC_COPY = "copy"
VIDEO_CODEC_LIBX264 = "libx264"
AUDIO_CODEC_OPUS = "libopus"
VIDEO_CODEC_H264_OMX = "h264_omx"
VIDEO_CODEC_H264_V4L2M2M = "h264_v4l2m2m"
VIDEO_PROFILE_NAMES = ["baseline", "main", "high"]
AUDIO_CODEC_COPY = "copy"

# #### Attributes ####
ATTR_AVAILABLE = "available"
ATTR_DISPLAY_NAME = "display_name"
ATTR_LAST_ACTION = "last_action"
ATTR_LOW_BATTERY = "low_battery"
ATTR_TAMPER_DETECTED = "tamper_detected"
ATTR_TAMPERED = "tampered"
ATTR_VALUE = "value"
ATTR_INTEGRATION = "platform"
ATTR_KEY_NAME = "key_name"
ATTR_SERIAL_NUMBER = "serial_number"
# Current attribute used by homekit_controller
ATTR_OBSTRUCTION_DETECTED = "obstruction-detected"

# #### Config ####
CONF_ACCESSORY_INFO_MANUFACTURER = "accessory_info_manufacturer"
CONF_ACCESSORY_INFO_MODEL = "accessory_info_model"
CONF_ACCESSORY_INFO_SERIAL_NUMBER = "accessory_info_serial_number"
CONF_ADVERTISE_IP = "advertise_ip"
CONF_AUDIO_CODEC = "audio_codec"
CONF_AUDIO_MAP = "audio_map"
CONF_AUDIO_PACKET_SIZE = "audio_packet_size"
CONF_ENTITY_CONFIG = "entity_config"
CONF_EXCLUDE_ACCESSORY_MODE = "exclude_accessory_mode"
CONF_FEATURE = "feature"
CONF_FEATURE_LIST = "feature_list"
CONF_FILTER = "filter"
CONF_HOMEKIT_MODE = "mode"
CONF_INPUT_DEVICE_TYPE = "device_type"
CONF_INPUT_SOURCE_TYPE = "source_type"
CONF_LINKED_BATTERY_SENSOR = "linked_battery_sensor"
CONF_LINKED_BATTERY_CHARGING_SENSOR = "linked_battery_charging_sensor"
CONF_LINKED_DOORBELL_SENSOR = "linked_doorbell_sensor"
CONF_LINKED_HUMIDITY_SENSOR = "linked_humidity_sensor"
CONF_LINKED_LIGHT = "linked_light"
CONF_LINKED_LIGHT_COLOR = "linked_light_color"
CONF_LINKED_LIGHT_LASER = "linked_light_laser"
CONF_LINKED_LOW_BATTERY_SENSOR = "linked_low_battery_sensor"
CONF_LINKED_MEDIA_PLAYER = "linked_media_player"
CONF_LINKED_MOTION_SENSOR = "linked_motion_sensor"
CONF_LINKED_OBSTRUCTION_SENSOR = "linked_obstruction_sensor"
CONF_LINKED_OCCUPANCY_SENSOR = "linked_occupancy_sensor"
CONF_LINKED_TAMPER_SENSOR = "linked_tamper_sensor"
CONF_LINKED_TEMPERATURE_SENSOR = "linked_temperature_sensor"
CONF_LOW_BATTERY_THRESHOLD = "low_battery_threshold"
CONF_MAX_FPS = "max_fps"
CONF_MAX_HEIGHT = "max_height"
CONF_MAX_WIDTH = "max_width"
CONF_SERVICE_NAME_PREFIX = "service_name_prefix"
CONF_SOURCE = "source"
CONF_SOURCE_CONFIG = "source_config"
CONF_STREAM_ADDRESS = "stream_address"
CONF_STREAM_COUNT = "stream_count"
CONF_STREAM_SOURCE = "stream_source"
CONF_SUPPORT_AUDIO = "support_audio"
CONF_THRESHOLD_CO = "co_threshold"
CONF_THRESHOLD_CO2 = "co2_threshold"
CONF_VIDEO_CODEC = "video_codec"
CONF_VIDEO_MAP = "video_map"
CONF_VIDEO_PACKET_SIZE = "video_packet_size"
CONF_VIDEO_PROFILE_NAMES = "video_profile_names"

# #### Config Defaults ####
DEFAULT_SUPPORT_AUDIO = False
DEFAULT_AUDIO_CODEC = AUDIO_CODEC_OPUS
DEFAULT_AUDIO_MAP = "0:a:0"
DEFAULT_AUDIO_PACKET_SIZE = 188
DEFAULT_EXCLUDE_ACCESSORY_MODE = False
DEFAULT_LOW_BATTERY_THRESHOLD = 20
DEFAULT_MAX_FPS = 30
DEFAULT_MAX_HEIGHT = 1080
DEFAULT_MAX_WIDTH = 1920
DEFAULT_PORT = 21063
DEFAULT_CONFIG_FLOW_PORT = 21064
DEFAULT_VIDEO_CODEC = VIDEO_CODEC_LIBX264
DEFAULT_VIDEO_MAP = "0:v:0"
DEFAULT_VIDEO_PACKET_SIZE = 1316
DEFAULT_VIDEO_PROFILE_NAMES = VIDEO_PROFILE_NAMES
DEFAULT_STREAM_COUNT = 3

# #### Features ####
FEATURE_ON_OFF = "on_off"
FEATURE_PLAY_PAUSE = "play_pause"
FEATURE_PLAY_STOP = "play_stop"
FEATURE_TOGGLE_MUTE = "toggle_mute"

# #### HomeKit Component Event ####
EVENT_HOMEKIT_CHANGED = "homekit_state_change"
EVENT_HOMEKIT_TV_REMOTE_KEY_PRESSED = "homekit_tv_remote_key_pressed"

# #### HomeKit Modes ####
HOMEKIT_MODE_ACCESSORY = "accessory"
HOMEKIT_MODE_BRIDGE = "bridge"
DEFAULT_HOMEKIT_MODE = HOMEKIT_MODE_BRIDGE
HOMEKIT_MODES = [HOMEKIT_MODE_BRIDGE, HOMEKIT_MODE_ACCESSORY]

# #### HomeKit Component Services ####
SERVICE_HOMEKIT_RESET_ACCESSORY = "reset_accessory"
SERVICE_HOMEKIT_UNPAIR = "unpair"

# #### String Constants ####
BRIDGE_MODEL = "Bridge"
BRIDGE_NAME = "Home Assistant Bridge"
SHORT_BRIDGE_NAME = "HASS Bridge"
SHORT_ACCESSORY_NAME = "HASS Accessory"
BRIDGE_SERIAL_NUMBER = "homekit.bridge"
MANUFACTURER = "Home Assistant"

# #### Custom Devices ####
DEVICE_AEOTEC_LEAK_SENSOR = "aeotec_leak_sensor"
DEVICE_BROADLINK_REMOTE = "broadlink_remote"
DEVICE_HATCH_REST_PLUS = "hatch_rest_plus"
DEVICE_RATGDO = "ratgdo"
DEVICE_SMARTTHINGS_BUTTON = "smartthings_button"
DEVICE_SMARTTHINGS_LEAK_SENSOR = "smartthings_leak_sensor"
DEVICE_SONY_BRAVIA = "sony_bravia"
DEVICE_TOTAL_CONNECT_CONTACT_SENSOR = "total_connect_contact_sensor"
DEVICE_TOTAL_CONNECT_SECURITY_SYSTEM = "total_connect_security_system"
DEVICE_TOTAL_CONNECT_SMOKE_SENSOR = "total_connect_smoke_sensor"
DEVICE_TUYA_STAR_PROJECTOR = "tuya_star_projector"

# #### Switch Types ####
TYPE_FAUCET = "faucet"
TYPE_OUTLET = "outlet"
TYPE_SHOWER = "shower"
TYPE_SPRINKLER = "sprinkler"
TYPE_SWITCH = "switch"
TYPE_VALVE = "valve"

# #### Categories ####
CATEGORY_ROUTER = 33
CATEGORY_AUDIO_RECEIVER = 34
CATEGORY_RECEIVER = 34

# #### Services ####
SERV_ACCESSORY_INFO = "AccessoryInformation"
SERV_AIR_QUALITY_SENSOR = "AirQualitySensor"
SERV_BATTERY_SERVICE = "BatteryService"
SERV_CAMERA_RTP_STREAM_MANAGEMENT = "CameraRTPStreamManagement"
SERV_CARBON_DIOXIDE_SENSOR = "CarbonDioxideSensor"
SERV_CARBON_MONOXIDE_SENSOR = "CarbonMonoxideSensor"
SERV_CONTACT_SENSOR = "ContactSensor"
SERV_DOOR = "Door"
SERV_DOORBELL = "Doorbell"
SERV_FAN = "Fan"
SERV_FANV2 = "Fanv2"
SERV_GARAGE_DOOR_OPENER = "GarageDoorOpener"
SERV_HUMIDIFIER_DEHUMIDIFIER = "HumidifierDehumidifier"
SERV_HUMIDITY_SENSOR = "HumiditySensor"
SERV_INPUT_SOURCE = "InputSource"
SERV_LEAK_SENSOR = "LeakSensor"
SERV_LIGHT_SENSOR = "LightSensor"
SERV_LIGHTBULB = "Lightbulb"
SERV_LOCK = "LockMechanism"
SERV_MICROPHONE = "Microphone"
SERV_MOTION_SENSOR = "MotionSensor"
SERV_OCCUPANCY_SENSOR = "OccupancySensor"
SERV_OUTLET = "Outlet"
SERV_SECURITY_SYSTEM = "SecuritySystem"
SERV_SERVICE_LABEL = "ServiceLabel"
SERV_SMOKE_SENSOR = "SmokeSensor"
SERV_SPEAKER = "Speaker"
SERV_STATELESS_PROGRAMMABLE_SWITCH = "StatelessProgrammableSwitch"
SERV_SWITCH = "Switch"
SERV_TELEVISION = "Television"
SERV_TELEVISION_SPEAKER = "TelevisionSpeaker"
SERV_TEMPERATURE_SENSOR = "TemperatureSensor"
SERV_THERMOSTAT = "Thermostat"
SERV_VALVE = "Valve"
SERV_WINDOW = "Window"
SERV_WINDOW_COVERING = "WindowCovering"

# #### Characteristics ####
CHAR_ACTIVE = "Active"
CHAR_ACTIVE_IDENTIFIER = "ActiveIdentifier"
CHAR_AIR_PARTICULATE_DENSITY = "AirParticulateDensity"
CHAR_AIR_QUALITY = "AirQuality"
CHAR_BATTERY_LEVEL = "BatteryLevel"
CHAR_BRIGHTNESS = "Brightness"
CHAR_CARBON_DIOXIDE_DETECTED = "CarbonDioxideDetected"
CHAR_CARBON_DIOXIDE_LEVEL = "CarbonDioxideLevel"
CHAR_CARBON_DIOXIDE_PEAK_LEVEL = "CarbonDioxidePeakLevel"
CHAR_CARBON_MONOXIDE_DETECTED = "CarbonMonoxideDetected"
CHAR_CARBON_MONOXIDE_LEVEL = "CarbonMonoxideLevel"
CHAR_CARBON_MONOXIDE_PEAK_LEVEL = "CarbonMonoxidePeakLevel"
CHAR_CHARGING_STATE = "ChargingState"
CHAR_COLOR_TEMPERATURE = "ColorTemperature"
CHAR_CONFIGURED_NAME = "ConfiguredName"
CHAR_CONTACT_SENSOR_STATE = "ContactSensorState"
CHAR_COOLING_THRESHOLD_TEMPERATURE = "CoolingThresholdTemperature"
CHAR_CURRENT_AMBIENT_LIGHT_LEVEL = "CurrentAmbientLightLevel"
CHAR_CURRENT_DOOR_STATE = "CurrentDoorState"
CHAR_CURRENT_FAN_STATE = "CurrentFanState"
CHAR_CURRENT_HEATING_COOLING = "CurrentHeatingCoolingState"
CHAR_CURRENT_HUMIDIFIER_DEHUMIDIFIER = "CurrentHumidifierDehumidifierState"
CHAR_CURRENT_POSITION = "CurrentPosition"
CHAR_CURRENT_HUMIDITY = "CurrentRelativeHumidity"
CHAR_CURRENT_SECURITY_STATE = "SecuritySystemCurrentState"
CHAR_CURRENT_TEMPERATURE = "CurrentTemperature"
CHAR_CURRENT_TILT_ANGLE = "CurrentHorizontalTiltAngle"
CHAR_CURRENT_VISIBILITY_STATE = "CurrentVisibilityState"
CHAR_DEHUMIDIFIER_THRESHOLD_HUMIDITY = "RelativeHumidityDehumidifierThreshold"
CHAR_FIRMWARE_REVISION = "FirmwareRevision"
CHAR_HARDWARE_REVISION = "HardwareRevision"
CHAR_HEATING_THRESHOLD_TEMPERATURE = "HeatingThresholdTemperature"
CHAR_HOLD_POSITION = "HoldPosition"
CHAR_HUE = "Hue"
CHAR_HUMIDIFIER_THRESHOLD_HUMIDITY = "RelativeHumidityHumidifierThreshold"
CHAR_IDENTIFIER = "Identifier"
CHAR_IDENTIFY = "Identify"
CHAR_IN_USE = "InUse"
CHAR_INPUT_DEVICE_TYPE = "InputDeviceType"
CHAR_INPUT_SOURCE_TYPE = "InputSourceType"
CHAR_IS_CONFIGURED = "IsConfigured"
CHAR_LEAK_DETECTED = "LeakDetected"
CHAR_LOCK_CURRENT_STATE = "LockCurrentState"
CHAR_LOCK_TARGET_STATE = "LockTargetState"
CHAR_LINK_QUALITY = "LinkQuality"
CHAR_MANUFACTURER = "Manufacturer"
CHAR_MODEL = "Model"
CHAR_MOTION_DETECTED = "MotionDetected"
CHAR_MUTE = "Mute"
CHAR_NAME = "Name"
CHAR_NITROGEN_DIOXIDE_DENSITY = "NitrogenDioxideDensity"
CHAR_OBSTRUCTION_DETECTED = "ObstructionDetected"
CHAR_OCCUPANCY_DETECTED = "OccupancyDetected"
CHAR_ON = "On"
CHAR_OUTLET_IN_USE = "OutletInUse"
CHAR_PM25_DENSITY = "PM2.5Density"
CHAR_PM10_DENSITY = "PM10Density"
CHAR_POSITION_STATE = "PositionState"
CHAR_PROGRAMMABLE_SWITCH_EVENT = "ProgrammableSwitchEvent"
CHAR_REMOTE_KEY = "RemoteKey"
CHAR_ROTATION_DIRECTION = "RotationDirection"
CHAR_ROTATION_SPEED = "RotationSpeed"
CHAR_SATURATION = "Saturation"
CHAR_SECURITY_SYSTEM_ALARM_TYPE = "SecuritySystemAlarmType"
CHAR_SERIAL_NUMBER = "SerialNumber"
CHAR_SERVICE_LABEL_INDEX = "ServiceLabelIndex"
CHAR_SERVICE_LABEL_NAMESPACE = "ServiceLabelNamespace"
CHAR_SLEEP_DISCOVER_MODE = "SleepDiscoveryMode"
CHAR_SMOKE_DETECTED = "SmokeDetected"
CHAR_STATUS_ACTIVE = "StatusActive"
CHAR_STATUS_FAULT = "StatusFault"
CHAR_STATUS_LOW_BATTERY = "StatusLowBattery"
CHAR_STREAMING_STRATUS = "StreamingStatus"
CHAR_STATUS_TAMPERED = "StatusTampered"
CHAR_SWING_MODE = "SwingMode"
CHAR_TARGET_DOOR_STATE = "TargetDoorState"
CHAR_TARGET_FAN_STATE = "TargetFanState"
CHAR_TARGET_HEATING_COOLING = "TargetHeatingCoolingState"
CHAR_TARGET_HUMIDIFIER_DEHUMIDIFIER = "TargetHumidifierDehumidifierState"
CHAR_TARGET_HUMIDITY = "TargetRelativeHumidity"
CHAR_TARGET_POSITION = "TargetPosition"
CHAR_TARGET_SECURITY_STATE = "SecuritySystemTargetState"
CHAR_TARGET_TEMPERATURE = "TargetTemperature"
CHAR_TARGET_TILT_ANGLE = "TargetHorizontalTiltAngle"
CHAR_TEMP_DISPLAY_UNITS = "TemperatureDisplayUnits"
CHAR_VALVE_TYPE = "ValveType"
CHAR_VOC_DENSITY = "VOCDensity"
CHAR_VOLUME = "Volume"
CHAR_VOLUME_SELECTOR = "VolumeSelector"
CHAR_VOLUME_CONTROL_TYPE = "VolumeControlType"
CHAR_CURRENT_POWER_USAGE = "CurrentPowerUsage"

# #### Properties ####
PROP_MAX_VALUE = "maxValue"
PROP_MIN_VALUE = "minValue"
PROP_MIN_STEP = "minStep"
PROP_CELSIUS = {"minValue": -273, "maxValue": 999}
PROP_VALID_VALUES = "ValidValues"

# #### Thresholds ####
THRESHOLD_CO = 25
THRESHOLD_CO2 = 1000

# #### Default values ####
DEFAULT_MIN_TEMP_WATER_HEATER = 40  # °C
DEFAULT_MAX_TEMP_WATER_HEATER = 60  # °C

# #### Media Player Key Names ####
KEY_ARROW_DOWN = "arrow_down"
KEY_ARROW_LEFT = "arrow_left"
KEY_ARROW_RIGHT = "arrow_right"
KEY_ARROW_UP = "arrow_up"
KEY_BACK = "back"
KEY_EXIT = "exit"
KEY_FAST_FORWARD = "fast_forward"
KEY_INFORMATION = "information"
KEY_NEXT_TRACK = "next_track"
KEY_PREVIOUS_TRACK = "previous_track"
KEY_REWIND = "rewind"
KEY_SELECT = "select"
KEY_PLAY_PAUSE = "play_pause"

# #### Door states ####
HK_DOOR_OPEN = 0
HK_DOOR_CLOSED = 1
HK_DOOR_OPENING = 2
HK_DOOR_CLOSING = 3
HK_DOOR_STOPPED = 4

# ### Position State ####
HK_POSITION_GOING_TO_MIN = 0
HK_POSITION_GOING_TO_MAX = 1
HK_POSITION_STOPPED = 2

# ### Charging State ###
HK_NOT_CHARGING = 0
HK_CHARGING = 1
HK_NOT_CHARGABLE = 2

# ### Config Options ###
CONFIG_OPTIONS = [
   CONF_FILTER,
   CONF_ENTITY_CONFIG,
   CONF_HOMEKIT_MODE,
   CONF_DEVICES,
]

# ### Maximum Lengths ###
MAX_NAME_LENGTH = 64
MAX_SERIAL_LENGTH = 64
MAX_MODEL_LENGTH = 64
MAX_VERSION_LENGTH = 64
MAX_MANUFACTURER_LENGTH = 64

# ### Input Types ###
TYPE_OTHER = "other"
TYPE_TV = "tv"
TYPE_RECORDING = "recording"
TYPE_TUNER = "tuner"
TYPE_PLAYBACK = "playback"
TYPE_AUDIO_SYSTEM = "audio_system"

TYPE_HOME_SCREEN = "home_screen"
TYPE_TUNER = "tuner"
TYPE_HDMI = "hdmi"
TYPE_COMPOSITE_VIDEO = "composite_video"
TYPE_S_VIDEO = "s_video"
TYPE_COMPONENT_VIDEO = "component_video"
TYPE_DVI = "dvi"
TYPE_AIR_PLAY = "air_play"
TYPE_USB = "usb"
TYPE_APPLICATION = "application"

DEFAULT_INPUT_DEVICE_TYPE = TYPE_OTHER
DEFAULT_INPUT_SOURCE_TYPE = TYPE_OTHER

INPUT_DEVICE_TYPES = {
   TYPE_OTHER: 0,
   TYPE_TV: 1,
   TYPE_RECORDING: 2,
   TYPE_TUNER: 3,
   TYPE_PLAYBACK: 4,
   TYPE_AUDIO_SYSTEM: 5,
}

INPUT_SOURCE_TYPES = {
   TYPE_OTHER: 0,
   TYPE_HOME_SCREEN: 1,
   TYPE_TUNER: 2,
   TYPE_HDMI: 3,
   TYPE_COMPOSITE_VIDEO: 4,
   TYPE_S_VIDEO: 5,
   TYPE_COMPONENT_VIDEO: 6,
   TYPE_DVI: 7,
   TYPE_AIR_PLAY: 8,
   TYPE_USB: 9,
   TYPE_APPLICATION: 10,
}

# ### Custom Characteristics ###
"""
   "CumulativeEnergyUsage": {
      "Format": "float",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "E863F10C-079E-48FF-8F27-9C2605A29F52",
      "maxValue": 1000000000,
      "minStep": 0.001,
      "minValue": 0,
      "unit": "kwh"
   },
   "CurrentPowerUsage": {
      "Format": "float",
      "Permissions": [
         "pr",
         "ev"
      ],
      "UUID": "E863F10D-079E-48FF-8F27-9C2605A29F52",
      "maxValue": 1000000000,
      "minStep": 1,
      "minValue": 0,
      "unit": "w"
   },
"""
