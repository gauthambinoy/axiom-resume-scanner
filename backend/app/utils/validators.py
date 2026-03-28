from app.utils.exceptions import (
    ResumeEmptyError,
    JDEmptyError,
    InputTooShortError,
    InputTooLongError,
)
from app.config import get_settings


def validate_resume_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise ResumeEmptyError()
    settings = get_settings()
    if len(text) < settings.min_resume_length:
        raise InputTooShortError(
            f"Resume must be at least {settings.min_resume_length} characters (got {len(text)})",
            details={"min_length": settings.min_resume_length, "actual_length": len(text)},
        )
    if len(text) > settings.max_resume_length:
        raise InputTooLongError(
            f"Resume must be under {settings.max_resume_length} characters (got {len(text)})",
            details={"max_length": settings.max_resume_length, "actual_length": len(text)},
        )
    return text


def validate_jd_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise JDEmptyError()
    settings = get_settings()
    if len(text) < settings.min_jd_length:
        raise InputTooShortError(
            f"Job description must be at least {settings.min_jd_length} characters (got {len(text)})",
            details={"min_length": settings.min_jd_length, "actual_length": len(text)},
        )
    if len(text) > settings.max_jd_length:
        raise InputTooLongError(
            f"Job description must be under {settings.max_jd_length} characters (got {len(text)})",
            details={"max_length": settings.max_jd_length, "actual_length": len(text)},
        )
    return text
