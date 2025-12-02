"""
Keyboard input for PyEPL3

Provides keyboard event tracking and button abstractions.
"""

import pygame
from typing import Optional, List, Union, Tuple
from pathlib import Path

from .base import LogTrack
from .timing import PresentationClock, now
from .exceptions import InputError


# Pygame key name mappings
KEY_NAMES = {
    pygame.K_SPACE: "SPACE",
    pygame.K_RETURN: "RETURN",
    pygame.K_ESCAPE: "ESCAPE",
    pygame.K_BACKSPACE: "BACKSPACE",
    pygame.K_TAB: "TAB",
    pygame.K_LSHIFT: "LSHIFT",
    pygame.K_RSHIFT: "RSHIFT",
    pygame.K_LCTRL: "LCTRL",
    pygame.K_RCTRL: "RCTRL",
    pygame.K_LALT: "LALT",
    pygame.K_RALT: "RALT",
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_F1: "F1",
    pygame.K_F2: "F2",
    pygame.K_F3: "F3",
    pygame.K_F4: "F4",
    pygame.K_F5: "F5",
    pygame.K_F6: "F6",
    pygame.K_F7: "F7",
    pygame.K_F8: "F8",
    pygame.K_F9: "F9",
    pygame.K_F10: "F10",
    pygame.K_F11: "F11",
    pygame.K_F12: "F12",
}


def get_key_name(key_code: int) -> str:
    """Get name for a pygame key code."""
    if key_code in KEY_NAMES:
        return KEY_NAMES[key_code]
    try:
        name = pygame.key.name(key_code)
        return name.upper()
    except:
        return f"KEY_{key_code}"


class KeyTrack(LogTrack):
    """
    Keyboard event track for logging key presses and releases.
    """

    def __init__(self, trackname: str = "keyboard",
                 archive_dir: Optional[Path] = None):
        """
        Initialize keyboard track.

        Args:
            trackname: Name for this track
            archive_dir: Directory for log files
        """
        super().__init__(trackname, archive_dir, ".keylog")

    def _writeHeader(self):
        """Write log header."""
        if self.logfile:
            self.logfile.write("timestamp\ttick\tevent\tkey\n")

    def logKeyPress(self, key_name: str, timestamp: Optional[int] = None):
        """
        Log a key press event.

        Args:
            key_name: Name of key pressed
            timestamp: Timestamp (None = now)
        """
        if timestamp is None:
            timestamp = now()
        self.logMessage(f"PRESS\t{key_name}", timestamp)

    def logKeyRelease(self, key_name: str, timestamp: Optional[int] = None):
        """
        Log a key release event.

        Args:
            key_name: Name of key released
            timestamp: Timestamp (None = now)
        """
        if timestamp is None:
            timestamp = now()
        self.logMessage(f"RELEASE\t{key_name}", timestamp)


class Key:
    """
    Represents a keyboard key as a Button.
    """

    def __init__(self, key_name: str):
        """
        Create a key button.

        Args:
            key_name: Name of key (e.g., "SPACE", "A", "RETURN")
        """
        self.key_name = key_name.upper()

        # Find pygame key code
        self.key_code = None
        for code, name in KEY_NAMES.items():
            if name == self.key_name:
                self.key_code = code
                break

        # Try single character keys
        if self.key_code is None and len(self.key_name) == 1:
            self.key_code = ord(self.key_name.lower())

        if self.key_code is None:
            # Try getting from pygame
            try:
                self.key_code = getattr(pygame, f"K_{self.key_name}")
            except AttributeError:
                raise InputError(f"Unknown key: {key_name}")

    def isPressed(self) -> bool:
        """Check if key is currently pressed."""
        keys = pygame.key.get_pressed()
        return keys[self.key_code] if self.key_code < len(keys) else False

    def __repr__(self):
        return f"Key('{self.key_name}')"


class ButtonChooser:
    """
    Waits for one of several buttons to be pressed.
    """

    def __init__(self, *buttons: Union[Key, 'MouseButton'],
                 track: Optional[KeyTrack] = None):
        """
        Create a button chooser.

        Args:
            *buttons: Button objects to wait for
            track: Track for logging events
        """
        self.buttons = list(buttons)
        self.track = track

    def wait(self, clk: Optional[PresentationClock] = None,
             timeout: Optional[int] = None) -> Optional[Union[Key, 'MouseButton']]:
        """
        Wait for a button press.

        Args:
            clk: Presentation clock
            timeout: Timeout in milliseconds (None = no timeout)

        Returns:
            Button that was pressed, or None if timeout
        """
        result, _ = self.waitWithTime(clk, timeout)
        return result

    def waitWithTime(self, clk: Optional[PresentationClock] = None,
                     timeout: Optional[int] = None) -> Tuple[Optional[Union[Key, 'MouseButton']], int]:
        """
        Wait for a button press and return with timestamp.

        Args:
            clk: Presentation clock
            timeout: Timeout in milliseconds (None = no timeout)

        Returns:
            Tuple of (button pressed, timestamp) or (None, timestamp) if timeout
        """
        # Record start time
        start_time = clk.get() if clk else now()

        # Clear any stale MOUSEMOTION and KEYUP events before starting
        for event in pygame.event.get([pygame.MOUSEMOTION, pygame.KEYUP]):
            pass  # Just drain these events

        # Main wait loop
        while True:
            # Check for relevant events only (QUIT, KEYDOWN, MOUSEBUTTONDOWN)
            # This prevents MOUSEMOTION from clogging the queue
            for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]):
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt("Window closed")

                if event.type == pygame.KEYDOWN:
                    # Check if this key matches any of our buttons
                    key_name = get_key_name(event.key)

                    for button in self.buttons:
                        if isinstance(button, Key) and button.key_name == key_name:
                            timestamp = clk.get() if clk else now()

                            # Log key press
                            if self.track and self.track.isLogging():
                                self.track.logKeyPress(key_name, timestamp)

                            return (button, timestamp)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle mouse buttons
                    from .mouse import MouseButton

                    for button in self.buttons:
                        if isinstance(button, MouseButton):
                            if button.button_num == event.button:
                                timestamp = clk.get() if clk else now()
                                return (button, timestamp)

            # Check timeout
            if timeout is not None:
                current_time = clk.get() if clk else now()
                elapsed = current_time - start_time
                if elapsed >= timeout:
                    return (None, current_time)

            # Wait 10ms before checking again (reduces CPU usage and iterations)
            # For a 5000ms timeout, this means ~500 checks instead of 5000
            pygame.time.wait(10)

            # If using a clock, advance it by the wait time
            if clk:
                clk._virtual_time += 10
