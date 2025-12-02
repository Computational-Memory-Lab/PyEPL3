"""
Base classes for PyEPL3

Provides foundational classes used throughout the library:
- Track: Base class for all trackable components
- LogTrack: Base class for logging systems
- Registry: Metaclass for automatic track registration
"""

import time
import weakref
from typing import Optional, Any, Dict, List, TextIO
from pathlib import Path


class Registry(type):
    """
    Metaclass that maintains a registry of all instances of a class.
    Used to track all Track instances for automatic management.
    """
    def __init__(cls, name, bases, dict):
        super(Registry, cls).__init__(name, bases, dict)
        cls._registry = weakref.WeakValueDictionary()
        cls._instances = []

    def __call__(cls, *args, **kwargs):
        instance = super(Registry, cls).__call__(*args, **kwargs)
        if hasattr(instance, 'trackname'):
            cls._registry[instance.trackname] = instance
        cls._instances.append(weakref.ref(instance))
        return instance

    @classmethod
    def getInstances(mcs, cls):
        """Get all live instances of a class."""
        return [ref() for ref in cls._instances if ref() is not None]


class Track(metaclass=Registry):
    """
    Base class for all trackable components in PyEPL3.

    Tracks represent sources of data (video, audio, keyboard, etc.)
    and can be started, stopped, and managed automatically.
    """

    def __init__(self, trackname: str = ""):
        """
        Initialize a track.

        Args:
            trackname: Unique name for this track
        """
        self.trackname = trackname
        self._started = False

    def startLogging(self):
        """Start logging for this track."""
        self._started = True

    def stopLogging(self):
        """Stop logging for this track."""
        self._started = False

    def isLogging(self) -> bool:
        """Check if track is currently logging."""
        return self._started

    def flush(self):
        """Flush any buffered data."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.startLogging()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stopLogging()
        return False


class LogTrack(Track):
    """
    Base class for tracks that log events to files.

    Creates tab-delimited log files with timestamps for all events.
    """

    def __init__(self, trackname: str, archive_dir: Optional[Path] = None,
                 extension: str = ".log"):
        """
        Initialize a log track.

        Args:
            trackname: Name for this track
            archive_dir: Directory to store log files (default: current directory)
            extension: File extension for log files
        """
        super().__init__(trackname)
        self.archive_dir = Path(archive_dir) if archive_dir else Path(".")
        self.extension = extension
        self.logfile: Optional[TextIO] = None
        self.filename: Optional[Path] = None
        self._tick = 0  # For ordering events within same timestamp

    def startLogging(self):
        """Start logging to file."""
        if not self._started:
            super().startLogging()
            # Create archive directory if needed
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            # Open log file
            self.filename = self.archive_dir / f"{self.trackname}{self.extension}"
            self.logfile = open(self.filename, 'w')
            self._writeHeader()

    def stopLogging(self):
        """Stop logging and close file."""
        if self._started:
            if self.logfile:
                self.flush()
                self.logfile.close()
                self.logfile = None
            super().stopLogging()

    def _writeHeader(self):
        """Write header row to log file. Override in subclasses."""
        if self.logfile:
            self.logfile.write("timestamp\ttick\tevent\n")

    def logMessage(self, message: str, timestamp: Optional[int] = None):
        """
        Log a message with timestamp.

        Args:
            message: Message to log
            timestamp: Timestamp in milliseconds (None = current time)
        """
        if not self._started or not self.logfile:
            return

        if timestamp is None:
            timestamp = int(time.time() * 1000)

        # Write log entry
        self.logfile.write(f"{timestamp}\t{self._tick}\t{message}\n")
        self._tick += 1

    def flush(self):
        """Flush buffered data to disk."""
        if self.logfile:
            self.logfile.flush()

    def __iter__(self):
        """Iterate over log entries (for reading logs)."""
        if self.filename and self.filename.exists():
            with open(self.filename, 'r') as f:
                # Skip header
                next(f)
                for line in f:
                    yield line.strip().split('\t')


class UniquelyConstructed:
    """
    Base class for objects that should only be constructed once
    with the same arguments (singleton pattern per arguments).
    """
    _instances: Dict[tuple, Any] = {}

    def __new__(cls, *args, **kwargs):
        # Create key from args and sorted kwargs
        key = (cls, args, tuple(sorted(kwargs.items())))

        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance

        return cls._instances[key]


class MediaFile:
    """
    Base class for media files (images, sounds, etc.).
    Provides common functionality for loading and managing media.
    """

    def __init__(self, filename: str):
        """
        Initialize media file.

        Args:
            filename: Path to media file
        """
        self.filename = Path(filename)
        if not self.filename.exists():
            raise FileNotFoundError(f"Media file not found: {filename}")

        self._loaded = False
        self._data = None

    def load(self):
        """Load media data into memory. Override in subclasses."""
        self._loaded = True

    def unload(self):
        """Unload media data from memory."""
        self._data = None
        self._loaded = False

    def isLoaded(self) -> bool:
        """Check if media is loaded in memory."""
        return self._loaded
