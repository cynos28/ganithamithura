"""
Number Extraction Module

Extracts numeric answers from speech with high accuracy.
Handles word numbers, digit numbers, and phonetic variations.
"""

import re
from typing import Optional


class NumberExtractor:
    """Extract numbers from speech with high accuracy."""

    # Word to number mapping
    WORD_TO_NUMBER = {
        # Zero
        'zero': 0, 'oh': 0,
        # Ones
        'one': 1, 'won': 1, 'wan': 1,
        'two': 2, 'to': 2, 'too': 2, 'tu': 2,
        'three': 3, 'tree': 3, 'free': 3,
        'four': 4, 'for': 4, 'fore': 4, 'floor': 4,
        'five': 5, 'hive': 5, 'dive': 5,
        'six': 6, 'sex': 6, 'sicks': 6, 'sick': 6,
        'seven': 7, 'heaven': 7,
        'eight': 8, 'ate': 8, 'weight': 8, 'gate': 8,
        'nine': 9, 'wine': 9, 'nein': 9, 'mine': 9,
        # Teens
        'ten': 10, 'pen': 10, 'hen': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13, 'thirty': 30,
        'fourteen': 14, 'forty': 40,
        'fifteen': 15, 'fifty': 50,
        'sixteen': 16, 'sixty': 60,
        'seventeen': 17, 'seventy': 70,
        'eighteen': 18, 'eighty': 80,
        'nineteen': 19, 'ninety': 90,
        'twenty': 20,
        # Larger numbers
        'hundred': 100,
        'thousand': 1000,
    }

    @staticmethod
    def extract(speech: str) -> Optional[int]:
        """
        Extract a number from speech text.

        Args:
            speech: Speech text to extract number from

        Returns:
            Extracted number, or None if no valid number found
        """
        if not speech:
            return None

        speech_lower = speech.lower().strip()
        print(f"🔍 Extracting number from: '{speech_lower}'")

        # Try exact word match first (most accurate)
        number = NumberExtractor._extract_word_number(speech_lower)
        if number is not None:
            print(f"✅ Found word number: {number}")
            return number

        # Try digit extraction
        number = NumberExtractor._extract_digit_number(speech_lower)
        if number is not None:
            print(f"✅ Found digit number: {number}")
            return number

        # Try phonetic variations
        number = NumberExtractor._extract_phonetic_number(speech_lower)
        if number is not None:
            print(f"✅ Found phonetic number: {number}")
            return number

        print(f"❌ No number found in '{speech_lower}'")
        return None

    @staticmethod
    def _extract_word_number(speech: str) -> Optional[int]:
        """
        Extract number from word representation.

        Args:
            speech: Lowercase speech text

        Returns:
            Number if found, None otherwise
        """
        # Direct word match
        for word, value in NumberExtractor.WORD_TO_NUMBER.items():
            # Use word boundaries to match complete words
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, speech):
                return value

        return None

    @staticmethod
    def _extract_digit_number(speech: str) -> Optional[int]:
        """
        Extract number from digit representation.

        Args:
            speech: Lowercase speech text

        Returns:
            Number if found, None otherwise
        """
        # Look for standalone digits or numbers
        digit_matches = re.findall(r'\b(\d+)\b', speech)
        if digit_matches:
            # Return the first number found
            return int(digit_matches[0])

        return None

    @staticmethod
    def _extract_phonetic_number(speech: str) -> Optional[int]:
        """
        Extract number from phonetic variations.

        Args:
            speech: Lowercase speech text

        Returns:
            Number if found, None otherwise
        """
        # Handle special phonetic patterns
        phonetic_patterns = {
            r'\bone\b': 1,
            r'\btwo\b|\btu\b': 2,
            r'\bthree\b|\btree\b': 3,
            r'\bfour\b|\bfor\b': 4,
            r'\bfive\b': 5,
            r'\bsix\b': 6,
            r'\bseven\b': 7,
            r'\beight\b|\bate\b': 8,
            r'\bnine\b': 9,
            r'\bten\b': 10,
        }

        for pattern, value in phonetic_patterns.items():
            if re.search(pattern, speech):
                return value

        return None

    @staticmethod
    def is_valid_answer(number: Optional[int], expected_type: str = 'integer') -> bool:
        """
        Validate extracted number.

        Args:
            number: Extracted number
            expected_type: Type of expected number (integer, positive, etc.)

        Returns:
            True if valid, False otherwise
        """
        if number is None:
            return False

        if expected_type == 'integer':
            return isinstance(number, int)
        elif expected_type == 'positive':
            return isinstance(number, int) and number > 0
        elif expected_type == 'non_negative':
            return isinstance(number, int) and number >= 0

        return True
