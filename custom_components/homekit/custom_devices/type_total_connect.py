"""Class to hold a custom Total Connect security panel accessory."""

import logging

from ..pyhap.const import CATEGORY_ALARM_SYSTEM, CATEGORY_SENSOR
from pyhap.util import callback as pyhap_callback

from homeassistant.components.alarm_control_panel.const import DOMAIN
from homeassistant.const import (
    ATTR_CODE,
    ATTR_ENTITY_ID,
    SERVICE_ALARM_ARM_AWAY,
    SERVICE_ALARM_ARM_HOME,
    SERVICE_ALARM_ARM_NIGHT,
    SERVICE_ALARM_DISARM,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION,
    STATE_ALARM_ARMING,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
    STATE_ON,
)
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_CURRENT_SECURITY_STATE,
    CHAR_CONTACT_SENSOR_STATE,
    CHAR_NAME,
    CHAR_SECURITY_SYSTEM_ALARM_TYPE,
    CHAR_SMOKE_DETECTED,
    CHAR_STATUS_LOW_BATTERY,
    CHAR_STATUS_TAMPERED,
    CHAR_TARGET_SECURITY_STATE,
    CONF_LINKED_LOW_BATTERY_SENSOR,
    CONF_LINKED_TAMPER_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_CONTACT_SENSOR,
    SERV_SECURITY_SYSTEM,
    SERV_SMOKE_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

HK_ALARM_STAY_ARMED = 0
HK_ALARM_AWAY_ARMED = 1
HK_ALARM_NIGHT_ARMED = 2
HK_ALARM_DISARMED = 3
HK_ALARM_TRIGGERED = 4

HASS_TO_HOMEKIT_CURRENT = {
    STATE_ALARM_ARMED_HOME: HK_ALARM_STAY_ARMED,
    STATE_ALARM_ARMED_VACATION: HK_ALARM_AWAY_ARMED,
    STATE_ALARM_ARMED_AWAY: HK_ALARM_AWAY_ARMED,
    STATE_ALARM_ARMED_NIGHT: HK_ALARM_NIGHT_ARMED,
    STATE_ALARM_ARMING: HK_ALARM_DISARMED,
    STATE_ALARM_DISARMED: HK_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED: HK_ALARM_TRIGGERED,
}

HASS_TO_HOMEKIT_TARGET = {
    STATE_ALARM_ARMED_HOME: HK_ALARM_STAY_ARMED,
    STATE_ALARM_ARMED_VACATION: HK_ALARM_AWAY_ARMED,
    STATE_ALARM_ARMED_AWAY: HK_ALARM_AWAY_ARMED,
    STATE_ALARM_ARMED_NIGHT: HK_ALARM_NIGHT_ARMED,
    STATE_ALARM_ARMING: HK_ALARM_AWAY_ARMED,
    STATE_ALARM_DISARMED: HK_ALARM_DISARMED,
}

HASS_TO_HOMEKIT_SERVICES = {
    SERVICE_ALARM_ARM_HOME: HK_ALARM_STAY_ARMED,
    SERVICE_ALARM_ARM_AWAY: HK_ALARM_AWAY_ARMED,
    SERVICE_ALARM_ARM_NIGHT: HK_ALARM_NIGHT_ARMED,
    SERVICE_ALARM_DISARM: HK_ALARM_DISARMED,
}

HK_TO_SERVICE = {
    HK_ALARM_AWAY_ARMED: SERVICE_ALARM_ARM_AWAY,
    HK_ALARM_STAY_ARMED: SERVICE_ALARM_ARM_HOME,
    HK_ALARM_NIGHT_ARMED: SERVICE_ALARM_ARM_NIGHT,
    HK_ALARM_DISARMED: SERVICE_ALARM_DISARM,
}


@TYPES.register("TotalConnectSecuritySystem")
class TotalConnectSecuritySystem(HomeAccessory):
    """Generate a TotalConnectSecuritySystem accessory."""

    def __init__(self, *args):
        """Initialize a TotalConnectSecuritySystem accessory object."""
        super().__init__(*args, category=CATEGORY_ALARM_SYSTEM)
        self._alarm_code = self.config.get(ATTR_CODE)

        security_system_chars = [
            CHAR_NAME,
            CHAR_CURRENT_SECURITY_STATE,
            CHAR_TARGET_SECURITY_STATE,
            CHAR_SECURITY_SYSTEM_ALARM_TYPE,
        ]

        self.linked_tamper_sensor = self.config.get(CONF_LINKED_TAMPER_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked tamper sensor {self.linked_tamper_sensor}")
        if self.linked_tamper_sensor:
            tamper_sensor_state = self.hass.states.get(self.linked_tamper_sensor)
            if tamper_sensor_state:
                security_system_chars.append(CHAR_STATUS_TAMPERED)

        serv_security_system = self.add_preload_service(
            SERV_SECURITY_SYSTEM, security_system_chars
        )

        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)
        serv_security_system.configure_char(
            CHAR_NAME, value=f"{prefix} Security System"[:MAX_NAME_LENGTH],
        )

