"""
Custom exceptions for PyEPL3
"""


class PyEPL3Error(Exception):
    """Base exception for all PyEPL3 errors."""
    pass


class TrackError(PyEPL3Error):
    """Errors related to Track operations."""
    pass


class DisplayError(PyEPL3Error):
    """Errors related to display operations."""
    pass


class AudioError(PyEPL3Error):
    """Errors related to audio operations."""
    pass


class InputError(PyEPL3Error):
    """Errors related to input operations."""
    pass


class ConfigurationError(PyEPL3Error):
    """Errors related to configuration."""
    pass


class TimingError(PyEPL3Error):
    """Errors related to timing operations."""
    pass


class PoolError(PyEPL3Error):
    """Errors related to pool operations."""
    pass
