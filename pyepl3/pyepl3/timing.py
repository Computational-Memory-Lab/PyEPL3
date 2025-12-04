"""
Timing utilities for PyEPL3

Provides high-precision timing for experiments:
- PresentationClock: Virtual time management with jitter and error tracking
- Timing utilities: delays, waits, and precise time measurement
"""

import time
import random
from typing import Optional, Callable, Any
from .exceptions import TimingError


# Module-level time base
_time_base = time.perf_counter()


def now() -> int:
    """
    Get current time in milliseconds since module import.

    Returns:
        Current time in milliseconds
    """
    return int((time.perf_counter() - _time_base) * 1000)


def delay(milliseconds: int):
    """
    Delay for specified milliseconds using busy-wait for precision.

    Args:
        milliseconds: Time to delay in milliseconds
    """
    target = time.perf_counter() + (milliseconds / 1000.0)
    while time.perf_counter() < target:
        pass  # Busy wait for precision


def wait(until_time: int):
    """
    Wait until a specific time (in milliseconds).

    Args:
        until_time: Target time in milliseconds
    """
    current = now()
    if until_time > current:
        time.sleep((until_time - current) / 1000.0)


class PresentationClock:
    """
    Virtual clock for managing experiment timing.

    The PresentationClock maintains a virtual time that doesn't auto-advance.
    It provides precise control over experiment timing with jitter support,
    error tracking, and synchronization with real time.
    """

    def __init__(self, start_time: Optional[int] = None):
        """
        Initialize a presentation clock.

        Args:
            start_time: Starting time in milliseconds (None = current time)
        """
        if start_time is None:
            start_time = now()

        self._virtual_time = start_time
        self._real_base = time.perf_counter()
        self._accumulated_error = 0.0
        self._error_correction = True

    def get(self) -> int:
        """
        Get current virtual time.

        Returns:
            Virtual time in milliseconds
        """
        return self._virtual_time

    def tare(self, new_time: Optional[int] = None):
        """
        Reset the clock to a new time.

        Args:
            new_time: New virtual time (None = current real time)
        """
        if new_time is None:
            new_time = now()

        self._virtual_time = new_time
        self._real_base = time.perf_counter()
        self._accumulated_error = 0.0

    def delay(self, milliseconds: int, jitter: int = 0) -> int:
        """
        Advance virtual time and wait for real time to catch up.

        Args:
            milliseconds: Base delay in milliseconds
            jitter: Maximum random jitter to add (±jitter/2)

        Returns:
            Actual timestamp after delay
        """
        if jitter > 0:
            milliseconds += random.randint(-jitter // 2, jitter // 2)

        # Advance virtual time
        self._virtual_time += milliseconds

        # Wait for real time to catch up
        self.wait()

        return self._virtual_time

    def jitter(self, low: int, high: int) -> int:
        """
        Delay for a random amount between low and high.

        Args:
            low: Minimum delay in milliseconds
            high: Maximum delay in milliseconds

        Returns:
            Timestamp after delay
        """
        milliseconds = random.randint(low, high)
        return self.delay(milliseconds)

    def wait(self):
        """
        Block until real time catches up to virtual time.

        This handles timing drift and accumulated errors.
        """
        elapsed_real = (time.perf_counter() - self._real_base) * 1000
        target_time = self._virtual_time

        # Calculate how much time we need to wait
        wait_time = target_time - elapsed_real

        if wait_time > 0:
            # We're ahead of real time, need to wait
            time.sleep(wait_time / 1000.0)

            # Track error
            actual_elapsed = (time.perf_counter() - self._real_base) * 1000
            error = actual_elapsed - target_time
            self._accumulated_error += error

        elif wait_time < -100:
            # We're more than 100ms behind real time
            if self._error_correction:
                # Sync real_base so elapsed_real equals virtual_time
                self._real_base = time.perf_counter() - (self._virtual_time / 1000.0)
                self._accumulated_error = 0.0

    def getAccumulatedError(self) -> float:
        """
        Get accumulated timing error in milliseconds.

        Returns:
            Accumulated error in milliseconds
        """
        return self._accumulated_error

    def setErrorCorrection(self, enabled: bool):
        """
        Enable or disable automatic error correction.

        Args:
            enabled: Whether to enable error correction
        """
        self._error_correction = enabled

    def timedCall(self, target_time: int, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function at a precise virtual time.

        Args:
            target_time: Time to execute function (in virtual time)
            func: Function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Return value of function
        """
        # Wait until target time
        wait_duration = target_time - self._virtual_time
        if wait_duration > 0:
            self.delay(wait_duration)
        elif wait_duration < 0:
            raise TimingError(f"Target time {target_time} is in the past (current: {self._virtual_time})")

        # Call function
        return func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"PresentationClock(virtual={self._virtual_time}ms, error={self._accumulated_error:.2f}ms)"
