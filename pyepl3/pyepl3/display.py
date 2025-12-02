"""
Display system for PyEPL3

Provides video output, image display, text rendering, and compound stimuli
with flexible positioning and timing control.
"""

import pygame
from PIL import Image as PILImage
from pathlib import Path
from typing import Optional, Tuple, List, Union, Any
from enum import IntEnum

from .base import LogTrack, MediaFile
from .timing import PresentationClock, now
from .exceptions import DisplayError


# Positioning constants
class Anchor(IntEnum):
    """Anchor points for positioning"""
    UPPER_LEFT = 0
    UPPER_CENTER = 1
    UPPER_RIGHT = 2
    CENTER_LEFT = 3
    CENTER = 4
    CENTER_RIGHT = 5
    LOWER_LEFT = 6
    LOWER_CENTER = 7
    LOWER_RIGHT = 8


# Relative positioning constants
ABOVE = "above"
BELOW = "below"
LEFT = "left"
RIGHT = "right"
OVER = "over"


class Color:
    """RGB Color representation."""

    def __init__(self, r: int, g: int, b: int):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))

    def tuple(self) -> Tuple[int, int, int]:
        """Get color as RGB tuple."""
        return (self.r, self.g, self.b)

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"


# Common colors
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)


class Showable:
    """
    Base class for anything that can be displayed on screen.
    """

    def __init__(self):
        self.surface: Optional[pygame.Surface] = None
        self.anchor = Anchor.CENTER
        self.position = (0, 0)  # Absolute position
        self._shown = False

    def getSize(self) -> Tuple[int, int]:
        """Get size in pixels."""
        if self.surface:
            return self.surface.get_size()
        return (0, 0)

    def getAnchorPos(self, anchor: Anchor) -> Tuple[int, int]:
        """Get position of an anchor point in absolute coordinates."""
        width, height = self.getSize()
        x, y = self.position

        # Calculate offset based on anchor
        anchor_offsets = [
            (0, 0),                    # UPPER_LEFT
            (width // 2, 0),           # UPPER_CENTER
            (width, 0),                # UPPER_RIGHT
            (0, height // 2),          # CENTER_LEFT
            (width // 2, height // 2), # CENTER
            (width, height // 2),      # CENTER_RIGHT
            (0, height),               # LOWER_LEFT
            (width // 2, height),      # LOWER_CENTER
            (width, height),           # LOWER_RIGHT
        ]

        offset_x, offset_y = anchor_offsets[anchor]
        return (x + offset_x, y + offset_y)

    def setAnchor(self, anchor: Anchor):
        """Set the anchor point for positioning."""
        self.anchor = anchor

    def render(self) -> pygame.Surface:
        """Render and return the surface. Override in subclasses."""
        return self.surface

    def present(self, clk: Optional[PresentationClock] = None,
                duration: int = 0, jitter: int = 0) -> int:
        """
        Present stimulus for a duration.

        Args:
            clk: Presentation clock
            duration: Duration in milliseconds
            jitter: Random jitter to add to duration

        Returns:
            Timestamp when presented
        """
        # This is a simple version - VideoTrack handles actual presentation
        if clk and duration > 0:
            clk.delay(duration, jitter)
        return now()


class Image(Showable, MediaFile):
    """
    Image stimulus that can be displayed on screen.
    """

    def __init__(self, filename: str,
                 scale: Optional[float] = None,
                 propxsize: Optional[float] = None,
                 propysize: Optional[float] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None):
        """
        Create an image stimulus.

        Args:
            filename: Path to image file
            scale: Scale factor (multiplier)
            propxsize: Proportional width relative to screen width
            propysize: Proportional height relative to screen height
            width: Explicit width in pixels
            height: Explicit height in pixels
        """
        MediaFile.__init__(self, filename)
        Showable.__init__(self)

        self.scale = scale
        self.propxsize = propxsize
        self.propysize = propysize
        self.target_width = width
        self.target_height = height

        # Load image
        self.load()

    def load(self):
        """Load image from file."""
        if self._loaded:
            return

        try:
            # Load with PIL for better format support
            pil_image = PILImage.open(self.filename)

            # Convert to RGB if needed
            if pil_image.mode != 'RGB' and pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')

            # Convert PIL image to Pygame surface
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()

            self.surface = pygame.image.fromstring(data, size, mode)
            self._loaded = True

            # Apply scaling if specified
            self._applyScaling()

        except Exception as e:
            raise DisplayError(f"Failed to load image {self.filename}: {e}")

    def _applyScaling(self):
        """Apply scaling to the image."""
        if not self.surface:
            return

        original_size = self.surface.get_size()
        new_size = list(original_size)

        # Apply explicit dimensions
        if self.target_width:
            new_size[0] = self.target_width
        if self.target_height:
            new_size[1] = self.target_height

        # Apply scale factor
        if self.scale:
            new_size[0] = int(new_size[0] * self.scale)
            new_size[1] = int(new_size[1] * self.scale)

        # Apply proportional sizing (relative to screen)
        if self.propxsize or self.propysize:
            if pygame.display.get_surface():
                screen_width, screen_height = pygame.display.get_surface().get_size()

                if self.propysize:
                    # Size based on screen height (PyEPL default)
                    new_size[1] = int(screen_height * self.propysize)
                    # Maintain aspect ratio
                    aspect = original_size[0] / original_size[1]
                    new_size[0] = int(new_size[1] * aspect)

                if self.propxsize:
                    new_size[0] = int(screen_width * self.propxsize)
                    if not self.propysize:
                        # Maintain aspect ratio
                        aspect = original_size[1] / original_size[0]
                        new_size[1] = int(new_size[0] * aspect)

        # Only scale if size changed
        if new_size != list(original_size):
            self.surface = pygame.transform.scale(self.surface, new_size)


class Text(Showable):
    """
    Text stimulus that can be displayed on screen.
    """

    def __init__(self, text: str,
                 size: int = 30,
                 color: Color = WHITE,
                 font: Optional[str] = None,
                 width: Optional[int] = None):
        """
        Create text stimulus.

        Args:
            text: Text to display
            size: Font size in points
            color: Text color
            font: Path to font file (None = default)
            width: Maximum width for word wrapping
        """
        super().__init__()

        self.text = text
        self.size = size
        self.color = color
        self.font_path = font
        self.max_width = width

        # Initialize font
        pygame.font.init()
        if font and Path(font).exists():
            self.font = pygame.font.Font(font, size)
        else:
            self.font = pygame.font.Font(None, size)

        # Render text
        self.render()

    def render(self) -> pygame.Surface:
        """Render text to surface."""
        if self.max_width:
            # Word wrap
            lines = self._wrapText(self.text, self.max_width)
        else:
            lines = self.text.split('\n')

        # Render each line
        line_surfaces = []
        for line in lines:
            if line.strip():
                line_surf = self.font.render(line, True, self.color.tuple())
            else:
                # Empty line - create small transparent surface
                line_surf = pygame.Surface((1, self.font.get_height()))
                line_surf.set_alpha(0)
            line_surfaces.append(line_surf)

        if not line_surfaces:
            line_surfaces = [pygame.Surface((1, self.font.get_height()))]

        # Calculate total size
        max_width = max(surf.get_width() for surf in line_surfaces)
        total_height = sum(surf.get_height() for surf in line_surfaces)

        # Create combined surface
        self.surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparent background

        # Blit lines (center-aligned)
        y = 0
        for line_surf in line_surfaces:
            # Center each line horizontally
            x = (max_width - line_surf.get_width()) // 2
            self.surface.blit(line_surf, (x, y))
            y += line_surf.get_height()

        return self.surface

    def _wrapText(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_surf = self.font.render(test_line, True, (255, 255, 255))

            if test_surf.get_width() > max_width:
                if len(current_line) == 1:
                    # Word is too long, break it anyway
                    lines.append(test_line)
                    current_line = []
                else:
                    # Remove last word and start new line
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines


class CompoundStimulus(Showable):
    """
    Container for multiple showable objects with relative positioning.
    """

    def __init__(self, *children):
        """
        Create compound stimulus.

        Args:
            *children: Child showables to include
        """
        super().__init__()
        self.children: List[Showable] = list(children)

    def add(self, child: Showable):
        """Add a child showable."""
        self.children.append(child)

    def render(self) -> pygame.Surface:
        """Render all children to a single surface."""
        if not self.children:
            self.surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            return self.surface

        # Calculate bounding box
        min_x = min(child.position[0] for child in self.children)
        min_y = min(child.position[1] for child in self.children)
        max_x = max(child.position[0] + child.getSize()[0] for child in self.children)
        max_y = max(child.position[1] + child.getSize()[1] for child in self.children)

        width = max_x - min_x
        height = max_y - min_y

        # Create surface
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))

        # Render children
        for child in self.children:
            child_surf = child.render()
            offset_x = child.position[0] - min_x
            offset_y = child.position[1] - min_y
            self.surface.blit(child_surf, (offset_x, offset_y))

        return self.surface


class VideoTrack(LogTrack):
    """
    Video display track for managing screen output and logging display events.
    """

    def __init__(self, trackname: str = "video",
                 archive_dir: Optional[Path] = None,
                 resolution: Optional[Tuple[int, int]] = None,
                 fullscreen: bool = False,
                 background_color: Color = BLACK):
        """
        Initialize video track.

        Args:
            trackname: Name for this track
            archive_dir: Directory for log files
            resolution: Screen resolution (None = default)
            fullscreen: Whether to use fullscreen mode
            background_color: Background color
        """
        super().__init__(trackname, archive_dir, ".vidlog")

        pygame.init()
        pygame.display.init()

        # Set up display
        self.fullscreen = fullscreen
        self.background_color = background_color

        if resolution:
            self.resolution = resolution
        else:
            # Get default resolution
            display_info = pygame.display.Info()
            self.resolution = (display_info.current_w, display_info.current_h)

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(self.resolution, flags)
        pygame.display.set_caption("PyEPL3 Experiment")

        # Shown items tracking
        self.shown: List[Tuple[Showable, Tuple[int, int]]] = []

        # Clear screen
        self.clear()

    def _writeHeader(self):
        """Write log header."""
        if self.logfile:
            self.logfile.write("timestamp\ttick\tevent\tdetails\n")

    def clear(self, color: Optional[Color] = None):
        """
        Clear screen to background color.

        Args:
            color: Color to clear to (None = background color)
        """
        if color is None:
            color = self.background_color
        self.screen.fill(color.tuple())

    def updateScreen(self, clk: Optional[PresentationClock] = None) -> int:
        """
        Update the screen display.

        Args:
            clk: Presentation clock for timing

        Returns:
            Timestamp of update
        """
        pygame.display.flip()

        timestamp = now()
        if clk:
            timestamp = clk.get()

        # Log update
        self.logMessage(f"UPDATE\tscreen", timestamp)

        return timestamp

    def showCentered(self, showable: Showable,
                     clk: Optional[PresentationClock] = None) -> int:
        """
        Show a stimulus centered on screen.

        Args:
            showable: Showable object to display
            clk: Presentation clock

        Returns:
            Timestamp when shown
        """
        # Calculate center position
        screen_width, screen_height = self.resolution
        stim_width, stim_height = showable.getSize()

        x = (screen_width - stim_width) // 2
        y = (screen_height - stim_height) // 2

        return self.show(showable, (x, y), clk)

    def show(self, showable: Showable,
             position: Tuple[int, int],
             clk: Optional[PresentationClock] = None) -> int:
        """
        Show a stimulus at a specific position.

        Args:
            showable: Showable object to display
            position: (x, y) position
            clk: Presentation clock

        Returns:
            Timestamp when shown
        """
        showable.position = position
        showable._shown = True

        # Render to screen
        surface = showable.render()
        self.screen.blit(surface, position)

        # Track shown items
        self.shown.append((showable, position))

        timestamp = now()
        if clk:
            timestamp = clk.get()

        # Log show event
        self.logMessage(f"SHOW\t{type(showable).__name__}", timestamp)

        return timestamp

    def unshow(self, showable: Showable):
        """
        Remove a stimulus from screen.

        Args:
            showable: Showable to remove
        """
        # Remove from shown list
        self.shown = [(s, p) for s, p in self.shown if s is not showable]
        showable._shown = False

        # Log unshow
        self.logMessage(f"UNSHOW\t{type(showable).__name__}")

    def unshowAll(self):
        """Remove all shown stimuli."""
        for showable, _ in self.shown:
            showable._shown = False
        self.shown = []
        self.clear()

    def getResolution(self) -> Tuple[int, int]:
        """Get screen resolution."""
        return self.resolution

    def close(self):
        """Close the display."""
        pygame.display.quit()
        pygame.quit()

    def showInstructions(self, text: str,
                        clk: Optional[PresentationClock] = None,
                        size: int = 24,
                        color: Color = WHITE):
        """
        Display instructions and wait for keypress (SPACE or RETURN).

        This is a convenience method for showing instruction screens
        that are commonly used in experiments.

        Args:
            text: Instruction text to display
            clk: PresentationClock (optional)
            size: Font size
            color: Text color

        Returns:
            Timestamp when key was pressed
        """
        # Get keyboard track for input
        from .base import Registry
        from .keyboard import KeyTrack, Key, ButtonChooser

        keyboard_instances = Registry.getInstances(KeyTrack)
        keyboard = keyboard_instances[-1] if keyboard_instances else None

        if not keyboard:
            raise DisplayError("No KeyTrack found for showInstructions()")

        # Clear screen
        self.clear(BLACK)

        # Create instruction text
        instruction_text = Text(text, size=size, color=color)

        # Show centered
        self.showCentered(instruction_text, clk)
        self.updateScreen(clk)

        # Wait for SPACE or RETURN
        bc = ButtonChooser(Key("SPACE"), Key("RETURN"), track=keyboard)
        button, timestamp = bc.waitWithTime(clk)

        # Clear screen
        self.unshowAll()
        self.clear(BLACK)
        self.updateScreen(clk)

        # Clear pygame event queue to prevent event buildup
        pygame.event.clear()

        return timestamp

    def stopLogging(self):
        """Stop logging and clean up."""
        super().stopLogging()
        # Note: We don't close display here as it might still be needed
