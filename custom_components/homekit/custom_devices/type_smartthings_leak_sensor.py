"""Class to hold a custom SmartThings leak sensor accessory."""

import logging

from ..pyhap.const import CATEGORY_SENSOR
from pyhap.util import callback as pyhap_callback

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_ON,
    UnitOfTemperature,
)
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_CURRENT_TEMPERATURE,
    CHAR_LEAK_DETECTED,
    CHAR_NAME,
    CONF_LINKED_TEMPERATURE_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_LEAK_SENSOR,
    SERV_TEMPERATURE_SENSOR,
)
from ..util import convert_to_float, temperature_to_homekit

_LOGGER = logging.getLogger(__name__)


@TYPES.register("SmartThingsLeakSensor")
class SmartThingsLeakSensor(HomeAccessory):
    """Generate a SmartThingsLeakSensor accessory."""

    def __init__(self, *args):
        """Initialize a SmartThingsLeakSensor accessory object."""
        super().__init__(*args, category=CATEGORY_SENSOR)
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Leak Sensor
        state = self.hass.states.get(self.entity_id)
        leak_chars = [
            CHAR_NAME,
            CHAR_LEAK_DETECTED,
        ]
        serv_leak = self.add_preload_service(
            SERV_LEAK_SENSOR, leak_chars,
        )
        serv_leak.configure_char(
            CHAR_NAME, value=f"{prefix} Leak"[:MAX_NAME_LENGTH],
        )
        self.char_leak_detected = serv_leak.configure_char(
            CHAR_LEAK_DETECTED, value=0,
        )

        # Temperature Sensor
        self.linked_temperature_sensor = self.config.get(CONF_LINKED_TEMPERATURE_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked temperature sensor {self.linked_temperature_sensor}")
        if self.linked_temperature_sensor:
            temperature_sensor_state = self.hass.states.get(self.linked_temperature_sensor)
            if temperature_sensor_state:
                temperature_chars = [
                    CHAR_NAME,
                    CHAR_CURRENT_TEMPERATURE,
                ]
                serv_temperature = self.add_preload_service(
                    SERV_TEMPERATURE_SENSOR, temperature_chars,
                )
                serv_temperature.configure_char(
                    CHAR_NAME, value=f"{prefix} Temperature"[:MAX_NAME_LENGTH],
                )
                self.char_temperature = serv_temperature.configure_char(
                    CHAR_CURRENT_TEMPERATURE, value=0,
                )
                self._async_update_temperature_sensor_state(temperature_sensor_state)

        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_temperature_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_temperature_sensor],
                    self._async_update_temperature_sensor_event,
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
    def _async_update_temperature_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_temperature_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_temperature_sensor_state(self, new_state):
        """Handle linked temperature sensor state change to update HomeKit value."""
        if not new_state:
            return

        unit = new_state.attributes.get(
            ATTR_UNIT_OF_MEASUREMENT, UnitOfTemperature.CELSIUS
        )
        if (temperature := convert_to_float(new_state.state)) is not None:
            temperature = temperature_to_homekit(temperature, unit)
            self.char_temperature.set_value(temperature)
            _LOGGER.debug(
                "%s: Current temperature set to %.1f°C", self.entity_id, temperature
            )
