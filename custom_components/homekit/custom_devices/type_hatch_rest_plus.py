"""Class to hold a custom Hatch Rest Plus accessory."""

from __future__ import annotations

import logging
from typing import Any

from ..pyhap.const import CATEGORY_SPEAKER
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
from homeassistant.components.media_player import (
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_SOUND_MODE,
    ATTR_MEDIA_VOLUME_MUTED,
    ATTR_SOUND_MODE_LIST,
    DOMAIN as DOMAIN_MEDIA_PLAYER,
    SERVICE_SELECT_SOUND_MODE,
    SERVICE_VOLUME_MUTE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_SET,
    SERVICE_VOLUME_UP,
    STATE_ON,
)
from homeassistant.core import CALLBACK_TYPE, HassJobType, State, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util.color import (
    color_temperature_kelvin_to_mired,
    color_temperature_to_hs,
)

from ..accessories import TYPES, HomeAccessory
from ..const import (
    CHAR_ACTIVE,
    CHAR_ACTIVE_IDENTIFIER,
    CHAR_BRIGHTNESS,
    CHAR_COLOR_TEMPERATURE,
    CHAR_CONFIGURED_NAME,
    CHAR_CURRENT_VISIBILITY_STATE,
    CHAR_HUE,
    CHAR_IDENTIFIER,
    CHAR_INPUT_DEVICE_TYPE,
    CHAR_INPUT_SOURCE_TYPE,
    CHAR_IS_CONFIGURED,
    CHAR_MUTE,
    CHAR_NAME,
    CHAR_ON,
    CHAR_SATURATION,
    CHAR_SLEEP_DISCOVER_MODE,
    CHAR_VOLUME,
    CHAR_VOLUME_CONTROL_TYPE,
    CHAR_VOLUME_SELECTOR,
    CONF_INPUT_DEVICE_TYPE,
    CONF_INPUT_SOURCE_TYPE,
    CONF_LINKED_LIGHT,
    CONF_LINKED_MEDIA_PLAYER,
    CONF_SERVICE_NAME_PREFIX,
    CONF_SOURCE,
    DEFAULT_INPUT_DEVICE_TYPE,
    DEFAULT_INPUT_SOURCE_TYPE,
    INPUT_DEVICE_TYPES,
    INPUT_SOURCE_TYPES,
    MAX_NAME_LENGTH,
    PROP_MAX_VALUE,
    PROP_MIN_VALUE,
    SERV_INPUT_SOURCE,
    SERV_LIGHTBULB,
    SERV_TELEVISION,
    SERV_TELEVISION_SPEAKER,
)
from ..type_lights import CHANGE_COALESCE_TIME_WINDOW, DEFAULT_MAX_COLOR_TEMP

_LOGGER = logging.getLogger(__name__)


