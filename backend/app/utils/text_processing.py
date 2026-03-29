import re
import html
import unicodedata
from collections import Counter
from dataclasses import dataclass


@dataclass
class NumberMatch:
    value: float
    raw: str
    number_type: str  # percentage, count, duration, currency, multiplier
    context: str


@dataclass
class ReadabilityScore:
    flesch_kincaid_grade: float
    avg_sentence_length: float
    avg_word_length: float


ABBREVIATIONS = {
    "dr", "mr", "mrs", "ms", "jr", "sr", "inc", "ltd", "corp", "dept",
    "univ", "prof", "assoc", "govt", "approx", "etc", "vs", "jan", "feb",
    "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "st", "ave", "blvd", "e.g", "i.e",
}


def clean_text(text: str) -> str:
    try:
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        text = unicodedata.normalize("NFKD", text)
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2013", "-").replace("\u2014", "-")
        text = re.sub(r"[\u200b\u200c\u200d\ufeff\u00ad]", "", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[^\S\n]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
    except Exception:
        text = text.strip() if text else ""
    return text


def tokenize_sentences(text: str) -> list[str]:
    try:
        if not text.strip():
            return []
        abbrev_pattern = "|".join(re.escape(a) for a in ABBREVIATIONS)
        placeholder_text = text
        abbrev_matches: list[tuple[str, str]] = []
        for match in re.finditer(rf"(?i)\b({abbrev_pattern})\.", placeholder_text):
            placeholder = f"__ABBREV{len(abbrev_matches)}__"
            abbrev_matches.append((placeholder, match.group(0)))
            placeholder_text = placeholder_text.replace(match.group(0), placeholder, 1)

        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", placeholder_text)

        result = []
        for sent in sentences:
            for placeholder, original in abbrev_matches:
                sent = sent.replace(placeholder, original)
            sent = sent.strip()
            if sent:
                result.append(sent)
        return result
    except Exception:
        return [s.strip() for s in text.split(".") if s.strip()]


def tokenize_bullets(text: str) -> list[str]:
    try:
        if not text.strip():
            return []
        lines = text.split("\n")
        bullets: list[str] = []
        current_bullet = ""
        bullet_pattern = re.compile(r"^\s*(?:[•\-\*▪◦►]|\d+[.)]\s)")

        for line in lines:
            line = line.strip()
            if not line:
                if current_bullet:
                    bullets.append(current_bullet.strip())
                    current_bullet = ""
                continue

            if bullet_pattern.match(line):
                if current_bullet:
                    bullets.append(current_bullet.strip())
                cleaned = re.sub(r"^\s*(?:[•\-\*▪◦►]|\d+[.)]\s)\s*", "", line)
                current_bullet = cleaned
            else:
                if current_bullet:
                    current_bullet += " " + line
                else:
                    current_bullet = line

        if current_bullet:
            bullets.append(current_bullet.strip())

        return [b for b in bullets if b]
    except Exception:
        return [line.strip() for line in text.split("\n") if line.strip()]


def count_words(text: str) -> int:
    try:
        return len(text.split()) if text.strip() else 0
    except Exception:
        return 0


def extract_numbers(text: str) -> list[NumberMatch]:
    results: list[NumberMatch] = []
    try:
        if not text:
            return results

        patterns = [
            (r"(\d+(?:\.\d+)?)\s*%", "percentage"),
            (r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:M|K|B)?", "currency"),
            (r"(\d+(?:\.\d+)?)\s*[xX]\b", "multiplier"),
            (r"(\d+)\+?\s*(?:years?|yrs?)", "duration"),
        ]

        for pattern, num_type in patterns:
            for match in re.finditer(pattern, text):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].strip()
                try:
                    value = float(match.group(1).replace(",", ""))
                except (ValueError, IndexError):
                    continue
                results.append(NumberMatch(
                    value=value, raw=match.group(0), number_type=num_type, context=context,
                ))

        # Generic numbers not caught above
        for match in re.finditer(r"\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b", text):
            raw = match.group(0)
            if not any(raw in r.raw for r in results):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                try:
                    value = float(raw.replace(",", ""))
                except ValueError:
                    continue
                results.append(NumberMatch(
                    value=value, raw=raw, number_type="count", context=text[start:end].strip(),
                ))
    except Exception:
        pass
    return results


