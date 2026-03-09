"""
Enhanced data cleaning with spam detection (PROJECT_SPEC_CONTINUATION §3.4).
"""
import re
import unicodedata
from typing import Optional

try:
    from langdetect import detect, LangDetectException
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

SPAM_PATTERNS = [
    r"buy now",
    r"click here",
    r"subscribe to",
    r"use code .+ for \d+%",
    r"giveaway",
    r"win a free",
    r"check out my channel",
    r"follow me on",
    r"promo code",
    r"sponsored",
]


class DataCleaner:
    """Cleans extracted text for NLP; rejects spam and non-English."""

    MIN_TEXT_LENGTH = 20
    MAX_TEXT_LENGTH = 10000

    def clean(self, text: str) -> dict:
        """
        Full cleaning pipeline.
        Returns dict with cleaned_text, is_valid, rejection_reason, language.
        """
        result = {
            "original_length": len(text or ""),
            "is_valid": True,
            "rejection_reason": None,
            "language": None,
            "cleaned_text": "",
        }
        if not text:
            result["is_valid"] = False
            result["rejection_reason"] = "empty"
            return result

        text = self._remove_html(text)
        text = self._normalize_unicode(text)
        text = self._normalize_whitespace(text)

        if HAS_LANGDETECT:
            try:
                lang = detect(text)
                result["language"] = lang
                if lang != "en":
                    result["is_valid"] = False
                    result["rejection_reason"] = f"non_english:{lang}"
                    return result
            except (LangDetectException, Exception):
                result["language"] = "unknown"

        if len(text) < self.MIN_TEXT_LENGTH:
            result["is_valid"] = False
            result["rejection_reason"] = "too_short"
            return result

        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[: self.MAX_TEXT_LENGTH]

        if self._is_spam(text):
            result["is_valid"] = False
            result["rejection_reason"] = "spam_detected"
            return result

        result["cleaned_text"] = text
        result["cleaned_length"] = len(text)
        return result

    def _remove_html(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&[a-zA-Z]+;", " ", text)
        text = re.sub(r"&#\d+;", " ", text)
        return text

    def _normalize_unicode(self, text: str) -> str:
        text = unicodedata.normalize("NFKD", text)
        try:
            text = text.encode("ascii", "ignore").decode("ascii")
        except Exception:
            pass
        return text

    def _normalize_whitespace(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _is_spam(self, text: str) -> bool:
        text_lower = text.lower()
        spam_score = sum(
            1 for pattern in SPAM_PATTERNS if re.search(pattern, text_lower)
        )
        return spam_score >= 2
