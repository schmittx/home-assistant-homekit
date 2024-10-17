"""Class to hold a custom Aeotec leak sensor accessory."""

import logging

from ..pyhap.const import CATEGORY_SENSOR
from pyhap.util import callback as pyhap_callback

from homeassistant.const import STATE_ON
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_LEAK_DETECTED,
    CHAR_NAME,
    CHAR_STATUS_TAMPERED,
    CONF_LINKED_TAMPER_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_LEAK_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


@TYPES.register("AeotecLeakSensor")
class AeotecLeakSensor(HomeAccessory):
    """Generate a AeotecLeakSensor accessory."""

    def __init__(self, *args):
        """Initialize a AeotecLeakSensor accessory object."""
        super().__init__(*args, category=CATEGORY_SENSOR)
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Leak Sensor
        state = self.hass.states.get(self.entity_id)
        leak_chars = [
            CHAR_NAME,
            CHAR_LEAK_DETECTED,
        ]

        self.linked_tamper_sensor = self.config.get(CONF_LINKED_TAMPER_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked tamper sensor {self.linked_tamper_sensor}")
        if self.linked_tamper_sensor:
            tamper_sensor_state = self.hass.states.get(self.linked_tamper_sensor)
            if tamper_sensor_state:
                leak_chars.append(CHAR_STATUS_TAMPERED)

        serv_leak = self.add_preload_service(
            SERV_LEAK_SENSOR, leak_chars,
        )
        serv_leak.configure_char(
            CHAR_NAME, value=f"{prefix} Leak"[:MAX_NAME_LENGTH],
        )
        self.char_leak_detected = serv_leak.configure_char(
            CHAR_LEAK_DETECTED, value=0,
        )

        if CHAR_STATUS_TAMPERED in leak_chars:
            self.char_tamper_detected = serv_leak.configure_char(
                CHAR_STATUS_TAMPERED, value=0,
            )
            self._async_update_tamper_sensor_state(tamper_sensor_state)

        self.async_update_state(state)

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
        """Update accessory after state change."""
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.entity_id, current_state)
        self.char_leak_detected.set_value(int(current_state))

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
