"""
Mouse input for PyEPL3

Provides mouse event tracking and button/axis abstractions.
"""

import pygame
from typing import Optional, Tuple
from pathlib import Path

from .base import LogTrack
from .timing import now
from .exceptions import InputError


class MouseTrack(LogTrack):
    """
    Mouse event track for logging mouse events.
    """

    def __init__(self, trackname: str = "mouse",
                 archive_dir: Optional[Path] = None):
        """
        Initialize mouse track.

        Args:
            trackname: Name for this track
            archive_dir: Directory for log files
        """
        super().__init__(trackname, archive_dir, ".mouselog")

    def _writeHeader(self):
        """Write log header."""
        if self.logfile:
            self.logfile.write("timestamp\ttick\tevent\tdetails\n")

    def logButtonPress(self, button: int, position: Tuple[int, int],
                       timestamp: Optional[int] = None):
        """
        Log a mouse button press.

        Args:
            button: Button number
            position: (x, y) position
            timestamp: Timestamp (None = now)
        """
        if timestamp is None:
            timestamp = now()
        self.logMessage(f"PRESS\tbutton={button},pos={position}", timestamp)

    def logButtonRelease(self, button: int, position: Tuple[int, int],
                        timestamp: Optional[int] = None):
        """
        Log a mouse button release.

        Args:
            button: Button number
            position: (x, y) position
            timestamp: Timestamp (None = now)
        """
        if timestamp is None:
            timestamp = now()
        self.logMessage(f"RELEASE\tbutton={button},pos={position}", timestamp)

    def logMotion(self, position: Tuple[int, int],
                  timestamp: Optional[int] = None):
        """
        Log mouse motion.

        Args:
            position: (x, y) position
            timestamp: Timestamp (None = now)
        """
        if timestamp is None:
            timestamp = now()
        self.logMessage(f"MOTION\tpos={position}", timestamp)


class MouseButton:
    """
    Represents a mouse button.
    """

    def __init__(self, button_num: int):
        """
        Create a mouse button.

        Args:
            button_num: Button number (1=left, 2=middle, 3=right)
        """
        self.button_num = button_num

    def isPressed(self) -> bool:
        """Check if button is currently pressed."""
        buttons = pygame.mouse.get_pressed()
        if self.button_num <= len(buttons):
            return buttons[self.button_num - 1]
        return False

    def __repr__(self):
        button_names = {1: "LEFT", 2: "MIDDLE", 3: "RIGHT"}
        name = button_names.get(self.button_num, f"BUTTON{self.button_num}")
        return f"MouseButton({name})"


class MouseAxis:
    """
    Represents mouse position as an axis.
    """

    def __init__(self, axis: str = "x"):
        """
        Create a mouse axis.

        Args:
            axis: Axis name ("x" or "y")
        """
        if axis.lower() not in ["x", "y"]:
            raise InputError(f"Invalid axis: {axis}")
        self.axis = axis.lower()

    def get(self) -> int:
        """Get current axis position."""
        pos = pygame.mouse.get_pos()
        if self.axis == "x":
            return pos[0]
        else:
            return pos[1]

    def __repr__(self):
        return f"MouseAxis('{self.axis}')"


# Common mouse buttons
LEFT_BUTTON = MouseButton(1)
MIDDLE_BUTTON = MouseButton(2)
RIGHT_BUTTON = MouseButton(3)
