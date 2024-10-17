"""Class to hold a custom Broadlink remote accessory."""

import logging

from ..pyhap.const import CATEGORY_SENSOR
from pyhap.util import callback as pyhap_callback

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    UnitOfTemperature,
)
from homeassistant.core import HassJobType, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_CURRENT_HUMIDITY,
    CHAR_CURRENT_TEMPERATURE,
    CHAR_NAME,
    CONF_LINKED_HUMIDITY_SENSOR,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_HUMIDITY_SENSOR,
    SERV_TEMPERATURE_SENSOR,
)
from ..util import convert_to_float, temperature_to_homekit

_LOGGER = logging.getLogger(__name__)


@TYPES.register("BroadlinkRemote")
class BroadlinkRemote(HomeAccessory):
    """Generate a BroadlinkRemote accessory."""

    def __init__(self, *args):
        """Initialize a BroadlinkRemote accessory object."""
        super().__init__(*args, category=CATEGORY_SENSOR)
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Temperature Sensor
        state = self.hass.states.get(self.entity_id)
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

        # Humidity Sensor
        self.linked_humidity_sensor = self.config.get(CONF_LINKED_HUMIDITY_SENSOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked humidity sensor {self.linked_humidity_sensor}")
        if self.linked_humidity_sensor:
            humidity_sensor_state = self.hass.states.get(self.linked_humidity_sensor)
            if humidity_sensor_state:
                humidity_chars = [
                    CHAR_NAME,
                    CHAR_CURRENT_HUMIDITY,
                ]
                serv_humidity = self.add_preload_service(
                    SERV_HUMIDITY_SENSOR, temperature_chars,
                )
                serv_humidity.configure_char(
                    CHAR_NAME, value=f"{prefix} Humidity"[:MAX_NAME_LENGTH],
                )
                self.char_humidity = serv_humidity.configure_char(
                    CHAR_CURRENT_HUMIDITY, value=0,
                )
                self._async_update_humidity_sensor_state(humidity_sensor_state)

        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_humidity_sensor:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_humidity_sensor],
                    self._async_update_humidity_sensor_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update accessory after state change."""
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

    @callback
    def _async_update_humidity_sensor_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_humidity_sensor_state(event.data.get("new_state"))

    @callback
    def _async_update_humidity_sensor_state(self, new_state):
        """Handle linked humidity sensor state change to update HomeKit value."""
        if not new_state:
            return

        if (humidity := convert_to_float(new_state.state)) is not None:
            self.char_humidity.set_value(humidity)
            _LOGGER.debug("%s: Current humidity set to %d%%", self.entity_id, humidity)