#        current_char = serv_security_system.get_characteristic(CHAR_CURRENT_SECURITY_STATE)
        self.char_current_state = serv_security_system.configure_char(
            CHAR_CURRENT_SECURITY_STATE,
            value=HASS_TO_HOMEKIT_CURRENT[STATE_ALARM_DISARMED],
#            valid_values=current_char.properties.get("ValidValues"),
        )

#        target_char = serv_security_system.get_characteristic(CHAR_TARGET_SECURITY_STATE)
        self.char_target_state = serv_security_system.configure_char(
            CHAR_TARGET_SECURITY_STATE,
            value=HASS_TO_HOMEKIT_SERVICES[SERVICE_ALARM_DISARM],
#            valid_values=target_char.properties.get("ValidValues"),
            setter_callback=self.set_security_state,
        )

        self.char_alarm_type = serv_security_system.configure_char(
            CHAR_SECURITY_SYSTEM_ALARM_TYPE, value=0,
        )

        if CHAR_STATUS_TAMPERED in security_system_chars:
            self.char_tamper_detected = serv_security_system.configure_char(
                CHAR_STATUS_TAMPERED, value=0,
            )
            self._async_update_tamper_sensor_state(tamper_sensor_state)

        state = self.hass.states.get(self.entity_id)
        self.async_update_state(state)

    def set_security_state(self, value):
        """Move security state to value if call came from HomeKit."""
        _LOGGER.debug("%s: Set security state to %d", self.entity_id, value)
        service = HK_TO_SERVICE[value]

        params = {ATTR_ENTITY_ID: self.entity_id}
        if self._alarm_code:
            params[ATTR_CODE] = self._alarm_code
        self.async_call_service(DOMAIN, service, params)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_tamper_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_tamper_sensor],
                    self._async_update_tamper_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update security state after state changed."""
        hass_state = new_state.state
        if (current_state := HASS_TO_HOMEKIT_CURRENT.get(hass_state)) is not None:
            self.char_current_state.set_value(current_state)
            _LOGGER.debug(
                "%s: Updated current state to %s (%d)",
                self.entity_id,
                hass_state,
                current_state,
            )

        if (target_state := HASS_TO_HOMEKIT_TARGET.get(hass_state)) is not None:
            self.char_target_state.set_value(target_state)

        alarm_type = hass_state == STATE_ALARM_TRIGGERED
        self.char_alarm_type.set_value(alarm_type)

    @callback
    def _async_update_tamper_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_tamper_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_tamper_sensor_state(self, new_state):
        """Handle linked tamper sensor state change to update HomeKit value."""
        if not new_state:
            return

        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set tamper state to %s", self.entity_id, current_state)
        self.char_tamper_detected.set_value(int(current_state))


@TYPES.register("TotalConnectContactSensor")
class TotalConnectContactSensor(HomeAccessory):
    """Generate a TotalConnectContactSensor accessory."""

    def __init__(self, *args):
        """Initialize a TotalConnectContactSensor accessory object."""
        super().__init__(*args, category=CATEGORY_SENSOR)

        contact_chars = [
            CHAR_NAME,
            CHAR_CONTACT_SENSOR_STATE,
        ]

        self.linked_low_battery_sensor = self.config.get(CONF_LINKED_LOW_BATTERY_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked low battery sensor {self.linked_low_battery_sensor}")
        if self.linked_low_battery_sensor:
            low_battery_sensor_state = self.hass.states.get(self.linked_low_battery_sensor)
            if low_battery_sensor_state:
                contact_chars.append(CHAR_STATUS_LOW_BATTERY)

        self.linked_tamper_sensor = self.config.get(CONF_LINKED_TAMPER_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked tamper sensor {self.linked_tamper_sensor}")
        if self.linked_tamper_sensor:
            tamper_sensor_state = self.hass.states.get(self.linked_tamper_sensor)
            if tamper_sensor_state:
                contact_chars.append(CHAR_STATUS_TAMPERED)

        serv_contact = self.add_preload_service(
            SERV_CONTACT_SENSOR, contact_chars,
        )

        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)
        serv_contact.configure_char(
            CHAR_NAME, value=f"{prefix} Contact"[:MAX_NAME_LENGTH],
        )

        self.char_contact_detected = serv_contact.configure_char(
            CHAR_CONTACT_SENSOR_STATE, value=0,
        )

        if CHAR_STATUS_LOW_BATTERY in contact_chars:
            self.char_low_battery_detected = serv_contact.configure_char(
                CHAR_STATUS_LOW_BATTERY, value=0,
            )
            self._async_update_low_battery_sensor_state(low_battery_sensor_state)

        if CHAR_STATUS_TAMPERED in contact_chars:
            self.char_tamper_detected = serv_contact.configure_char(
                CHAR_STATUS_TAMPERED, value=0,
            )
            self._async_update_tamper_sensor_state(tamper_sensor_state)

        state = self.hass.states.get(self.entity_id)
        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_low_battery_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_low_battery_sensor],
                    self._async_update_low_battery_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )
        if self.linked_tamper_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_tamper_sensor],
                    self._async_update_tamper_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update accessory after state change."""
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.entity_id, current_state)
        self.char_contact_detected.set_value(int(current_state))

    @callback
    def _async_update_low_battery_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_low_battery_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_low_battery_sensor_state(self, new_state):
        """Handle linked low battery sensor state change to update HomeKit value."""
        if not new_state:
            return

        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set low battery state to %s", self.entity_id, current_state)
        self.char_low_battery_detected.set_value(int(current_state))

    @callback
    def _async_update_tamper_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_tamper_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_tamper_sensor_state(self, new_state):
        """Handle linked tamper sensor state change to update HomeKit value."""
        if not new_state:
            return

        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set tamper state to %s", self.entity_id, current_state)
        self.char_tamper_detected.set_value(int(current_state))


