"""
Audio system for PyEPL3

Provides audio playback with precise timing, multi-format support,
and event logging.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple
import threading

from .base import LogTrack, MediaFile
from .timing import PresentationClock, now
from .exceptions import AudioError


class AudioTrack(LogTrack):
    """
    Audio track for logging audio playback events.
    """

    def __init__(self, trackname: str = "audio",
                 archive_dir: Optional[Path] = None,
                 sample_rate: int = 44100):
        """
        Initialize audio track.

        Args:
            trackname: Name for this track
            archive_dir: Directory for log files
            sample_rate: Sample rate for audio playback (Hz)
        """
        super().__init__(trackname, archive_dir, ".sndlog")
        self.sample_rate = sample_rate

        # Initialize audio system
        sd.default.samplerate = sample_rate
        sd.default.channels = 2

    def _writeHeader(self):
        """Write log header."""
        if self.logfile:
            self.logfile.write("timestamp\ttick\tevent\tdetails\n")


class FileAudioClip(MediaFile):
    """
    Audio clip loaded from a file.
    """

    def __init__(self, filename: str,
                 sample_rate: Optional[int] = None):
        """
        Create audio clip from file.

        Args:
            filename: Path to audio file
            sample_rate: Target sample rate (None = file's native rate)
        """
        super().__init__(filename)
        self.target_sample_rate = sample_rate
        self.data: Optional[np.ndarray] = None
        self.file_sample_rate: Optional[int] = None
        self.duration_ms: int = 0

        # Load audio
        self.load()

    def load(self):
        """Load audio file."""
        if self._loaded:
            return

        try:
            # Load audio file
            data, sample_rate = sf.read(str(self.filename), always_2d=True)

            self.file_sample_rate = sample_rate
            self.data = data

            # Resample if needed
            if self.target_sample_rate and self.target_sample_rate != sample_rate:
                self.data = self._resample(data, sample_rate, self.target_sample_rate)
                self.file_sample_rate = self.target_sample_rate

            # Calculate duration
            self.duration_ms = int((len(self.data) / self.file_sample_rate) * 1000)

            self._loaded = True

        except Exception as e:
            raise AudioError(f"Failed to load audio file {self.filename}: {e}")

    def _resample(self, data: np.ndarray, old_rate: int, new_rate: int) -> np.ndarray:
        """
        Resample audio data.

        Args:
            data: Audio data
            old_rate: Original sample rate
            new_rate: Target sample rate

        Returns:
            Resampled audio data
        """
        if old_rate == new_rate:
            return data

        # Simple linear interpolation resampling
        duration = len(data) / old_rate
        new_length = int(duration * new_rate)

        # Create time arrays
        old_time = np.linspace(0, duration, len(data))
        new_time = np.linspace(0, duration, new_length)

        # Interpolate each channel
        resampled = np.zeros((new_length, data.shape[1]))
        for ch in range(data.shape[1]):
            resampled[:, ch] = np.interp(new_time, old_time, data[:, ch])

        return resampled

    def present(self, clk: Optional[PresentationClock] = None,
                track: Optional[AudioTrack] = None,
                block: bool = True) -> int:
        """
        Play the audio clip.

        Args:
            clk: Presentation clock
            track: Audio track for logging
            block: Whether to block until playback completes

        Returns:
            Timestamp when playback started
        """
        if not self._loaded or self.data is None:
            raise AudioError("Audio not loaded")

        timestamp = now()
        if clk:
            timestamp = clk.get()

        # Log playback start
        if track and track.isLogging():
            track.logMessage(f"PLAY\t{self.filename.name}", timestamp)

        # Play audio
        if block:
            sd.play(self.data, self.file_sample_rate)
            sd.wait()  # Wait until playback finishes

            # Log playback end
            if track and track.isLogging():
                end_timestamp = now()
                if clk:
                    end_timestamp = clk.get()
                track.logMessage(f"STOP\t{self.filename.name}", end_timestamp)
        else:
            # Non-blocking playback
            sd.play(self.data, self.file_sample_rate)

        return timestamp

    def getDuration(self) -> int:
        """
        Get duration in milliseconds.

        Returns:
            Duration in milliseconds
        """
        return self.duration_ms

    def stop(self):
        """Stop playback."""
        sd.stop()


class Beep:
    """
    Simple tone generator for creating beeps.
    """

    def __init__(self, frequency: int = 440,
                 duration_ms: int = 500,
                 sample_rate: int = 44100,
                 volume: float = 0.5):
        """
        Create a beep tone.

        Args:
            frequency: Frequency in Hz
            duration_ms: Duration in milliseconds
            sample_rate: Sample rate
            volume: Volume (0.0 to 1.0)
        """
        self.frequency = frequency
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.volume = min(1.0, max(0.0, volume))

        # Generate tone
        self.data = self._generate()

    def _generate(self) -> np.ndarray:
        """Generate the beep waveform."""
        duration_sec = self.duration_ms / 1000.0
        samples = int(self.sample_rate * duration_sec)

        # Generate sine wave
        t = np.linspace(0, duration_sec, samples)
        wave = np.sin(2 * np.pi * self.frequency * t)

        # Apply envelope (fade in/out to prevent clicks)
        envelope_samples = int(self.sample_rate * 0.01)  # 10ms fade
        envelope = np.ones_like(wave)

        # Fade in
        envelope[:envelope_samples] = np.linspace(0, 1, envelope_samples)

        # Fade out
        envelope[-envelope_samples:] = np.linspace(1, 0, envelope_samples)

        wave = wave * envelope * self.volume

        # Make stereo
        stereo = np.column_stack([wave, wave])

        return stereo

    def present(self, clk: Optional[PresentationClock] = None,
                track: Optional[AudioTrack] = None,
                block: bool = True) -> int:
        """
        Play the beep.

        Args:
            clk: Presentation clock
            track: Audio track for logging
            block: Whether to block until playback completes

        Returns:
            Timestamp when playback started
        """
        timestamp = now()
        if clk:
            timestamp = clk.get()

        # Log beep
        if track and track.isLogging():
            track.logMessage(f"BEEP\t{self.frequency}Hz", timestamp)

        # Play beep
        if block:
            sd.play(self.data, self.sample_rate)
            sd.wait()
        else:
            sd.play(self.data, self.sample_rate)

        return timestamp

    def getDuration(self) -> int:
        """Get duration in milliseconds."""
        return self.duration_ms
