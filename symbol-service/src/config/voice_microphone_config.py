"""
Voice and Microphone Configuration for Math Tutors

Manages:
- Voice system setup (macOS 'say' command vs text-only)
- Voice selection and speech settings
- Microphone configuration and calibration
- Speech recognition settings
"""

import subprocess
from typing import Optional, List


class VoiceConfig:
    """Configuration for voice system and text-to-speech settings."""

    # Voice method options
    VOICE_METHODS = ['macos_say', 'text_only']
    DEFAULT_VOICE_METHOD = 'text_only'

    # Preferred voice names for macOS
    PREFERRED_VOICE_NAMES = ['samantha', 'alex', 'allison', 'ava', 'karen', 'susan', 'victoria']

    # Speech settings
    SPEECH_RATE = 120  # Words per minute (slower for clarity)
    SPEAK_TIMEOUT = 15  # Seconds
    VOICE_LIST_TIMEOUT = 5  # Seconds to fetch available voices

    @staticmethod
    def detect_voice_method() -> str:
        """
        Detect the best available voice method for the system.

        Returns:
            'macos_say' if available, else 'text_only'
        """
        try:
            result = subprocess.run(['which', 'say'],
                                  capture_output=True,
                                  timeout=2,
                                  text=True)
            if result.returncode == 0:
                return 'macos_say'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return 'text_only'

    @staticmethod
    def get_available_voices() -> List[str]:
        """
        Get list of available macOS voices.

        Returns:
            List of voice names, or empty list if unavailable
        """
        try:
            result = subprocess.run(['say', '-v', '?'],
                                  capture_output=True,
                                  text=True,
                                  timeout=VoiceConfig.VOICE_LIST_TIMEOUT)
            voices = [line.split()[0] for line in result.stdout.strip().split('\n') if line]
            return voices
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return []

    @staticmethod
    def select_preferred_voice(available_voices: List[str]) -> Optional[str]:
        """
        Select a preferred voice from available voices.

        Args:
            available_voices: List of available voice names

        Returns:
            Preferred voice name, or None if none match preferences
        """
        for voice in available_voices:
            if any(name in voice.lower() for name in VoiceConfig.PREFERRED_VOICE_NAMES):
                return voice
        return None


class MicrophoneConfig:
    """Configuration for microphone setup and speech recognition."""

    # Microphone detection
    PREFERRED_MIC_KEYWORDS = ["MacBook", "Microphone"]

    # Speech recognition settings
    ENERGY_THRESHOLD = 300
    DYNAMIC_ENERGY_THRESHOLD = True
    PAUSE_THRESHOLD = 1.0

    # Ambient noise calibration
    CALIBRATION_DURATION = 3  # Seconds
    LISTEN_TIMEOUT = 15  # Seconds
    PHRASE_TIME_LIMIT = 8  # Seconds per phrase
    GOOGLE_API_TIMEOUT = 10  # Seconds for Google Speech-to-Text API

    # Ambient noise adjustment during listening
    LISTEN_AMBIENT_DURATION = 0.5  # Seconds

    @staticmethod
    def select_microphone_device(mic_list: List[str]) -> Optional[int]:
        """
        Select the best microphone device from available list.

        Args:
            mic_list: List of available microphone names

        Returns:
            Device index of preferred microphone, or None to use default
        """
        for i, name in enumerate(mic_list):
            if all(keyword in name for keyword in MicrophoneConfig.PREFERRED_MIC_KEYWORDS):
                return i
        return None

    @staticmethod
    def get_recognizer_settings() -> dict:
        """
        Get speech recognizer configuration settings.

        Returns:
            Dictionary of recognizer settings
        """
        return {
            'energy_threshold': MicrophoneConfig.ENERGY_THRESHOLD,
            'dynamic_energy_threshold': MicrophoneConfig.DYNAMIC_ENERGY_THRESHOLD,
            'pause_threshold': MicrophoneConfig.PAUSE_THRESHOLD,
        }
