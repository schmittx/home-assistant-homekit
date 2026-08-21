"""Custom constants used be the HomeKit component."""

# #### Attributes ####
ATTR_AVAILABLE = "available"
ATTR_LAST_ACTION = "last_action"
ATTR_LOW_BATTERY = "low_battery"
ATTR_TAMPER_DETECTED = "tamper_detected"
ATTR_TAMPERED = "tampered"
ATTR_SERIAL_NUMBER = "serial_number"

# #### Config ####
CONF_ACCESSORY_INFO_MANUFACTURER = "accessory_info_manufacturer"
CONF_ACCESSORY_INFO_MODEL = "accessory_info_model"
CONF_ACCESSORY_INFO_SERIAL_NUMBER = "accessory_info_serial_number"
CONF_INPUT_DEVICE_TYPE = "device_type"
CONF_INPUT_SOURCE_TYPE = "source_type"
CONF_LINKED_LIGHT = "linked_light"
CONF_LINKED_LIGHT_COLOR = "linked_light_color"
CONF_LINKED_LIGHT_LASER = "linked_light_laser"
CONF_LINKED_LOW_BATTERY_SENSOR = "linked_low_battery_sensor"
CONF_LINKED_MEDIA_PLAYER = "linked_media_player"
CONF_LINKED_OCCUPANCY_SENSOR = "linked_occupancy_sensor"
CONF_LINKED_TAMPER_SENSOR = "linked_tamper_sensor"
CONF_SERVICE_NAME_PREFIX = "service_name_prefix"
CONF_SOURCE = "source"
CONF_SOURCE_CONFIG = "source_config"

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

# #### Categories ####
CATEGORY_ROUTER = 33
CATEGORY_AUDIO_RECEIVER = 34

# #### Services ####
SERV_FAN = "Fan"
SERV_MICROPHONE = "Microphone"

# #### Characteristics ####
CHAR_IDENTIFY = "Identify"
CHAR_INPUT_DEVICE_TYPE = "InputDeviceType"
CHAR_SECURITY_SYSTEM_ALARM_TYPE = "SecuritySystemAlarmType"
CHAR_STATUS_ACTIVE = "StatusActive"
CHAR_STATUS_FAULT = "StatusFault"
CHAR_STATUS_TAMPERED = "StatusTampered"
CHAR_CURRENT_POWER_USAGE = "CurrentPowerUsage"

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