def calculate_readability(text: str) -> ReadabilityScore:
    try:
        sentences = tokenize_sentences(text)
        if not sentences:
            return ReadabilityScore(flesch_kincaid_grade=0.0, avg_sentence_length=0.0, avg_word_length=0.0)

        words = text.split()
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(_count_syllables(w) for w in words)

        avg_sentence_length = total_words / max(total_sentences, 1)
        avg_word_length = sum(len(w) for w in words) / max(total_words, 1)

        # Flesch-Kincaid Grade Level
        if total_words > 0 and total_sentences > 0:
            fk_grade = (
                0.39 * (total_words / total_sentences)
                + 11.8 * (total_syllables / total_words)
                - 15.59
            )
        else:
            fk_grade = 0.0

        return ReadabilityScore(
            flesch_kincaid_grade=round(fk_grade, 2),
            avg_sentence_length=round(avg_sentence_length, 2),
            avg_word_length=round(avg_word_length, 2),
        )
    except Exception:
        return ReadabilityScore(flesch_kincaid_grade=0.0, avg_sentence_length=0.0, avg_word_length=0.0)


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:\"'")
    if not word:
        return 1
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "it", "its", "this", "that", "these", "those",
    "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "they", "them", "their", "what", "which", "who",
    "whom", "where", "when", "why", "how", "not", "no", "nor", "as",
    "if", "then", "than", "so", "up", "out", "about", "into", "over",
    "after", "before", "between", "under", "again", "further", "once",
}


def compute_text_analytics(text: str) -> dict:
    """Compute word-level analytics for a given text."""
    try:
        if not text or not text.strip():
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "avg_sentence_length": 0.0,
                "avg_word_length": 0.0,
                "vocabulary_richness": 0.0,
                "longest_sentence": 0,
                "shortest_sentence": 0,
                "top_words": [],
            }

        words = text.split()
        word_count = len(words)
        character_count = len(text)

        sentences = tokenize_sentences(text)
        sentence_count = len(sentences) if sentences else 0

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs) if paragraphs else 1

        sentence_lengths = [len(s.split()) for s in sentences] if sentences else [0]
        avg_sentence_length = round(sum(sentence_lengths) / max(len(sentence_lengths), 1), 2)
        longest_sentence = max(sentence_lengths) if sentence_lengths else 0
        shortest_sentence = min(sentence_lengths) if sentence_lengths else 0

        clean_words = [re.sub(r"[^\w]", "", w.lower()) for w in words]
        clean_words = [w for w in clean_words if w]
        avg_word_length = round(
            sum(len(w) for w in clean_words) / max(len(clean_words), 1), 2
        )

        unique_words = set(clean_words)
        vocabulary_richness = round(
            len(unique_words) / max(len(clean_words), 1), 4
        )

        # Top 10 most frequent non-stop words
        non_stop = [w for w in clean_words if w not in _STOP_WORDS and len(w) > 1]
        word_freq = Counter(non_stop)
        top_words = word_freq.most_common(10)

        return {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "vocabulary_richness": vocabulary_richness,
            "longest_sentence": longest_sentence,
            "shortest_sentence": shortest_sentence,
            "top_words": top_words,
        }
    except Exception:
        return {
            "word_count": 0,
            "character_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "avg_sentence_length": 0.0,
            "avg_word_length": 0.0,
            "vocabulary_richness": 0.0,
            "longest_sentence": 0,
            "shortest_sentence": 0,
            "top_words": [],
        }