@TYPES.register("TotalConnectSmokeSensor")
class TotalConnectSmokeSensor(HomeAccessory):
    """Generate a TotalConnectSmokeSensor accessory."""

    def __init__(self, *args):
        """Initialize a TotalConnectSmokeSensor accessory object."""
        super().__init__(*args, category=CATEGORY_SENSOR)

        smoke_chars = [
            CHAR_NAME,
            CHAR_CONTACT_SENSOR_STATE,
        ]

        self.linked_low_battery_sensor = self.config.get(CONF_LINKED_LOW_BATTERY_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked low battery sensor {self.linked_low_battery_sensor}")
        if self.linked_low_battery_sensor:
            low_battery_sensor_state = self.hass.states.get(self.linked_low_battery_sensor)
            if low_battery_sensor_state:
                smoke_chars.append(CHAR_STATUS_LOW_BATTERY)

        self.linked_tamper_sensor = self.config.get(CONF_LINKED_TAMPER_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked tamper sensor {self.linked_tamper_sensor}")
        if self.linked_tamper_sensor:
            tamper_sensor_state = self.hass.states.get(self.linked_tamper_sensor)
            if tamper_sensor_state:
                smoke_chars.append(CHAR_STATUS_TAMPERED)

        serv_smoke = self.add_preload_service(
            SERV_SMOKE_SENSOR, smoke_chars,
        )

        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)
        serv_smoke.configure_char(
            CHAR_NAME, value=f"{prefix} Smoke"[:MAX_NAME_LENGTH],
        )

        self.char_smoke_detected = serv_smoke.configure_char(
            CHAR_SMOKE_DETECTED, value=0,
        )

        if CHAR_STATUS_LOW_BATTERY in smoke_chars:
            self.char_low_battery_detected = serv_smoke.configure_char(
                CHAR_STATUS_LOW_BATTERY, value=0,
            )
            self._async_update_low_battery_sensor_state(low_battery_sensor_state)

        if CHAR_STATUS_TAMPERED in smoke_chars:
            self.char_tamper_detected = serv_smoke.configure_char(
                CHAR_STATUS_TAMPERED, value=0,
            )
            self._async_update_tamper_sensor_state(tamper_sensor_state)

        state = self.hass.states.get(self.entity_id)
        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_low_battery_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_low_battery_sensor],
                    self._async_update_low_battery_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )
        if self.linked_tamper_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_tamper_sensor],
                    self._async_update_tamper_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update accessory after state change."""
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.entity_id, current_state)
        self.char_smoke_detected.set_value(int(current_state))

    @callback
    def _async_update_low_battery_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_low_battery_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_low_battery_sensor_state(self, new_state):
        """Handle linked low battery sensor state change to update HomeKit value."""
        if not new_state:
            return

        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set low battery state to %s", self.entity_id, current_state)
        self.char_low_battery_detected.set_value(int(current_state))

    @callback
    def _async_update_tamper_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_tamper_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_tamper_sensor_state(self, new_state):
        """Handle linked tamper sensor state change to update HomeKit value."""
        if not new_state:
            return

        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set tamper state to %s", self.entity_id, current_state)
        self.char_tamper_detected.set_value(int(current_state))