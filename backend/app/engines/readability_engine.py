"""
Readability Engine -- computes text readability metrics.

Metrics:
  - Flesch-Kincaid grade level
  - Reading time estimate (words / 200 wpm)
  - Word count, sentence count, avg sentence length, avg word length
  - Vocabulary richness (unique words / total words)
"""

import re
from dataclasses import dataclass


@dataclass
class ReadabilityResult:
    flesch_kincaid_grade: float = 0.0
    reading_time_seconds: int = 0
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    vocabulary_richness: float = 0.0


def _count_syllables(word: str) -> int:
    """Estimate syllable count for an English word."""
    word = word.lower().strip(".,;:!?\"'()-")
    if not word:
        return 0
    # Remove trailing silent-e
    if word.endswith("e") and len(word) > 2:
        word = word[:-1]
    # Count vowel groups
    vowel_groups = re.findall(r"[aeiouy]+", word)
    count = len(vowel_groups)
    return max(1, count)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Split on sentence-ending punctuation followed by space or end-of-string
    sentences = re.split(r"(?<=[.!?])\s+", text)
    # Also split on newlines that look like separate items (bullets, etc.)
    result = []
    for s in sentences:
        lines = s.split("\n")
        for line in lines:
            stripped = line.strip()
            # Remove bullet markers
            stripped = re.sub(r"^[•\-\*]\s*", "", stripped).strip()
            if stripped and len(stripped.split()) >= 2:
                result.append(stripped)
    return result


def _extract_words(text: str) -> list[str]:
    """Extract words from text, filtering out non-word tokens."""
    return [w for w in re.findall(r"[a-zA-Z]+(?:'[a-zA-Z]+)?", text) if len(w) > 0]


class ReadabilityEngine:
    """Computes readability metrics for a given text."""

    def analyze(self, text: str) -> ReadabilityResult:
        if not text or not text.strip():
            return ReadabilityResult()

        words = _extract_words(text)
        sentences = _split_sentences(text)

        word_count = len(words)
        sentence_count = max(len(sentences), 1)

        if word_count == 0:
            return ReadabilityResult()

        # Average sentence length
        avg_sentence_length = round(word_count / sentence_count, 1)

        # Average word length (in characters)
        total_chars = sum(len(w) for w in words)
        avg_word_length = round(total_chars / word_count, 1)

        # Total syllables
        total_syllables = sum(_count_syllables(w) for w in words)
        avg_syllables_per_word = total_syllables / word_count

        # Flesch-Kincaid Grade Level
        # FK = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        fk_grade = (
            0.39 * (word_count / sentence_count)
            + 11.8 * avg_syllables_per_word
            - 15.59
        )
        fk_grade = round(max(0.0, fk_grade), 1)

        # Reading time: 200 words per minute
        reading_time_seconds = round((word_count / 200) * 60)

        # Vocabulary richness: unique words / total words
        unique_words = set(w.lower() for w in words)
        vocabulary_richness = round(len(unique_words) / word_count, 3)

        return ReadabilityResult(
            flesch_kincaid_grade=fk_grade,
            reading_time_seconds=reading_time_seconds,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            vocabulary_richness=vocabulary_richness,
        )
