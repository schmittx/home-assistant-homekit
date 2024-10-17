"""Class to hold a custom RATGDO accessory."""

import logging

from ..pyhap.const import CATEGORY_LIGHTBULB
from pyhap.util import callback as pyhap_callback

from homeassistant.components.light import DOMAIN as DOMAIN_LIGHT
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_NAME,
    CHAR_OCCUPANCY_DETECTED,
    CHAR_ON,
    CONF_LINKED_OCCUPANCY_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_LIGHTBULB,
    SERV_OCCUPANCY_SENSOR,
)

_LOGGER = logging.getLogger(__name__)


@TYPES.register("RATGDO")
class RATGDO(HomeAccessory):
    """Generate a RATGDO accessory."""

    def __init__(self, *args):
        """Initialize a RATGDO accessory object."""
        super().__init__(*args, category=CATEGORY_LIGHTBULB)
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Light
        state = self.hass.states.get(self.entity_id)
        light_chars = [
            CHAR_NAME,
        ]
        serv_light = self.add_preload_service(
            SERV_LIGHTBULB, light_chars,
        )
        self.set_primary_service(serv_light)
        serv_light.configure_char(
            CHAR_NAME, value=f"{prefix} Light"[:MAX_NAME_LENGTH],
        )
        self.char_on = serv_light.configure_char(
            CHAR_ON, value=0, setter_callback=self.set_state
        )

        # Occupancy Sensor
        self.linked_occupancy_sensor = self.config.get(CONF_LINKED_OCCUPANCY_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked occupancy sensor {self.linked_occupancy_sensor}")
        if self.linked_occupancy_sensor:
            occupancy_sensor_state = self.hass.states.get(self.linked_occupancy_sensor)
            if occupancy_sensor_state:
                occupancy_chars = [
                    CHAR_NAME,
                    CHAR_OCCUPANCY_DETECTED,
                ]
                serv_occupancy = self.add_preload_service(
                    SERV_OCCUPANCY_SENSOR, occupancy_chars,
                )
                serv_light.add_linked_service(serv_occupancy)
                serv_occupancy.configure_char(
                    CHAR_NAME, value=f"{prefix} Occupancy Detected"[:MAX_NAME_LENGTH],
                )
                self.char_occupancy = serv_occupancy.configure_char(
                    CHAR_OCCUPANCY_DETECTED, value=0,
                )
                self._async_update_occupancy_sensor_state(occupancy_sensor_state)

        self.async_update_state(state)

    def set_state(self, value: bool) -> None:
        """Move light state to value if call came from HomeKit."""
        _LOGGER.debug("%s: Set switch state to %s", self.entity_id, value)
        params = {ATTR_ENTITY_ID: self.entity_id}
        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        self.async_call_service(DOMAIN_LIGHT, service, params)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_occupancy_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_occupancy_sensor],
                    self._async_update_occupancy_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update accessory after state change."""
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.entity_id, current_state)
        self.char_on.set_value(current_state)

    @callback
    def _async_update_occupancy_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_occupancy_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_occupancy_sensor_state(self, new_state):
        """Handle linked occupancy sensor state change to update HomeKit value."""
        detected = new_state.state == STATE_ON
        if self.char_occupancy.value == detected:
            return

        self.char_occupancy.set_value(detected)
        _LOGGER.debug(
            "%s: Set linked occupancy %s sensor to %d",
            self.entity_id,
            self.linked_occupancy_sensor,
            detected,
        )
