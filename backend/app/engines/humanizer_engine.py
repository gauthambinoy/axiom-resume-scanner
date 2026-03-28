"""
Humanizer Engine — rewrites AI-flagged resume text so that no AI detector can flag it.

Multi-layer approach:
  Layer 1: ML paraphrasing via HuggingFace Inference API (free tier)
  Layer 2: Heavy rule-based transformations (local, no API needed)
  Layer 3: Self-verification loop using our own AI detection engine

The rule-based layer is strong enough to work WITHOUT any API key.
"""

import os
import re
import random
import statistics
from dataclasses import dataclass, field
from typing import Optional

import httpx

from app.engines.constants import (
    BANNED_PHRASES,
    BANNED_EXTENDED_WORDS,
    AI_STRUCTURE_PATTERNS,
    ROUND_NUMBERS,
    TRANSITIONAL_OPENERS,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# HuggingFace Inference API config
# ---------------------------------------------------------------------------
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_PRIMARY_MODEL = "humarin/chatgpt_paraphraser_on_T5_base"
HF_TIMEOUT = 30  # seconds

# ---------------------------------------------------------------------------
# Banned word/phrase replacement maps
# ---------------------------------------------------------------------------
BANNED_WORD_REPLACEMENTS: dict[str, list[str]] = {
    # AI-telltale verbs
    "leveraged": ["used", "relied on", "tapped"],
    "orchestrated": ["ran", "coordinated", "managed"],
    "spearheaded": ["led", "kicked off", "started"],
    "facilitated": ["helped", "supported", "enabled"],
    "utilized": ["used", "applied"],
    "utilizing": ["using"],
    "implemented": ["built", "set up", "rolled out", "shipped"],
    "architected": ["designed", "planned out"],
    "conceptualized": ["came up with", "designed"],
    "streamlined": ["simplified", "cleaned up", "tightened"],
    "optimized": ["sped up", "tuned", "improved"],
    "cultivated": ["built", "grew"],
    "fostered": ["encouraged", "built"],
    "championed": ["pushed for", "advocated"],
    "evangelized": ["promoted", "pushed"],
    "propelled": ["drove", "pushed"],
    "catalyzed": ["triggered", "kicked off"],
    "galvanized": ["rallied", "motivated"],
    "navigated": ["worked through", "handled"],
    "traversed": ["went through", "covered"],
    "ameliorated": ["fixed", "improved"],
    "augmented": ["added to", "expanded"],
    "bolstered": ["strengthened", "boosted"],
    "buttressed": ["supported", "backed up"],
    "fortified": ["strengthened", "hardened"],
    "engendered": ["created", "produced"],
    "envisioned": ["imagined", "planned"],
    "innovated": ["created", "introduced"],
    "ideated": ["brainstormed", "came up with"],
    "operationalized": ["put into practice", "launched"],
    "revolutionized": ["transformed", "overhauled"],
    "oversaw": ["managed", "ran"],
    # AI-telltale adjectives / adverbs
    "delve": ["dig into", "explore"],
    "pivotal": ["key", "important", "major"],
    "intricate": ["complex", "detailed"],
    "showcasing": ["showing", "demonstrating"],
    "holistic": ["full", "complete", "overall"],
    "transformative": ["major", "significant"],
    "meticulous": ["careful", "thorough"],
    "robust": ["solid", "strong", "reliable"],
    "scalable": ["flexible", "growable"],
    "impactful": ["meaningful", "effective"],
    "actionable": ["practical", "useful"],
    "comprehensive": ["full", "complete", "thorough"],
    "seamlessly": ["smoothly", "cleanly"],
    "meticulously": ["carefully", "thoroughly"],
    "rigorously": ["strictly", "carefully"],
    "diligently": ["carefully", "steadily"],
    "proactively": ["early on", "ahead of time"],
    "strategically": ["thoughtfully", "deliberately"],
    # AI-telltale nouns
    "synergy": ["teamwork", "collaboration"],
    "paradigm": ["model", "approach"],
    "ecosystem": ["system", "environment", "setup"],
    "landscape": ["space", "area", "field"],
    "realm": ["area", "space"],
    "cornerstone": ["foundation", "base"],
    "linchpin": ["key part", "core piece"],
    "bedrock": ["foundation", "base"],
    "nexus": ["center", "hub"],
    "tapestry": ["mix", "blend"],
    "crucible": ["test", "trial"],
    "zenith": ["peak", "high point"],
    "pinnacle": ["top", "peak"],
    "endeavor": ["effort", "project"],
    "trajectory": ["path", "direction"],
    "plethora": ["lot", "many", "bunch"],
    "myriad": ["many", "tons of", "a range of"],
    "gamut": ["range", "spectrum"],
    # Transitional filler
    "furthermore": ["also", "on top of that"],
    "moreover": ["also", "plus"],
    "additionally": ["also", "on top of that"],
    "subsequently": ["then", "after that"],
    "consequently": ["so", "as a result"],
    "henceforth": ["from then on", "after that"],
    "thereby": ["which", "so"],
    "whereby": ["where", "through which"],
    "whilst": ["while"],
    "thereof": ["of it", "of that"],
    "therein": ["in it", "in that"],
}

BANNED_PHRASE_REPLACEMENTS: dict[str, list[str]] = {
    "responsible for": ["owned", "ran", "drove"],
    "in charge of": ["led", "directed", "ran"],
    "helped with": ["contributed to", "supported"],
    "worked on": ["shipped", "delivered", "built"],
    "involved in": ["contributed to", "part of"],
    "passionate about": [""],  # remove
    "results-driven": [""],
    "dynamic professional": [""],
    "dedicated team player": [""],
    "detail-oriented": [""],
    "seamless integration": ["integration"],
    "end-to-end solution": ["full solution"],
    "drive continuous improvement": ["keep improving"],
    "innovative solution": ["solution"],
    "best practices": ["standards", "patterns"],
    "fast-paced environment": [""],
    "strong communication skills": [""],
    "proven track record": [""],
    "self-starter": [""],
    "thought leader": [""],
    "cutting-edge": ["modern", "current"],
    "state-of-the-art": ["modern", "current"],
    "robust solution": ["solid solution"],
    "value-add": ["value"],
    "deep dive": ["close look", "deep look"],
    "scalable architecture": ["architecture"],
    "played a key role": ["helped", "was central to"],
    "ensuring seamless": ["keeping things smooth"],
    "end-to-end ownership": ["full ownership"],
    "drove significant improvements": ["made real improvements"],
    "cross-functional collaboration": ["working with other teams", "teaming up across groups"],
    "key stakeholder": ["stakeholder"],
    "actionable insights": ["useful findings"],
    "data-driven decision": ["decision backed by data"],
    "mission-critical": ["critical", "high-priority"],
    "high-impact": ["important", "meaningful"],
    "world-class": ["top-tier", "excellent"],
    "industry-leading": ["leading", "top"],
    "next-generation": ["new", "modern"],
    "game-changing": ["major", "big"],
    "holistic approach": ["full approach", "complete approach"],
    "paradigm shift": ["big change", "shift"],
    "core competency": ["strength", "skill"],
    "value proposition": ["value", "offer"],
    "strategic initiative": ["initiative", "project"],
    "operational excellence": ["strong ops", "smooth operations"],
    "thought leadership": [""],
    "resulting in a": ["which cut", "which brought", "—"],
    "leading to a": ["which led to", "giving us"],
    "contributing to a": ["helping with"],
    "which resulted in": ["which cut", "which got us"],
    "spearheaded the development": ["led development of", "built"],
    "played a pivotal role": ["was key in", "helped drive"],
    "instrumental in": ["key in", "helped with"],
    "fostering a culture": ["building a culture"],
    "driving innovation": ["pushing new ideas"],
    "ensuring compliance": ["staying compliant", "keeping us compliant"],
    "leveraging cutting-edge": ["using modern"],
    "leveraging advanced": ["using advanced"],
    "leveraging modern": ["using modern"],
    "utilizing industry-leading": ["using top"],
    "employing state-of-the-art": ["using modern"],
    "adept at": ["good at", "skilled in"],
    "well-versed in": ["experienced with", "comfortable with"],
    "seasoned professional": ["experienced engineer"],
    "track record of success": [""],
    "demonstrated ability": ["ability"],
    "proven ability": ["ability"],
    "extensive experience": ["experience"],
    "deep understanding": ["solid understanding", "good grasp of"],
    "keen eye for": ["focus on", "attention to"],
    "ensuring optimal": ["keeping things running well"],
    "ensuring high-quality": ["maintaining quality"],
    "ensuring timely delivery": ["delivering on time"],
    "while simultaneously": ["; also", "and also"],
    "while maintaining": ["; kept", "and kept"],
    "while ensuring": ["; made sure", "and ensured"],
    "served as a": ["was the", "acted as"],
    "acted as a": ["was the"],
    "functioned as a": ["was the"],
    "tasked with": ["asked to", "brought in to"],
    "charged with": ["asked to", "responsible for"],
    "entrusted with": ["given", "handed"],
    "effectively managed": ["managed"],
    "successfully delivered": ["delivered", "shipped"],
    "efficiently handled": ["handled"],
    "significantly improved": ["improved", "boosted"],
    "dramatically reduced": ["cut", "slashed"],
    "substantially increased": ["grew", "raised"],
    "greatly enhanced": ["improved"],
    "markedly improved": ["improved"],
    "notably increased": ["grew", "bumped up"],
    "wide range of": ["many", "various"],
    "broad spectrum of": ["many", "a mix of"],
    "diverse set of": ["various", "different"],
    "key contributor": ["contributor"],
    "key driver": ["driver"],
    "key enabler": ["enabler"],
    "from the ground up": ["from scratch"],
    "in a timely manner": ["on time", "quickly"],
    "on a daily basis": ["daily", "every day"],
    "on an ongoing basis": ["regularly", "continuously"],
    "stakeholder management": ["working with stakeholders"],
    "change management": ["managing change"],
    "risk mitigation": ["reducing risk"],
    "continuous improvement": ["ongoing improvements"],
    "process optimization": ["improving processes"],
    "workflow optimization": ["improving workflows"],
    "digital transformation": ["modernization"],
    "agile transformation": ["move to agile"],
    "subject matter expert": ["SME", "expert"],
    "domain expertise": ["expertise"],
    "in order to": ["to"],
    "not only": [""],  # will need context-aware handling
    "low-hanging fruit": ["easy wins", "quick wins"],
    "circle back": ["revisit", "come back to"],
    "touch base": ["check in", "sync"],
    "align on": ["agree on", "sync on"],
    "north star": ["goal", "target"],
    "move the needle": ["make a difference", "have an impact"],
    "hit the ground running": ["got up to speed fast"],
    "go-to person": ["point person", "the one people came to"],
    "wear many hats": ["did a bit of everything"],
}

# Contraction map
CONTRACTION_MAP: dict[str, str] = {
    "did not": "didn't",
    "do not": "don't",
    "does not": "doesn't",
    "could not": "couldn't",
    "would not": "wouldn't",
    "should not": "shouldn't",
    "will not": "won't",
    "can not": "can't",
    "cannot": "can't",
    "is not": "isn't",
    "are not": "aren't",
    "was not": "wasn't",
    "were not": "weren't",
    "has not": "hasn't",
    "have not": "haven't",
    "had not": "hadn't",
    "it is": "it's",
    "that is": "that's",
    "there is": "there's",
    "I am": "I'm",
    "I have": "I've",
    "I will": "I'll",
    "I would": "I'd",
    "we have": "we've",
    "we are": "we're",
    "they are": "they're",
    "they have": "they've",
    "you are": "you're",
    "who is": "who's",
    "what is": "what's",
}

# Informal parenthetical asides to inject
PARENTHETICAL_ASIDES: list[str] = [
    "(mostly Python)",
    "(the legacy one)",
    "(not fun)",
    "(finally)",
    "(long overdue)",
    "(about time)",
    "(surprisingly)",
    "(still proud of this)",
    "(messy but it worked)",
    "(our biggest bottleneck)",
    "(nobody else wanted to touch it)",
    "(before my time, it was manual)",
    "(took a few tries)",
    "(on a tight deadline)",
    "(weekend project that stuck)",
    "(across 3 time zones)",
]

# Context-first openers to prepend
CONTEXT_OPENERS: list[str] = [
    "During a production incident,",
    "After inheriting a messy codebase,",
    "Under a tight deadline,",
    "When the team was short-staffed,",
    "In response to a client escalation,",
    "After a major outage,",
    "Ahead of a product launch,",
    "While onboarding,",
    "In my first quarter,",
    "After noticing recurring failures,",
]


@dataclass
class HumanizeRequest:
    text: str
    ai_score: float = 0.0
    flagged_signals: list[str] = field(default_factory=list)
    flagged_phrases: list[str] = field(default_factory=list)
    flagged_words: list[str] = field(default_factory=list)
    jd_text: str = ""  # Optional: preserve JD-relevant keywords


@dataclass
class HumanizeResult:
    original_text: str
    humanized_text: str
    original_ai_score: float = 0.0
    new_ai_score: float = 0.0
    improvement: float = 0.0
    retries_used: int = 0
    success: bool = False
    error: str = ""


# ───────────────────────────────────────────────────────────────────────────
# Layer 1 — ML paraphrasing via HuggingFace Inference API
# ───────────────────────────────────────────────────────────────────────────

async def _hf_paraphrase(text: str, api_key: str) -> Optional[str]:
    """Call the HuggingFace Inference API to paraphrase text.

    Returns None if the API is unavailable or the key is missing.
    Works sentence-by-sentence to stay within model token limits.
    """
    if not api_key:
        return None

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{HF_API_URL}/{HF_PRIMARY_MODEL}"

    sentences = _split_into_sentences(text)
    paraphrased: list[str] = []

    try:
        async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 10:
                    paraphrased.append(sent)
                    continue

                payload = {
                    "inputs": f"paraphrase: {sent}",
                    "parameters": {
                        "max_length": max(60, int(len(sent.split()) * 2.5)),
                        "num_return_sequences": 1,
                        "do_sample": True,
                        "top_k": 50,
                        "top_p": 0.95,
                    },
                }
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        generated = data[0].get("generated_text", "").strip()
                        if generated and len(generated) > 5:
                            paraphrased.append(generated)
                            continue
                # Fallback: keep original sentence
                paraphrased.append(sent)

        result = " ".join(paraphrased)
        # Only use ML result if it preserved a reasonable amount of content
        if len(result.split()) >= len(text.split()) * 0.5:
            return result
        return None

    except Exception as e:
        logger.warning("HuggingFace paraphrase failed, falling back to rule-based", error=str(e))
        return None


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving bullet structure."""
    lines = text.split("\n")
    sentences: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            sentences.append("")
            continue
        # Keep bullet markers separate
        if re.match(r"^[•\-\*]\s*", line):
            sentences.append(line)
        else:
            # Split on sentence boundaries
            parts = re.split(r"(?<=[.!?])\s+", line)
            sentences.extend(parts)
    return sentences


# ───────────────────────────────────────────────────────────────────────────
# Layer 2 — Rule-based transformations
# ───────────────────────────────────────────────────────────────────────────

def _replace_banned_phrases(text: str) -> str:
    """Replace all banned phrases with natural alternatives."""
    for phrase, replacements in BANNED_PHRASE_REPLACEMENTS.items():
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        matches = list(pattern.finditer(text))
        for match in reversed(matches):
            replacement = random.choice(replacements)
            # Preserve capitalization of original
            if match.group()[0].isupper() and replacement:
                replacement = replacement[0].upper() + replacement[1:]
            text = text[:match.start()] + replacement + text[match.end():]
    return text


def _replace_banned_words(text: str) -> str:
    """Replace banned words with simple alternatives."""
    for word, replacements in BANNED_WORD_REPLACEMENTS.items():
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        matches = list(pattern.finditer(text))
        for match in reversed(matches):
            replacement = random.choice(replacements)
            original = match.group()
            # Preserve capitalization
            if original[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            text = text[:match.start()] + replacement + text[match.end():]

    # Catch any remaining banned extended words not in the replacement map
    for word in BANNED_EXTENDED_WORDS:
        if word.lower() in BANNED_WORD_REPLACEMENTS:
            continue
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        text = pattern.sub("", text)

    return text


def _fix_round_numbers(text: str) -> str:
    """Replace round percentages with specific-looking ones."""
    def _jitter(match: re.Match) -> str:
        num = int(match.group(1))
        if num in ROUND_NUMBERS:
            offset = random.choice([-3, -2, -1, 1, 2, 3])
            new_num = max(1, min(99, num + offset))
            return f"{new_num}%"
        return match.group(0)

    text = re.sub(r"\b(\d{1,2})%", _jitter, text)
    # Also handle "Xx" multiplier round numbers
    def _jitter_x(match: re.Match) -> str:
        num = int(match.group(1))
        if num in {2, 3, 4, 5, 10}:
            decimal = random.choice([".1", ".3", ".4", ".7", ".8"])
            return f"{num}{decimal}x"
        return match.group(0)

    text = re.sub(r"\b(\d{1,2})x\b", _jitter_x, text)
    return text


def _inject_contractions(text: str) -> str:
    """Convert some formal expansions to contractions."""
    for full, contracted in CONTRACTION_MAP.items():
        pattern = re.compile(rf"\b{re.escape(full)}\b", re.IGNORECASE)
        matches = list(pattern.finditer(text))
        for match in reversed(matches):
            # Apply ~70% of the time for naturalness
            if random.random() < 0.7:
                replacement = contracted
                if match.group()[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]
                text = text[:match.start()] + replacement + text[match.end():]
    return text


def _vary_sentence_lengths(lines: list[str]) -> list[str]:
    """Randomly split long sentences and merge short ones to create burstiness."""
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            result.append(line)
            i += 1
            continue

        words = line.split()

        # Split long lines (>30 words) into two shorter sentences sometimes
        if len(words) > 30 and random.random() < 0.5:
            # Find a natural split point (conjunction, comma, semicolon)
            split_candidates = []
            for j, w in enumerate(words):
                if j < 8 or j > len(words) - 8:
                    continue
                if w.lower() in {"and", "but", "which", "that", "so", "then"} or w.endswith(","):
                    split_candidates.append(j)
            if split_candidates:
                split_at = random.choice(split_candidates)
                first_half = " ".join(words[:split_at]).rstrip(",")
                second_half = " ".join(words[split_at:]).lstrip("and ").lstrip("but ")
                if not first_half.endswith((".", "!", "?")):
                    first_half += "."
                if second_half and second_half[0].islower():
                    second_half = second_half[0].upper() + second_half[1:]
                result.append(first_half)
                result.append(second_half)
                i += 1
                continue

        # Merge two short consecutive lines (<12 words each) sometimes
        if (
            len(words) < 12
            and i + 1 < len(lines)
            and lines[i + 1].strip()
            and len(lines[i + 1].split()) < 12
            and random.random() < 0.35
        ):
            merged = line.rstrip(".") + "; " + lines[i + 1].strip()
            if not merged.endswith((".", "!", "?")):
                merged += "."
            result.append(merged)
            i += 2
            continue

        result.append(line)
        i += 1

    return result


def _diversify_openers(lines: list[str]) -> list[str]:
    """Rewrite bullet points that start with the same word, using varied opener patterns."""
    if len(lines) < 3:
        return lines

    # Detect repeated first words
    first_words: dict[str, list[int]] = {}
    for i, line in enumerate(lines):
        stripped = re.sub(r"^[•\-\*]\s*", "", line.strip())
        if not stripped:
            continue
        fw = stripped.split()[0].lower() if stripped.split() else ""
        first_words.setdefault(fw, []).append(i)

    # For any first word used 3+ times, rewrite some of those lines
    transforms_applied = set()
    for fw, indices in first_words.items():
        if len(indices) < 3:
            continue
        # Keep the first occurrence, rewrite the rest
        for idx in indices[1:]:
            if random.random() < 0.6:
                lines[idx] = _rewrite_opener(lines[idx])
                transforms_applied.add(idx)

    # Also rewrite ~20% of bullets randomly for variety even if no repeats
    for i, line in enumerate(lines):
        if i not in transforms_applied and line.strip() and random.random() < 0.2:
            lines[i] = _rewrite_opener(lines[i])

    return lines


def _rewrite_opener(line: str) -> str:
    """Rewrite a single line's opener to use a different pattern."""
    # Extract bullet marker if present
    marker_match = re.match(r"^([•\-\*]\s*)", line)
    marker = marker_match.group(1) if marker_match else ""
    content = line[len(marker):].strip()

    if not content:
        return line

    words = content.split()
    if len(words) < 4:
        return line

    strategy = random.choice([
        "context_first",
        "object_first",
        "short_punchy",
        "number_first",
        "gerund",
    ])

    if strategy == "context_first":
        opener = random.choice(CONTEXT_OPENERS)
        # Lowercase the first word of the original content
        if content[0].isupper():
            content = content[0].lower() + content[1:]
        return f"{marker}{opener} {content}"

    elif strategy == "object_first":
        # Try to find the object (after the verb) and move it to front
        # Simple heuristic: take words after the first verb
        if len(words) >= 5:
            # Take from word 2 onward, put a dash, then first part
            obj_part = " ".join(words[2:5])
            rest = " ".join(words[:2] + words[5:])
            return f"{marker}{obj_part.capitalize()} — {rest.lower()}"
        return line

    elif strategy == "short_punchy":
        # Truncate to a punchy version and add a period
        if len(words) > 8:
            short = " ".join(words[:random.randint(4, 7)])
            if not short.endswith((".", "!", "?")):
                short += "."
            # Add a brief qualifier
            qualifier = " ".join(words[7:])
            if qualifier:
                qualifier = qualifier[0].upper() + qualifier[1:] if qualifier else ""
                if not qualifier.endswith((".", "!", "?")):
                    qualifier += "."
                return f"{marker}{short} {qualifier}"
            return f"{marker}{short}"
        return line

    elif strategy == "number_first":
        # Look for a number in the line and move it to front
        num_match = re.search(r"(\d+[\d,.]*[%x]?)\s+(\w+)", content)
        if num_match:
            num = num_match.group(0)
            rest = content[:num_match.start()] + content[num_match.end():]
            rest = rest.strip(" ,—-")
            if rest and rest[0].isupper():
                rest = rest[0].lower() + rest[1:]
            return f"{marker}{num}, {rest}"
        return line

    elif strategy == "gerund":
        # Convert "Verb X" to "Verbing X"
        first_word = words[0]
        # Simple gerund conversion
        gerund = _to_gerund(first_word)
        if gerund != first_word:
            rest = " ".join(words[1:])
            return f"{marker}{gerund} {rest}"
        return line

    return line


def _to_gerund(verb: str) -> str:
    """Convert a past tense or base verb to gerund form."""
    v = verb.lower().rstrip(".,;:")
    # Common irregular mappings
    gerund_map = {
        "built": "Building", "led": "Leading", "ran": "Running",
        "wrote": "Writing", "set": "Setting", "cut": "Cutting",
        "got": "Getting", "made": "Making", "took": "Taking",
        "drove": "Driving", "gave": "Giving", "found": "Finding",
        "kept": "Keeping", "brought": "Bringing", "thought": "Thinking",
        "told": "Telling", "sent": "Sending", "put": "Putting",
        "won": "Winning", "grew": "Growing", "drew": "Drawing",
        "broke": "Breaking", "spoke": "Speaking", "chose": "Choosing",
        "began": "Beginning", "knew": "Knowing", "came": "Coming",
        "saw": "Seeing", "held": "Holding", "stood": "Standing",
    }
    if v in gerund_map:
        return gerund_map[v]

    # Past tense -ed → -ing
    if v.endswith("ed"):
        base = v[:-2]
        if base.endswith("at") or base.endswith("it"):
            return (base + "ting").capitalize()
        if base.endswith("e"):
            return (base[:-1] + "ing").capitalize()
        return (base + "ing").capitalize()

    # Base form
    if v.endswith("e") and not v.endswith("ee"):
        return (v[:-1] + "ing").capitalize()

    return (v + "ing").capitalize()


def _inject_punctuation_variety(text: str) -> str:
    """Add semicolons, em-dashes, and parentheticals for natural feel."""
    lines = text.split("\n")
    result_lines: list[str] = []
    semicolons_added = 0
    dashes_added = 0
    parens_added = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or len(stripped.split()) < 6:
            result_lines.append(line)
            continue

        # Inject em-dash around a clause (~15% of lines)
        if dashes_added < 3 and random.random() < 0.15 and ", " in stripped:
            parts = stripped.split(", ", 1)
            if len(parts) == 2 and len(parts[1].split()) >= 3:
                # Replace one comma clause with em-dash clause
                stripped = f"{parts[0]} \u2014 {parts[1]}"
                dashes_added += 1

        # Inject parenthetical aside (~10% of lines)
        if parens_added < 2 and random.random() < 0.10 and "(" not in stripped:
            aside = random.choice(PARENTHETICAL_ASIDES)
            words = stripped.split()
            if len(words) > 6:
                insert_pos = random.randint(3, min(len(words) - 2, 8))
                words.insert(insert_pos, aside)
                stripped = " ".join(words)
                parens_added += 1

        # Inject semicolon by replacing a period or "and" (~12% of lines)
        if semicolons_added < 2 and random.random() < 0.12:
            stripped = re.sub(
                r"\.\s+([A-Z])",
                lambda m: f"; {m.group(1).lower()}",
                stripped,
                count=1,
            )
            semicolons_added += 1

        result_lines.append(stripped)

    return "\n".join(result_lines)


def _inject_passive_voice(text: str) -> str:
    """Convert ~15% of sentences to passive voice for natural variation."""
    lines = text.split("\n")
    result: list[str] = []
    passive_count = 0
    max_passive = max(1, len(lines) // 7)

    for line in lines:
        stripped = line.strip()
        if (
            passive_count < max_passive
            and stripped
            and len(stripped.split()) >= 6
            and random.random() < 0.15
        ):
            converted = _try_passive_conversion(stripped)
            if converted != stripped:
                result.append(converted)
                passive_count += 1
                continue
        result.append(line)

    return "\n".join(result)


def _try_passive_conversion(sentence: str) -> str:
    """Try to convert an active sentence to passive voice.

    Simple pattern: "Verb Object rest" -> "Object was verb-ed rest"
    Only works for simple patterns to avoid garbling.
    """
    # Extract bullet marker
    marker_match = re.match(r"^([•\-\*]\s*)", sentence)
    marker = marker_match.group(1) if marker_match else ""
    content = sentence[len(marker):].strip()

    words = content.split()
    if len(words) < 4:
        return sentence

    # Pattern: "Built the X" -> "The X was built"
    verb = words[0].lower().rstrip(".,;:")
    past_participle_map = {
        "built": "built", "created": "created", "designed": "designed",
        "developed": "developed", "deployed": "deployed", "wrote": "written",
        "set": "set", "reduced": "reduced", "improved": "improved",
        "configured": "configured", "migrated": "migrated",
        "shipped": "shipped", "launched": "launched", "fixed": "fixed",
        "rewrote": "rewritten", "refactored": "refactored",
        "automated": "automated", "integrated": "integrated",
    }

    pp = past_participle_map.get(verb)
    if not pp:
        return sentence

    # Find the object (article + noun or just noun)
    if words[1].lower() in {"the", "a", "an", "our", "my", "their"}:
        article = words[1]
        obj_words = []
        rest_start = 2
        for i in range(2, min(len(words), 6)):
            if words[i].lower() in {"that", "which", "to", "for", "by", "with", "and", "—", "from"}:
                break
            obj_words.append(words[i])
            rest_start = i + 1

        if not obj_words:
            return sentence

        obj = " ".join(obj_words)
        rest = " ".join(words[rest_start:])
        passive = f"{article.capitalize()} {obj} was {pp}"
        if rest:
            passive += f" {rest}"
        if not passive.endswith((".", "!", "?")):
            passive += "."
        return f"{marker}{passive}"

    return sentence


def _remove_ai_structure_patterns(text: str) -> str:
    """Remove or rewrite sentences that match known AI structure patterns."""
    for pattern_str in AI_STRUCTURE_PATTERNS:
        pattern = re.compile(pattern_str)
        matches = list(pattern.finditer(text))
        for match in reversed(matches):
            original = match.group()
            # "while also Xing" -> "; also Xed"
            if "while also" in original.lower():
                text = text[:match.start()] + text[match.end():]
            # "in order to X" -> "to X"
            elif "in order to" in original.lower():
                replacement = original.lower().replace("in order to", "to")
                text = text[:match.start()] + replacement + text[match.end():]
            # "resulting in a X%" -> "— cut X%"
            elif re.search(r"resulting\s+in", original, re.I):
                text = text[:match.start()] + text[match.end():]
    return text


def _add_informal_touches(text: str) -> str:
    """Sprinkle in occasional informal language for human feel."""
    informal_swaps = [
        (r"\bvery large\b", "huge"),
        (r"\bvery small\b", "tiny"),
        (r"\bvery difficult\b", "really tough"),
        (r"\bextremely\b", "really"),
        (r"\bsignificant\b", "big"),
        (r"\bsubstantial\b", "solid"),
        (r"\bnumerous\b", "a lot of"),
        (r"\bcommenced\b", "started"),
        (r"\bterminated\b", "ended"),
        (r"\bpurchased\b", "bought"),
        (r"\bprocured\b", "got"),
        (r"\bacquired\b", "picked up"),
        (r"\bascertained\b", "figured out"),
        (r"\bremuneration\b", "pay"),
        (r"\bdemonstrated\b", "showed"),
        (r"\bperformance\s+improvement\b", "speedup"),
    ]
    for pat, replacement in informal_swaps:
        if random.random() < 0.8:  # Apply most but not all
            text = re.sub(pat, replacement, text, flags=re.IGNORECASE, count=1)
    return text


def _clean_up(text: str) -> str:
    """Final cleanup pass to fix artifacts from transformations."""
    # Fix double spaces
    text = re.sub(r"  +", " ", text)
    # Fix space before punctuation
    text = re.sub(r" ([.,;:!?])", r"\1", text)
    # Fix double punctuation
    text = re.sub(r"\.\.+", ".", text)
    text = re.sub(r";;+", ";", text)
    text = re.sub(r",,+", ",", text)
    # Fix empty parentheses from removed content
    text = re.sub(r"\(\s*\)", "", text)
    # Fix orphan dashes
    text = re.sub(r"\s+\u2014\s+\u2014\s+", " \u2014 ", text)
    # Fix lines that start with lowercase after bullet
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        # Ensure bullet content starts with uppercase
        m = re.match(r"^([•\-\*]\s*)(.*)", stripped)
        if m and m.group(2) and m.group(2)[0].islower():
            stripped = m.group(1) + m.group(2)[0].upper() + m.group(2)[1:]
        cleaned.append(stripped)
    text = "\n".join(cleaned)
    # Remove leading/trailing blank lines
    text = text.strip()
    return text


def apply_rule_based_transforms(text: str, aggressive: bool = False) -> str:
    """Apply all rule-based transformations.

    When aggressive=True, applies more transforms (used on retries).
    """
    # Step 1: Replace banned phrases and words
    text = _replace_banned_phrases(text)
    text = _replace_banned_words(text)

    # Step 2: Fix round numbers
    text = _fix_round_numbers(text)

    # Step 3: Remove AI structure patterns
    text = _remove_ai_structure_patterns(text)

    # Step 4: Inject contractions
    text = _inject_contractions(text)

    # Step 5: Sentence length variation
    lines = [l for l in text.split("\n")]
    lines = _vary_sentence_lengths(lines)
    text = "\n".join(lines)

    # Step 6: Diversify openers
    lines = text.split("\n")
    lines = _diversify_openers(lines)
    text = "\n".join(lines)

    # Step 7: Punctuation variety
    text = _inject_punctuation_variety(text)

    # Step 8: Passive voice injection
    text = _inject_passive_voice(text)

    # Step 9: Informal touches
    text = _add_informal_touches(text)

    # If aggressive mode, run another pass of some transforms
    if aggressive:
        text = _replace_banned_phrases(text)
        text = _replace_banned_words(text)
        text = _fix_round_numbers(text)
        lines = text.split("\n")
        lines = _diversify_openers(lines)
        text = "\n".join(lines)
        text = _inject_punctuation_variety(text)
        text = _inject_contractions(text)

    # Final cleanup
    text = _clean_up(text)

    return text


# ───────────────────────────────────────────────────────────────────────────
# Layer 3 — Self-verification (quick AI score check)
# ───────────────────────────────────────────────────────────────────────────

def _quick_score(text: str) -> float:
    """Fast heuristic scoring without full engine — checks the most impactful signals."""
    from collections import Counter

    score = 0.0
    text_lower = text.lower()
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 10]

    # Check banned phrases (weight: 15)
    phrase_count = sum(1 for p in BANNED_PHRASES if p in text_lower)
    if phrase_count >= 5:
        score += 15
    elif phrase_count >= 3:
        score += 10
    elif phrase_count >= 1:
        score += 5

    # Check banned words (weight: 12)
    word_count = sum(
        1 for w in BANNED_EXTENDED_WORDS
        if re.search(rf"\b{re.escape(w)}\b", text_lower)
    )
    if word_count >= 4:
        score += 12
    elif word_count >= 2:
        score += 7
    elif word_count >= 1:
        score += 3

    # Check sentence length variance (weight: 12)
    if len(lines) >= 3:
        lengths = [len(l.split()) for l in lines]
        std = statistics.stdev(lengths)
        if std < 3:
            score += 12
        elif std < 5:
            score += 6

    # Check opening word repetition (weight: 10)
    first_words = [
        l.split()[0].lower().strip("•-*") for l in lines if l.split()
    ]
    fw_counts = Counter(first_words)
    max_repeat = max(fw_counts.values()) if fw_counts else 0
    if max_repeat >= 4:
        score += 10
    elif max_repeat >= 3:
        score += 6

    # Check round numbers (weight: 8)
    round_nums = len(
        re.findall(
            r"\b(?:20|25|30|35|40|45|50|55|60|65|70|75|80|85|90|95)\s*%", text
        )
    )
    if round_nums >= 3:
        score += 8
    elif round_nums >= 2:
        score += 5

    # Check AI sentence patterns (weight: 8)
    ai_patterns = [
        r"(?i)resulting\s+in\s+a?\s*\d+",
        r"(?i)leading\s+to\s+a?\s*\d+",
        r"(?i)by\s+leveraging",
        r"(?i)not\s+only.+but\s+also",
        r"(?i)while\s+also\s+\w+",
    ]
    pattern_count = sum(1 for p in ai_patterns if re.search(p, text))
    if pattern_count >= 3:
        score += 8
    elif pattern_count >= 1:
        score += 4

    # Punctuation variety bonus (reduces score)
    has_semicolon = ";" in text
    has_parens = bool(re.search(r"\([^)]+\)", text))
    has_dash = bool(re.search(r"\s[\u2014\u2013]\s", text))
    has_contraction = bool(re.search(r"\w+n't\b", text))
    punct_variety = sum([has_semicolon, has_parens, has_dash, has_contraction])
    score -= punct_variety * 3

    return max(0.0, min(100.0, score))


# ───────────────────────────────────────────────────────────────────────────
# Main engine class
# ───────────────────────────────────────────────────────────────────────────

class HumanizerEngine:
    MAX_RETRIES = 2

    def __init__(self) -> None:
        self._hf_api_key = os.environ.get("HUGGINGFACE_API_KEY", "")

    async def humanize(self, request: HumanizeRequest) -> HumanizeResult:
        result = HumanizeResult(
            original_text=request.text,
            humanized_text="",
            original_ai_score=request.ai_score,
        )

        try:
            text = request.text

            # ── Layer 1: ML paraphrasing (if API key available) ──
            ml_text = await _hf_paraphrase(text, self._hf_api_key)
            if ml_text:
                logger.info("HuggingFace paraphrasing succeeded")
                text = ml_text
            else:
                logger.info(
                    "Skipping HuggingFace paraphrasing (no key or API unavailable), "
                    "using rule-based transforms only"
                )

            # ── Layer 2: Rule-based transforms ──
            text = apply_rule_based_transforms(text, aggressive=False)

            # ── Layer 3: Self-verification loop ──
            new_score = _quick_score(text)
            retries = 0

            while new_score > 25 and retries < self.MAX_RETRIES:
                retries += 1
                logger.info(
                    "Humanization retry — score still high",
                    attempt=retries,
                    score=new_score,
                )
                # Re-apply transforms more aggressively
                text = apply_rule_based_transforms(text, aggressive=True)
                new_score = _quick_score(text)

            result.humanized_text = text
            result.new_ai_score = round(new_score, 1)
            result.improvement = round(request.ai_score - new_score, 1)
            result.retries_used = retries
            result.success = new_score < 30

            return result

        except Exception as e:
            logger.error("Humanization failed", error=str(e))
            result.error = str(e)
            return result
