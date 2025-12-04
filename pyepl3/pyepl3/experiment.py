"""
Experiment management for PyEPL3

Provides the main Experiment class and configuration system for managing
psychology experiments, including session handling, data archiving, and
configuration management.
"""

import sys
import pickle
import shutil
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .exceptions import ConfigurationError
from .base import Track, Registry


class Configuration:
    """
    Base configuration class providing dictionary-like access to config values.
    """

    def __init__(self):
        self.config: Dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to config values."""
        if name.startswith('_') or name == 'config':
            return object.__getattribute__(self, name)
        if name not in self.config:
            raise AttributeError(f"Configuration has no attribute '{name}'")
        return self.config[name]

    def __setattr__(self, name: str, value: Any):
        """Allow attribute assignment to config values."""
        if name == 'config':
            object.__setattr__(self, name, value)
        else:
            self.config[name] = value

    def __getitem__(self, name: str) -> Any:
        """Allow dictionary-style access."""
        return self.config[name]

    def __setitem__(self, name: str, value: Any):
        """Allow dictionary-style assignment."""
        self.config[name] = value

    def __contains__(self, name: str) -> bool:
        """Check if config contains a key."""
        return name in self.config

    def get(self, name: str, default: Any = None) -> Any:
        """Get config value with default."""
        return self.config.get(name, default)

    def update(self, other: Dict[str, Any]):
        """Update configuration with another dictionary."""
        self.config.update(other)


class ConfigurationFile(Configuration):
    """
    Configuration loaded from a Python file.

    Executes the file in a namespace and makes all defined variables available.
    """

    def __init__(self, filename: str, parent: Optional[Configuration] = None):
        """
        Load configuration from Python file.

        Args:
            filename: Path to config file
            parent: Parent configuration to inherit from
        """
        super().__init__()

        config_file = Path(filename)
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {filename}")

        # Set up namespace for config file
        namespace = {'config': self}

        # Inherit from parent if provided
        if parent:
            self.config.update(parent.config)

        # Execute config file
        with open(config_file, 'r') as f:
            code = compile(f.read(), filename, 'exec')
            exec(code, namespace, self.config)


class State:
    """
    Experiment state that can be saved and restored.

    Allows experiments to be interrupted and resumed.
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to state data."""
        if name == 'data':
            return object.__getattribute__(self, name)
        if name not in self.data:
            raise AttributeError(f"State has no attribute '{name}'")
        return self.data[name]

    def __setattr__(self, name: str, value: Any):
        """Allow attribute assignment to state data."""
        if name == 'data':
            object.__setattr__(self, name, value)
        else:
            self.data[name] = value

    def __getitem__(self, name: str) -> Any:
        return self.data[name]

    def __setitem__(self, name: str, value: Any):
        self.data[name] = value


class Experiment:
    """
    Main experiment class managing sessions, configuration, and data archiving.
    """

    def __init__(self, name: str = "experiment", use_args: bool = True):
        """
        Initialize experiment.

        Args:
            name: Experiment name
            use_args: Whether to parse command-line arguments
        """
        self.name = name
        self.subject = None
        self.session = None
        self.config = Configuration()
        self.state = State()

        # Parse command-line arguments
        if use_args:
            self._parseArgs()

        # Set up directories
        self.data_dir = Path("data")
        self.subject_dir = None
        self.session_dir = None
        self.state_dir = None

        if self.subject:
            self._setupDirectories()

    def _parseArgs(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description=f"{self.name} experiment")
        parser.add_argument('subject', nargs='?', help='Subject ID')
        parser.add_argument('-s', '--subject-alt', dest='subject_alt', help='Subject ID (alternative to positional)')
        parser.add_argument('--session', help='Session name')
        parser.add_argument('-c', '--config', help='Config file path')

        args = parser.parse_args()

        # Support both positional and -s flag for subject (like original PyEPL)
        self.subject = args.subject or args.subject_alt
        self.session = args.session or "session_0"

        # Load config file if specified
        if args.config:
            self.config = ConfigurationFile(args.config)

    def _setupDirectories(self):
        """Set up directory structure for data storage."""
        # Subject directory
        self.subject_dir = self.data_dir / str(self.subject)
        self.subject_dir.mkdir(parents=True, exist_ok=True)

        # Session directory
        self.session_dir = self.subject_dir / self.session
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # State directory
        self.state_dir = self.subject_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Config backup directory
        config_backup_dir = self.subject_dir / "configbackup"
        config_backup_dir.mkdir(parents=True, exist_ok=True)

    def getConfig(self) -> Configuration:
        """
        Get experiment configuration.

        Returns:
            Configuration object
        """
        return self.config

    def setConfig(self, config: Configuration):
        """
        Set experiment configuration.

        Args:
            config: Configuration object
        """
        self.config = config

    def loadConfig(self, filename: str):
        """
        Load configuration from file.

        Args:
            filename: Path to config file
        """
        self.config = ConfigurationFile(filename, parent=self.config)

    def getState(self) -> State:
        """
        Get experiment state.

        Returns:
            State object
        """
        return self.state

    def saveState(self, name: Optional[str] = None):
        """
        Save current experiment state.

        Args:
            name: State name (default: timestamped)
        """
        if not self.state_dir:
            raise ConfigurationError("Cannot save state: no subject directory")

        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"state_{timestamp}"

        state_file = self.state_dir / f"{name}.pkl"

        with open(state_file, 'wb') as f:
            pickle.dump(self.state.data, f)

    def restoreState(self, name: Optional[str] = None):
        """
        Restore experiment state.

        Args:
            name: State name (default: most recent)
        """
        if not self.state_dir:
            raise ConfigurationError("Cannot restore state: no subject directory")

        if name is None:
            # Find most recent state file
            state_files = list(self.state_dir.glob("state_*.pkl"))
            if not state_files:
                raise ConfigurationError("No saved states found")
            state_file = max(state_files, key=lambda p: p.stat().st_mtime)
        else:
            state_file = self.state_dir / f"{name}.pkl"

        if not state_file.exists():
            raise ConfigurationError(f"State file not found: {state_file}")

        with open(state_file, 'rb') as f:
            self.state.data = pickle.load(f)

    def getArchive(self) -> Optional[Path]:
        """
        Get the current session archive directory.

        Returns:
            Path to session directory
        """
        return self.session_dir

    def setBreak(self):
        """
        Set up break key handling.

        In original PyEPL this was Escape+F1. For now we'll handle this
        in individual track implementations.
        """
        # TODO: Implement global break key handling
        pass

    def cleanup(self):
        """
        Clean up experiment resources.

        Stops all tracks and closes files.
        """
        # Stop all tracks
        for track_class in [Track]:
            instances = Registry.getInstances(track_class)
            for track in instances:
                if track and track.isLogging():
                    track.stopLogging()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False
