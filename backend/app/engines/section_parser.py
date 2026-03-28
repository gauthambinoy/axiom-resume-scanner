import re
from dataclasses import dataclass, field

from app.engines.constants import RESUME_SECTIONS, REQUIRED_SECTIONS, RECOMMENDED_SECTIONS, JD_DETECTION_PHRASES
from app.utils.exceptions import ResumeEmptyError
from app.utils.text_processing import count_words
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ContactInfo:
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


@dataclass
class BulletPoint:
    text: str
    word_count: int
    section: str
    position: int
    first_word: str
    has_metric: bool
    ends_with_metric: bool


@dataclass
class ExperienceEntry:
    company: str = ""
    title: str = ""
    dates: str = ""
    bullets: list[BulletPoint] = field(default_factory=list)


@dataclass
class SectionParseResult:
    sections_found: list[str] = field(default_factory=list)
    sections_missing: list[str] = field(default_factory=list)
    section_content: dict[str, str] = field(default_factory=dict)
    bullets: list[BulletPoint] = field(default_factory=list)
    summary_text: str = ""
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    total_bullet_count: int = 0
    experience_entries: list[ExperienceEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    flat_text_mode: bool = False


_HEADER_PATTERNS = [
    re.compile(r"^([A-Z][A-Z\s&/]{2,})$", re.MULTILINE),                     # ALL CAPS HEADER
    re.compile(r"^([A-Za-z\s&/]+):\s*$", re.MULTILINE),                       # Header:
    re.compile(r"^(?:#{1,3})\s+(.+)$", re.MULTILINE),                          # ### Markdown header
    re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$", re.MULTILINE),       # Title Case Header
    # New patterns for edge cases
    re.compile(r"^[-=]{3,}\s*\n\s*(.+)$", re.MULTILINE),                       # --- below header
    re.compile(r"^(.+)\s*\n\s*[-=]{3,}$", re.MULTILINE),                       # header above ---
    re.compile(r"^\*\*([A-Za-z\s&/]+)\*\*\s*$", re.MULTILINE),                # **Bold Header**
    re.compile(r"^([A-Z][A-Z\s&/]+)(?:\s*[-|:]\s*)$", re.MULTILINE),          # HEADER - or HEADER |
    re.compile(r"^(?:•|\d+\.)\s*([A-Z][A-Z\s&/]{2,})\s*$", re.MULTILINE),    # • HEADER or 1. HEADER
]

_BULLET_PATTERN = re.compile(r"^\s*(?:[•\-\*▪◦►✦✧⦿⬤➤➜→▸▹⁃‣]|\d+[.)]\s|[a-z][.)]\s)")
_METRIC_END_PATTERN = re.compile(r"(?:\d+[\d,.]*\s*%|\d+[xX]|\$[\d,.]+[MKB]?)\s*\.?\s*$")
_METRIC_PATTERN = re.compile(r"\d+[\d,.]*\s*%|\d+[xX]|\$[\d,.]+")


class SectionParser:
    def parse(self, resume_text: str) -> SectionParseResult:
        if not resume_text or not resume_text.strip():
            raise ResumeEmptyError()

        resume_text = resume_text.replace("\r\n", "\n").replace("\r", "\n")
        result = SectionParseResult()

        # Check if text looks like a JD
        text_lower = resume_text.lower()
        jd_matches = sum(1 for p in JD_DETECTION_PHRASES if p in text_lower)
        if jd_matches >= 3:
            result.warnings.append(
                "This text appears to be a job description, not a resume. "
                "Make sure you haven't swapped the inputs."
            )

        # Detect contact info
        result.contact_info = self._extract_contact_info(resume_text)

        # Detect sections
        sections = self._detect_sections(resume_text)

        if not sections:
            result.flat_text_mode = True
            result.warnings.append("Could not detect section headers")
            result.section_content["full_text"] = resume_text
            bullets = self._extract_bullets(resume_text, "unknown")
            result.bullets = bullets
            result.total_bullet_count = len(bullets)
        else:
            found_names: list[str] = []
            for section_name, content in sections.items():
                result.section_content[section_name] = content
                found_names.append(section_name)

            result.sections_found = found_names

            # Map found sections to known section types
            normalized_found = self._normalize_section_names(found_names)

            all_expected = set(REQUIRED_SECTIONS + RECOMMENDED_SECTIONS)
            result.sections_missing = [s for s in all_expected if s not in normalized_found]

            # Extract summary
            for key in ["summary", "objective", "profile", "about"]:
                if key in normalized_found:
                    for name, content in sections.items():
                        if self._normalize_name(name) == key:
                            result.summary_text = content.strip()
                            break
                    if result.summary_text:
                        break

            # Extract bullets from experience sections
            all_bullets: list[BulletPoint] = []
            for name, content in sections.items():
                norm = self._normalize_name(name)
                if norm in {"experience", "work experience", "employment", "projects"}:
                    bullets = self._extract_bullets(content, name)
                    all_bullets.extend(bullets)

            # If no experience bullets found, try all sections
            if not all_bullets:
                for name, content in sections.items():
                    bullets = self._extract_bullets(content, name)
                    all_bullets.extend(bullets)

            result.bullets = all_bullets
            result.total_bullet_count = len(all_bullets)

            # Extract experience entries
            for name, content in sections.items():
                norm = self._normalize_name(name)
                if norm in {"experience", "work experience", "employment"}:
                    entries = self._parse_experience_entries(content)
                    result.experience_entries.extend(entries)

        return result

    def _detect_sections(self, text: str) -> dict[str, str]:
        lines = text.split("\n")
        section_starts: list[tuple[int, str]] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or len(stripped) > 60:
                continue

            for pattern in _HEADER_PATTERNS:
                match = pattern.match(stripped)
                if match:
                    header = match.group(1).strip()
                    if self._is_known_section(header):
                        section_starts.append((i, header))
                        break

        if not section_starts:
            # Fallback: try to infer sections from content patterns
            section_starts = self._infer_sections_from_content(lines)
            if not section_starts:
                return {}

        sections: dict[str, str] = {}
        for idx, (line_num, header) in enumerate(section_starts):
            start = line_num + 1
            end = section_starts[idx + 1][0] if idx + 1 < len(section_starts) else len(lines)
            content = "\n".join(lines[start:end]).strip()
            sections[header] = content

        return sections

    def _infer_sections_from_content(self, lines: list[str]) -> list[tuple[int, str]]:
        """Fallback: detect sections by content patterns when no headers are found."""
        inferred: list[tuple[int, str]] = []
        date_pattern = re.compile(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}"
            r"|(?:\d{1,2}/\d{4})"
            r"|(?:\d{4}\s*[-–]\s*(?:\d{4}|present|current))",
            re.IGNORECASE,
        )
        email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
        skill_keywords = {"python", "java", "javascript", "react", "aws", "docker", "sql", "git"}

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # Detect contact area (email/phone in first 5 lines)
            if i < 5 and email_pattern.search(stripped):
                inferred.append((0, "Contact"))
                continue

            # Detect education (university, bachelor, master, degree)
            if re.search(r"(?i)\b(university|bachelor|master|degree|b\.?s\.?|m\.?s\.?|ph\.?d)\b", stripped):
                if not any(name == "Education" for _, name in inferred):
                    inferred.append((i, "Education"))
                continue

            # Detect experience (dates + company-like context)
            if date_pattern.search(stripped) and _BULLET_PATTERN.match(lines[min(i+1, len(lines)-1)].strip() if i+1 < len(lines) else ""):
                if not any(name == "Experience" for _, name in inferred):
                    inferred.append((i, "Experience"))
                continue

            # Detect skills (many tech keywords on one line)
            words_lower = set(stripped.lower().replace(",", " ").replace("|", " ").split())
            if len(words_lower & skill_keywords) >= 3:
                if not any(name == "Skills" for _, name in inferred):
                    inferred.append((i, "Skills"))

        return inferred

    def _is_known_section(self, header: str) -> bool:
        normalized = header.lower().strip()
        for section in RESUME_SECTIONS:
            if section in normalized or normalized in section:
                return True
        # Extended variations for better edge-case detection
        extras = {
            "professional experience", "core skills", "key skills", "work history",
            "professional summary", "career objective", "additional skills",
            "relevant experience", "leadership", "activities", "honors",
            # Additional variations
            "career history", "employment history", "professional background",
            "areas of expertise", "core competencies", "technical expertise",
            "selected projects", "key projects", "notable projects",
            "professional development", "training", "licenses",
            "community involvement", "extracurricular", "affiliations",
            "memberships", "professional affiliations", "industry knowledge",
            "academic background", "academic history", "research",
            "technologies", "tech stack", "tools & technologies",
            "tools and technologies", "programming", "frameworks",
            "about me", "personal statement", "career summary",
            "executive summary", "qualifications summary", "highlight",
            "highlights", "key achievements", "accomplishments",
        }
        return normalized in extras

    def _normalize_name(self, name: str) -> str:
        name = name.lower().strip()
        mapping = {
            "professional experience": "experience",
            "work history": "experience",
            "relevant experience": "experience",
            "professional summary": "summary",
            "career objective": "objective",
            "core skills": "skills",
            "key skills": "skills",
            "additional skills": "skills",
            "technical skills": "skills",
        }
        return mapping.get(name, name)

    def _normalize_section_names(self, names: list[str]) -> set[str]:
        result: set[str] = set()
        for name in names:
            norm = self._normalize_name(name)
            result.add(norm)
            # Also add "contact" if contact info was found at top
        return result

    def _extract_bullets(self, text: str, section: str) -> list[BulletPoint]:
        bullets: list[BulletPoint] = []
        lines = text.split("\n")
        current_bullet = ""
        position = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_bullet:
                    bp = self._make_bullet(current_bullet, section, position)
                    if bp.word_count >= 3:
                        bullets.append(bp)
                        position += 1
                    current_bullet = ""
                continue

            if _BULLET_PATTERN.match(stripped):
                if current_bullet:
                    bp = self._make_bullet(current_bullet, section, position)
                    if bp.word_count >= 3:
                        bullets.append(bp)
                        position += 1
                cleaned = re.sub(r"^\s*(?:[•\-\*▪◦►✦✧⦿⬤➤➜→▸▹⁃‣]|\d+[.)]\s|[a-z][.)]\s)\s*", "", stripped)
                current_bullet = cleaned
            else:
                if current_bullet:
                    current_bullet += " " + stripped
                else:
                    # Could be a bullet without a marker (e.g., first line of experience)
                    if count_words(stripped) >= 5:
                        current_bullet = stripped

        if current_bullet:
            bp = self._make_bullet(current_bullet, section, position)
            if bp.word_count >= 3:
                bullets.append(bp)

        return bullets

    def _make_bullet(self, text: str, section: str, position: int) -> BulletPoint:
        text = text.strip()
        words = text.split()
        first_word = words[0].lower().rstrip(".,;:") if words else ""
        wc = len(words)
        has_metric = bool(_METRIC_PATTERN.search(text))
        ends_with_metric = bool(_METRIC_END_PATTERN.search(text))

        return BulletPoint(
            text=text,
            word_count=wc,
            section=section,
            position=position,
            first_word=first_word,
            has_metric=has_metric,
            ends_with_metric=ends_with_metric,
        )

    def _extract_contact_info(self, text: str) -> ContactInfo:
        info = ContactInfo()
        try:
            # Email
            email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
            if email_match:
                info.email = email_match.group(0)

            # Phone
            phone_match = re.search(
                r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
            )
            if phone_match:
                info.phone = phone_match.group(0)

            # LinkedIn
            linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
            if linkedin_match:
                info.linkedin = linkedin_match.group(0)

            # GitHub
            github_match = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)
            if github_match:
                info.github = github_match.group(0)

            # Name (heuristic: first non-empty line that isn't an email/phone/url)
            for line in text.split("\n")[:5]:
                line = line.strip()
                if not line or "@" in line or "http" in line.lower() or re.match(r"^[\d(+]", line):
                    continue
                if 2 <= len(line.split()) <= 4 and line[0].isupper():
                    info.name = line
                    break
        except Exception:
            pass
        return info

    def _parse_experience_entries(self, content: str) -> list[ExperienceEntry]:
        entries: list[ExperienceEntry] = []
        try:
            # Simple heuristic: look for lines with dates
            date_pattern = re.compile(
                r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}"
                r"|(?:\d{1,2}/\d{4})"
                r"|(?:\d{4}\s*[-–]\s*(?:\d{4}|present|current))",
                re.IGNORECASE,
            )
            lines = content.split("\n")
            current_entry: ExperienceEntry | None = None

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                date_match = date_pattern.search(stripped)
                if date_match and not _BULLET_PATTERN.match(stripped):
                    if current_entry:
                        entries.append(current_entry)
                    current_entry = ExperienceEntry(dates=date_match.group(0))
                    # Try to extract company/title from same or preceding line
                    title_part = stripped[:date_match.start()].strip().rstrip("|–-,")
                    if title_part:
                        parts = re.split(r"\s*[|–\-,]\s*", title_part, maxsplit=1)
                        current_entry.title = parts[0].strip()
                        if len(parts) > 1:
                            current_entry.company = parts[1].strip()
                elif current_entry and _BULLET_PATTERN.match(stripped):
                    cleaned = re.sub(r"^\s*(?:[•\-\*▪◦►✦✧⦿⬤➤➜→▸▹⁃‣]|\d+[.)]\s|[a-z][.)]\s)\s*", "", stripped)
                    bp = self._make_bullet(cleaned, "experience", len(current_entry.bullets))
                    current_entry.bullets.append(bp)

            if current_entry:
                entries.append(current_entry)
        except Exception:
            pass
        return entries