@TYPES.register("HatchRestPlus")
class HatchRestPlus(HomeAccessory):
    """Generate a HatchRestPlus accessory.

    Currently supports: state, brightness, color temperature, rgb_color.
    """

    def __init__(self, *args: Any) -> None:
        """Initialize a new HatchRestPlus accessory object."""
        super().__init__(*args, category=CATEGORY_SPEAKER)
        state = self.hass.states.get(self.entity_id)
        assert state
        prefix = self.config.get(CONF_SERVICE_NAME_PREFIX, self.display_name)

        # Light
        self.linked_light = self.config.get(CONF_LINKED_LIGHT)
        self.min_mireds = color_temperature_kelvin_to_mired(DEFAULT_MAX_COLOR_TEMP)
        _LOGGER.debug(f"{self.entity_id}: Found linked light {self.linked_light}")
        if self.linked_light:
            light_state = self.hass.states.get(self.linked_light)
            if light_state:
                self._event_timer: CALLBACK_TYPE | None = None
                self._pending_events: dict[str, Any] = {}
                self._previous_color_mode = state.attributes.get(ATTR_COLOR_MODE)

                light_chars = [
                    CHAR_NAME,
                    CHAR_BRIGHTNESS,
                    CHAR_COLOR_TEMPERATURE,
                    CHAR_HUE,
                    CHAR_ON,
                    CHAR_SATURATION,
                ]
                serv_light = self.add_preload_service(
                    SERV_LIGHTBULB, light_chars,
                )
                self.set_primary_service(serv_light)
                serv_light.configure_char(
                    CHAR_NAME, value=f"{prefix} Nightlight"[:MAX_NAME_LENGTH],
                )
                self.light_char_on = serv_light.configure_char(
                    CHAR_ON, value=0,
                )
                self.light_char_brightness = serv_light.configure_char(
                    CHAR_BRIGHTNESS, value=100,
                )
                self.light_char_color_temperature = serv_light.configure_char(
                    CHAR_COLOR_TEMPERATURE,
                    value=self.min_mireds,
                    properties={
                        PROP_MIN_VALUE: self.min_mireds,
                        PROP_MAX_VALUE: self.min_mireds,
                    },
                )
                self.light_char_hue = serv_light.configure_char(
                    CHAR_HUE, value=0,
                )
                self.light_char_saturation = serv_light.configure_char(
                    CHAR_SATURATION, value=75,
                )
                self._async_update_light_state(light_state)
                serv_light.setter_callback = self._set_light_chars

        # Speaker
        self.linked_media_player = self.config.get(CONF_LINKED_MEDIA_PLAYER)
        _LOGGER.debug(f"{self.entity_id}: Found linked media player {self.linked_media_player}")
        if self.linked_media_player:
            media_player_state = self.hass.states.get(self.linked_media_player)
            if media_player_state:
                audio_chars = [
                    CHAR_ACTIVE,
                    CHAR_ACTIVE_IDENTIFIER,
                    CHAR_CONFIGURED_NAME,
                    CHAR_SLEEP_DISCOVER_MODE,
                ]
                serv_audio = self.add_preload_service(
                    SERV_TELEVISION, audio_chars,
                )
                serv_audio.configure_char(
                    CHAR_CONFIGURED_NAME, value=f"{prefix} Sound Machine"[:MAX_NAME_LENGTH],
                )
                serv_audio.configure_char(
                    CHAR_SLEEP_DISCOVER_MODE, value=True,
                )
                self.audio_char_active = serv_audio.configure_char(
                    CHAR_ACTIVE, value=False, setter_callback=self._set_audio_state,
                )

                self.audio_char_input_source = serv_audio.configure_char(
                    CHAR_ACTIVE_IDENTIFIER, setter_callback=self._set_audio_input_source,
                )
                self.sources = []
                source_list = media_player_state.attributes.get(ATTR_SOUND_MODE_LIST, [])
                if source_list:
                    for source in source_list:
                        self.sources.append(
                            {
                                CONF_SOURCE: source,
                                CONF_INPUT_DEVICE_TYPE: DEFAULT_INPUT_DEVICE_TYPE,
                                CONF_INPUT_SOURCE_TYPE: DEFAULT_INPUT_SOURCE_TYPE,
                            }.copy()
                        )
                self.input_chars = [
                    CHAR_CONFIGURED_NAME,
                    CHAR_CURRENT_VISIBILITY_STATE,
                    CHAR_IDENTIFIER,
                    CHAR_INPUT_DEVICE_TYPE,
                    CHAR_INPUT_SOURCE_TYPE,
                    CHAR_IS_CONFIGURED,
                    CHAR_NAME,
                ]
                for index, source in enumerate(self.sources):
                    serv_input = self.add_preload_service(
                        SERV_INPUT_SOURCE, self.input_chars, unique_id=source[CONF_SOURCE],
                    )
                    serv_audio.add_linked_service(serv_input)

                    serv_input.configure_char(
                        CHAR_CONFIGURED_NAME, value=source[CONF_SOURCE],
                    )

                    serv_input.configure_char(
                        CHAR_CURRENT_VISIBILITY_STATE, value=False,
                    )

                    serv_input.configure_char(
                        CHAR_IDENTIFIER, value=index,
                    )

                    serv_input.configure_char(
                        CHAR_INPUT_DEVICE_TYPE, value=INPUT_DEVICE_TYPES[source[CONF_INPUT_DEVICE_TYPE]],
                    )

                    serv_input.configure_char(
                        CHAR_INPUT_SOURCE_TYPE, value=INPUT_SOURCE_TYPES[source[CONF_INPUT_SOURCE_TYPE]],
                    )

                    serv_input.configure_char(
                        CHAR_IS_CONFIGURED, value=True,
                    )

                    serv_input.configure_char(
                        CHAR_NAME, value=source[CONF_SOURCE][:MAX_NAME_LENGTH],
                    )

                    _LOGGER.debug("%s: Added source %s", self.entity_id, source[CONF_SOURCE])

                speaker_chars = [
                    CHAR_NAME,
                    CHAR_ACTIVE,
                    CHAR_MUTE,
                    CHAR_VOLUME,
                    CHAR_VOLUME_CONTROL_TYPE,
                    CHAR_VOLUME_SELECTOR,
                ]
                serv_speaker = self.add_preload_service(
                    SERV_TELEVISION_SPEAKER, speaker_chars,
                )
                serv_audio.add_linked_service(serv_speaker)
                serv_speaker.configure_char(
                    CHAR_NAME, value=f"{prefix} Speaker"[:MAX_NAME_LENGTH],
                )
                serv_speaker.configure_char(
                    CHAR_ACTIVE, value=1,
                )
                self.speaker_char_mute = serv_speaker.configure_char(
                    CHAR_MUTE, value=False, setter_callback=self._set_speaker_mute,
                )
                serv_speaker.configure_char(
                    CHAR_VOLUME_CONTROL_TYPE, value=1,
                )

                self.speaker_char_volume_selector = serv_speaker.configure_char(
                    CHAR_VOLUME_SELECTOR, setter_callback=self._set_speaker_volume_step,
                )
                self.speaker_char_volume = serv_speaker.configure_char(
                    CHAR_VOLUME, setter_callback=self._set_speaker_volume,
                )
                self._async_update_media_player_state(media_player_state)

        self.async_update_state(state)

    @callback
    @pyhap_callback
    def run(self) -> None:
        """Handle accessory driver started event."""
        super().run()
        if self.linked_light:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_light],
                    self._async_update_light_event,
                    job_type=HassJobType.Callback,
                )
            )

        if self.linked_media_player:
            self._subscriptions.append(
                async_track_state_change_event(
                    self.hass,
                    [self.linked_media_player],
                    self._async_update_media_player_event,
                    job_type=HassJobType.Callback,
                )
            )

    @callback
    def async_update_state(self, new_state: State) -> None:
        """Update state after state changed."""
        return

    @callback
    def _async_update_light_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_light_state(event.data.get("new_state"))

    @callback
    def _async_update_light_state(self, new_state):
        """Handle linked light state change to update HomeKit value."""
        if not new_state:
            return

        state = new_state.state
        attributes = new_state.attributes
        color_mode = attributes.get(ATTR_COLOR_MODE)
        self.light_char_on.set_value(int(state == STATE_ON))
        color_mode_changed = self._previous_color_mode != color_mode
        self._previous_color_mode = color_mode

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
            self.light_char_brightness.set_value(brightness)
            if color_mode_changed:
                self.light_char_brightness.notify()

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
            self.light_char_hue.set_value(round(hue, 0))
            self.light_char_saturation.set_value(round(saturation, 0))
            if color_mode_changed:
                # If the color temp changed, be sure to force the color to update
                self.light_char_hue.notify()
                self.light_char_saturation.notify()

        # Handle white channels
        color_temp = None
        if color_mode == ColorMode.WHITE:
            color_temp = self.min_mireds
        if isinstance(color_temp, (int, float)):
            self.light_char_color_temperature.set_value(round(color_temp, 0))
            if color_mode_changed:
                self.light_char_color_temperature.notify()

    @callback
    def _async_update_media_player_event(self, event):
        """Handle state change event listener callback."""
        self._async_update_media_player_state(event.data.get("new_state"))

    @callback
    def _async_update_media_player_state(self, new_state):
        """Handle linked media player state change to update HomeKit value."""
        if not new_state:
            return

        # Handle active state
        current_state = new_state.state == STATE_ON
        _LOGGER.debug("%s: Set current state to %s", self.linked_media_player, current_state)
        self.audio_char_active.set_value(current_state)

        # Handle active input
        if self.sources:
            index = None
            source_name = new_state.attributes.get(ATTR_SOUND_MODE)
            _LOGGER.debug("%s: Set current input to %s", self.linked_media_player, source_name)
            for _index, source in enumerate(self.sources):
                if source_name == source[CONF_SOURCE]:
                    index = _index
                    break
            if index:
                self.audio_char_input_source.set_value(index)
            elif current_state:
                _LOGGER.debug(
                    "%s: Sources out of sync. Restart Home Assistant", self.linked_media_player,
                )
                self.audio_char_input_source.set_value(0)

        # Handle mute state
        mute = bool(new_state.attributes.get(ATTR_MEDIA_VOLUME_MUTED))
        self.speaker_char_mute.set_value(mute)

        # Handle volume level
        volume_level = new_state.attributes.get(ATTR_MEDIA_VOLUME_LEVEL)
        if isinstance(volume_level, (float, int)):
            volume = int(volume_level * 100)
            _LOGGER.debug("%s: Set current volume level to %s", self.linked_media_player, volume)
            self.speaker_char_volume.set_value(volume)

    def _set_light_chars(self, char_values):
        _LOGGER.debug("Light _set_chars: %s", char_values)
        # Newest change always wins
        if CHAR_COLOR_TEMPERATURE in self._pending_events and (
            CHAR_SATURATION in char_values or CHAR_HUE in char_values
        ):
            del self._pending_events[CHAR_COLOR_TEMPERATURE]
        for char in (CHAR_HUE, CHAR_SATURATION):
            if char in self._pending_events and CHAR_COLOR_TEMPERATURE in char_values:
                del self._pending_events[char]

        self._pending_events.update(char_values)
        if self._event_timer:
            self._event_timer()
        self._event_timer = async_call_later(
            self.hass, CHANGE_COALESCE_TIME_WINDOW, self._async_send_light_events
        )

    @callback
    def _async_send_light_events(self, *_):
        """Process all changes at once."""
        _LOGGER.debug("Coalesced _set_chars: %s", self._pending_events)
        char_values = self._pending_events
        self._pending_events = {}
        events = []
        service = SERVICE_TURN_ON
        params = {ATTR_ENTITY_ID: self.linked_light}

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
                DOMAIN_LIGHT, service, {ATTR_ENTITY_ID: self.linked_light}, ", ".join(events)
            )
            return

        # Handle white channels
        if CHAR_COLOR_TEMPERATURE in char_values:
            temp = char_values[CHAR_COLOR_TEMPERATURE]
            events.append(f"color temperature at {temp}")
            bright_val = round(
                ((brightness_pct or self.light_char_brightness.value) * 255) / 100
            )
            params[ATTR_WHITE] = bright_val

        elif CHAR_HUE in char_values or CHAR_SATURATION in char_values:
            hue_sat = (
                char_values.get(CHAR_HUE, self.light_char_hue.value),
                char_values.get(CHAR_SATURATION, self.light_char_saturation.value),
            )
            _LOGGER.debug("%s: Set hs_color to %s", self.linked_light, hue_sat)
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

    def _set_audio_state(self, value):
        """Move switch state to value if call came from HomeKit."""
        _LOGGER.debug("%s: Set switch state to %s", self.linked_media_player, value)
        params = {ATTR_ENTITY_ID: self.linked_media_player}
        service = SERVICE_TURN_ON if value else SERVICE_TURN_OFF
        self.async_call_service(DOMAIN_MEDIA_PLAYER, service, params)

    def _set_audio_input_source(self, value):
        """Send input set value if call came from HomeKit."""
        _LOGGER.debug("%s: Set current input to %s", self.linked_media_player, value)
        source = self.sources[value][CONF_SOURCE]
        params = {ATTR_ENTITY_ID: self.linked_media_player, ATTR_SOUND_MODE: source}
        self.async_call_service(DOMAIN_MEDIA_PLAYER, SERVICE_SELECT_SOUND_MODE, params)

    def _set_speaker_mute(self, value):
        """Move switch state to value if call came from HomeKit."""
        _LOGGER.debug(
            '%s: Set switch state for "toggle_mute" to %s', self.linked_media_player, value
        )
        params = {ATTR_ENTITY_ID: self.linked_media_player, ATTR_MEDIA_VOLUME_MUTED: value}
        self.async_call_service(DOMAIN_MEDIA_PLAYER, SERVICE_VOLUME_MUTE, params)

    def _set_speaker_volume(self, value):
        """Send volume step value if call came from HomeKit."""
        _LOGGER.debug("%s: Set volume to %s", self.linked_media_player, value)
        params = {ATTR_ENTITY_ID: self.linked_media_player, ATTR_MEDIA_VOLUME_LEVEL: value}
        self.async_call_service(DOMAIN_MEDIA_PLAYER, SERVICE_VOLUME_SET, params)

    def _set_speaker_volume_step(self, value):
        """Send volume step value if call came from HomeKit."""
        _LOGGER.debug("%s: Step volume by %s", self.linked_media_player, value)
        service = SERVICE_VOLUME_DOWN if value else SERVICE_VOLUME_UP
        params = {ATTR_ENTITY_ID: self.linked_media_player}
        self.async_call_service(DOMAIN_MEDIA_PLAYER, service, params)
