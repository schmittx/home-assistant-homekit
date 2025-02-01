"""Class to hold a custom Tuya star projector accessory."""

from __future__ import annotations

import logging
from typing import Any

from ..pyhap.const import CATEGORY_LIGHTBULB
from pyhap.util import callback as pyhap_callback

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_BRIGHTNESS_PCT,
    ATTR_COLOR_MODE,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_RGBW_COLOR,
    ATTR_RGBWW_COLOR,
    ATTR_WHITE,
    DOMAIN as DOMAIN_LIGHT,
    ColorMode,
)
from homeassistant.components.switch import DOMAIN as DOMAIN_SWITCH
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import CALLBACK_TYPE, HassJobType, State, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util.color import color_temperature_to_hs

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_BRIGHTNESS,
    CHAR_COLOR_TEMPERATURE,
    CHAR_HUE,
    CHAR_NAME,
    CHAR_ON,
    CHAR_SATURATION,
    CONF_LINKED_LIGHT_COLOR,
    CONF_LINKED_LIGHT_LASER,
    CONF_SERVICE_NAME_PREFIX,
    MAX_NAME_LENGTH,
    SERV_LIGHTBULB,
    SERV_SWITCH,
)
from ..type_lights import CHANGE_COALESCE_TIME_WINDOW

_LOGGER = logging.getLogger(__name__)


