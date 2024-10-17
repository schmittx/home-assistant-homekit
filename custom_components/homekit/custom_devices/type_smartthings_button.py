"""Class to hold a custom SmartThings button accessory."""

import logging

from ..pyhap.const import CATEGORY_PROGRAMMABLE_SWITCH
from pyhap.util import callback as pyhap_callback

from homeassistant.components.event import ATTR_EVENT_TYPE
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_CURRENT_TEMPERATURE,
    CHAR_NAME,
    CHAR_PROGRAMMABLE_SWITCH_EVENT,
    CONF_LINKED_TEMPERATURE_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_STATELESS_PROGRAMMABLE_SWITCH,
    SERV_TEMPERATURE_SENSOR,
)
from ..util import convert_to_float, temperature_to_homekit

SWITCH_EVENT_MAP = {
    "pushed": 0,
    "double": 1,
    "held": 2,
}

_LOGGER = logging.getLogger(__name__)


@TYPES.register("SmartThingsButton")
class SmartThingsButton(HomeAccessory):
    """Generate a SmartThingsButton accessory."""

    def __init__(self, *args):
        """Initialize a SmartThingsButton accessory object."""
        super().__init__(*args, category=CATEGORY_PROGRAMMABLE_SWITCH)
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Button
        state = self.hass.states.get(self.entity_id)
        switch_chars = [
            CHAR_NAME,
            CHAR_PROGRAMMABLE_SWITCH_EVENT,
        ]
        serv_switch = self.add_preload_service(
            SERV_STATELESS_PROGRAMMABLE_SWITCH, switch_chars,
        )
        serv_switch.configure_char(
            CHAR_NAME, value=f"{prefix} Switch"[:MAX_NAME_LENGTH],
        )
        self.char_switch_event = serv_switch.configure_char(
            CHAR_PROGRAMMABLE_SWITCH_EVENT,
        )
        self.old_state = state.state

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
        if new_state.state != STATE_UNKNOWN:
            attrs = new_state.attributes
            switch_event = SWITCH_EVENT_MAP[attrs.get(ATTR_EVENT_TYPE)]
            if new_state.state != self.old_state:
                self.char_switch_event.set_value(switch_event)
                self.old_state = new_state.state

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