@TYPES.register("TuyaStarProjector")
class TuyaStarProjector(HomeAccessory):
    """Generate a TuyaStarProjector accessory.

    Currently supports: state, brightness, color temperature, rgb_color.
    """

    def __init__(self, *args):
        """Initialize a new TuyaStarProjector accessory object."""
        super().__init__(*args, category=CATEGORY_LIGHTBULB)
        state = self.hass.states.get(self.entity_id)
        assert state
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Power
        power_chars = [
            CHAR_NAME,
            CHAR_ON,
        ]
        serv_power = self.add_preload_service(
            SERV_SWITCH, power_chars,
        )
        self.set_primary_service(serv_power)
        serv_power.configure_char(
            CHAR_NAME, value=f"{prefix} Power"[:MAX_NAME_LENGTH],
        )
        self.power_char_on = serv_power.configure_char(
            CHAR_ON, value=False, setter_callback=self.set_state
        )

        # Color
        self.linked_light_color = self.config.get(CONF_LINKED_LIGHT_COLOR)
        _LOGGER.debug(f"{self.entity_id}: Found linked light for color {self.linked_light_color}")
        if self.linked_light_color:
            color_state = self.hass.states.get(self.linked_light_color)
            if color_state:
                self._color_event_timer: CALLBACK_TYPE | None = None
                self._color_pending_events: dict[str, Any] = {}
                self._color_previous_color_mode = color_state.attributes.get(ATTR_COLOR_MODE)

                color_chars = [
                    CHAR_NAME,
                    CHAR_BRIGHTNESS,
                    CHAR_HUE,
                    CHAR_ON,
                    CHAR_SATURATION,
                ]
                serv_color = self.add_preload_service(
                    SERV_LIGHTBULB, color_chars, "color_service",
                )
                serv_power.add_linked_service(serv_color)
                serv_color.configure_char(
                    CHAR_NAME, value=f"{prefix} Color"[:MAX_NAME_LENGTH],
                )
                self.color_char_on = serv_color.configure_char(
                    CHAR_ON, value=0,
                )
                self.color_char_brightness = serv_color.configure_char(
                    CHAR_BRIGHTNESS, value=100,
                )
                self.color_char_hue = serv_color.configure_char(
                    CHAR_HUE, value=0,
                )
                self.color_char_saturation = serv_color.configure_char(
                    CHAR_SATURATION, value=75,
                )
                self._async_update_color_state(color_state)
                serv_color.setter_callback = self._set_color_chars

        # Laser
        self.linked_light_laser = self.config.get(CONF_LINKED_LIGHT_LASER)
        _LOGGER.debug(f"{self.entity_id}: Found linked light for laser {self.linked_light_laser}")
        if self.linked_light_laser:
            laser_state = self.hass.states.get(self.linked_light_laser)
            if laser_state:
                self._laser_event_timer: CALLBACK_TYPE | None = None
                self._laser_pending_events: dict[str, Any] = {}
                self._laser_previous_color_mode = laser_state.attributes.get(ATTR_COLOR_MODE)

                laser_chars = [
                    CHAR_NAME,
                    CHAR_ON,
                    CHAR_BRIGHTNESS,
                ]
                serv_laser = self.add_preload_service(
                    SERV_LIGHTBULB, laser_chars, "laser_service",
                )
                serv_power.add_linked_service(serv_laser)
                serv_laser.configure_char(
                    CHAR_NAME, value=f"{prefix} Laser"[:MAX_NAME_LENGTH],
                )
                self.laser_char_on = serv_laser.configure_char(
                    CHAR_ON, value=0,
                )
                self.laser_char_brightness = serv_laser.configure_char(
                    CHAR_BRIGHTNESS, value=100,
                )
                self._async_update_laser_state(laser_state)
                serv_laser.setter_callback = self._set_laser_chars

        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_light_color:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_light_color],
                    self._async_update_color_event,
                    job_type=HassJobType.Callback,
                )
            )

        if self.linked_light_laser:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_light_laser],
                    self._async_update_laser_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state):
        """Update state after state changed."""
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.entity_id, current_state)
        self.power_char_on.set_value(current_state)

    @callback
    def _async_update_color_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_color_state(event.data.get("new_state"))

    @callback
    def _async_update_laser_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_laser_state(event.data.get("new_state"))

    @callback
    def _async_update_color_state(self, new_state: State):
        """Handle linked light state change to update HomeKit value."""
        if not new_state:
            return

        state = new_state.state
        attributes = new_state.attributes
        color_mode = attributes.get(ATTR_COLOR_MODE)
        self.color_char_on.set_value(int(state == STATE_ON))
        color_mode_changed = self._color_previous_color_mode != color_mode
        self._color_previous_color_mode = color_mode

        # Handle brightness
        if (
            (brightness := attributes.get(ATTR_BRIGHTNESS)) is not None
            and isinstance(brightness, (int, float))
        ):
            brightness = round(brightness / 255 * 100, 0)
            # The homeassistant component might report its brightness as 0 but is
            # not off. But 0 is a special value in homekit. When you turn on a
            # homekit accessory it will try to restore the last brightness state
            # which will be the last value saved by char_brightness.set_value.
            # But if it is set to 0, HomeKit will update the brightness to 100 as
            # it thinks 0 is off.
            #
            # Therefore, if the the brightness is 0 and the device is still on,
            # the brightness is mapped to 1 otherwise the update is ignored in
            # order to avoid this incorrect behavior.
            if brightness == 0 and state == STATE_ON:
                brightness = 1
            self.color_char_brightness.set_value(brightness)
            if color_mode_changed:
                self.color_char_brightness.notify()

        # Handle Color - color must always be set before color temperature
        # or the iOS UI will not display it correctly.
        if color_temp := attributes.get(ATTR_COLOR_TEMP_KELVIN):
            hue, saturation = color_temperature_to_hs(color_temp)
        elif color_mode == ColorMode.WHITE:
            hue, saturation = 0, 0
        elif (
            (hue_sat := attributes.get(ATTR_HS_COLOR))
            and isinstance(hue_sat, (list, tuple))
            and len(hue_sat) == 2
        ):
            hue, saturation = hue_sat
        else:
            hue = None
            saturation = None
        if isinstance(hue, (int, float)) and isinstance(saturation, (int, float)):
            self.color_char_hue.set_value(round(hue, 0))
            self.color_char_saturation.set_value(round(saturation, 0))
            if color_mode_changed:
                # If the color temp changed, be sure to force the color to update
                self.color_char_hue.notify()
                self.color_char_saturation.notify()

    @callback
    def _async_update_laser_state(self, new_state):
        """Handle linked light state change to update HomeKit value."""
        if not new_state:
            return

        state = new_state.state
        attributes = new_state.attributes
        color_mode = attributes.get(ATTR_COLOR_MODE)
        self.laser_char_on.set_value(int(state == STATE_ON))
        color_mode_changed = self._laser_previous_color_mode != color_mode
        self._laser_previous_color_mode = color_mode

        # Handle brightness
        if (
            (brightness := attributes.get(ATTR_BRIGHTNESS)) is not None
            and isinstance(brightness, (int, float))
        ):
            brightness = round(brightness / 255 * 100, 0)
            # The homeassistant component might report its brightness as 0 but is
            # not off. But 0 is a special value in homekit. When you turn on a
            # homekit accessory it will try to restore the last brightness state
            # which will be the last value saved by char_brightness.set_value.
            # But if it is set to 0, HomeKit will update the brightness to 100 as
            # it thinks 0 is off.
            #
            # Therefore, if the the brightness is 0 and the device is still on,
            # the brightness is mapped to 1 otherwise the update is ignored in
            # order to avoid this incorrect behavior.
            if brightness == 0 and state == STATE_ON:
                brightness = 1
            self.laser_char_brightness.set_value(brightness)
            if color_mode_changed:
                self.laser_char_brightness.notify()

    def set_state(self, value):
        """Move switch state to value if call came from HomeKit."""
        _LOGGER.debug("%s: Set switch state to %s", self.entity_id, value)
        params = {ATTR_ENTITY_ID: self.entity_id}
        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        self.async_call_service(DOMAIN_SWITCH, service, params)

    def _set_color_chars(self, char_values):
        _LOGGER.debug("Light _set_chars: %s", char_values)
        # Newest change always wins
        if CHAR_COLOR_TEMPERATURE in self._color_pending_events and (
            CHAR_SATURATION in char_values or CHAR_HUE in char_values
        ):
            del self._color_pending_events[CHAR_COLOR_TEMPERATURE]
        for char in (CHAR_HUE, CHAR_SATURATION):
            if char in self._color_pending_events and CHAR_COLOR_TEMPERATURE in char_values:
                del self._color_pending_events[char]

        self._color_pending_events.update(char_values)
        if self._color_event_timer:
            self._color_event_timer()
        self._color_event_timer = async_call_later(
            self.hass, CHANGE_COALESCE_TIME_WINDOW, self._async_send_color_events
        )

    def _set_laser_chars(self, char_values):
        _LOGGER.debug("Light _set_chars: %s", char_values)
        # Newest change always wins
        if CHAR_COLOR_TEMPERATURE in self._laser_pending_events and (
            CHAR_SATURATION in char_values or CHAR_HUE in char_values
        ):
            del self._laser_pending_events[CHAR_COLOR_TEMPERATURE]
        for char in (CHAR_HUE, CHAR_SATURATION):
            if char in self._laser_pending_events and CHAR_COLOR_TEMPERATURE in char_values:
                del self._laser_pending_events[char]

        self._laser_pending_events.update(char_values)
        if self._laser_event_timer:
            self._laser_event_timer()
        self._laser_event_timer = async_call_later(
            self.hass, CHANGE_COALESCE_TIME_WINDOW, self._async_send_laser_events
        )

    @callback
    def _async_send_color_events(self, *_):
        """Process all changes at once."""
        _LOGGER.debug("Coalesced _set_chars: %s", self._color_pending_events)
        char_values = self._color_pending_events
        self._color_pending_events = {}
        events = []
        service = SERVICE_TURN_ON
        params = {ATTR_ENTITY_ID: self.linked_light_color}

        if CHAR_ON in char_values:
            if not char_values[CHAR_ON]:
                service = SERVICE_TURN_OFF
            events.append(f"Set state to {char_values[CHAR_ON]}")

        brightness_pct = None
        if CHAR_BRIGHTNESS in char_values:
            if char_values[CHAR_BRIGHTNESS] == 0:
                events[-1] = "Set state to 0"
                service = SERVICE_TURN_OFF
            else:
                brightness_pct = char_values[CHAR_BRIGHTNESS]
            events.append(f"brightness at {char_values[CHAR_BRIGHTNESS]}%")

        if service == SERVICE_TURN_OFF:
            self.async_call_service(
                DOMAIN_LIGHT, service, {ATTR_ENTITY_ID: self.linked_light_color}, ", ".join(events)
            )
            return

        # Handle white channels
        if CHAR_COLOR_TEMPERATURE in char_values:
            temp = char_values[CHAR_COLOR_TEMPERATURE]
            events.append(f"color temperature at {temp}")
            bright_val = round(
                ((brightness_pct or self.color_char_brightness.value) * 255) / 100
            )
            params[ATTR_WHITE] = bright_val

        elif CHAR_HUE in char_values or CHAR_SATURATION in char_values:
            hue_sat = (
                char_values.get(CHAR_HUE, self.color_char_hue.value),
                char_values.get(CHAR_SATURATION, self.color_char_saturation.value),
            )
            _LOGGER.debug("%s: Set hs_color to %s", self.linked_light_color, hue_sat)
            events.append(f"set color at {hue_sat}")
            params[ATTR_HS_COLOR] = hue_sat

        if (
            brightness_pct
            and ATTR_RGBWW_COLOR not in params
            and ATTR_RGBW_COLOR not in params
        ):
            params[ATTR_BRIGHTNESS_PCT] = brightness_pct

        _LOGGER.debug(
            "Calling light service with params: %s -> %s", char_values, params
        )
        self.async_call_service(DOMAIN_LIGHT, service, params, ", ".join(events))

    @callback
    def _async_send_laser_events(self, *_):
        """Process all changes at once."""
        _LOGGER.debug("Coalesced _set_chars: %s", self._laser_pending_events)
        char_values = self._laser_pending_events
        self._laser_pending_events = {}
        events = []
        service = SERVICE_TURN_ON
        params = {ATTR_ENTITY_ID: self.linked_light_laser}

        if CHAR_ON in char_values:
            if not char_values[CHAR_ON]:
                service = SERVICE_TURN_OFF
            events.append(f"Set state to {char_values[CHAR_ON]}")

        brightness_pct = None
        if CHAR_BRIGHTNESS in char_values:
            if char_values[CHAR_BRIGHTNESS] == 0:
                events[-1] = "Set state to 0"
                service = SERVICE_TURN_OFF
            else:
                brightness_pct = char_values[CHAR_BRIGHTNESS]
            events.append(f"brightness at {char_values[CHAR_BRIGHTNESS]}%")

        if service == SERVICE_TURN_OFF:
            self.async_call_service(
                DOMAIN_LIGHT, service, {ATTR_ENTITY_ID: self.linked_light_laser}, ", ".join(events)
            )
            return

        if (
            brightness_pct
            and ATTR_RGBWW_COLOR not in params
            and ATTR_RGBW_COLOR not in params
        ):
            params[ATTR_BRIGHTNESS_PCT] = brightness_pct

        _LOGGER.debug(
            "Calling light service with params: %s -> %s", char_values, params
        )
        self.async_call_service(DOMAIN_LIGHT, service, params, ", ".join(events))
