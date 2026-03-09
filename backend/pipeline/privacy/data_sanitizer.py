"""
Personal data sanitization before storage (PROJECT_SPEC_CONTINUATION §10.3).
"""
import re
from typing import Dict, Any


class DataSanitizer:
    """Removes or masks personal data from text and post documents."""

    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    PHONE_PATTERN = re.compile(
        r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    )
    EXCLUDED_FIELDS = [
        "email", "phone", "address", "real_name",
        "ip_address", "device_id", "location",
    ]

    def sanitize_text(self, text: str) -> str:
        if not text:
            return ""
        text = self.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
        text = self.PHONE_PATTERN.sub("[PHONE_REDACTED]", text)
        return text

    def sanitize_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for key, value in post.items():
            if key in self.EXCLUDED_FIELDS:
                continue
            if isinstance(value, str):
                out[key] = self.sanitize_text(value)
            else:
                out[key] = value
        return out
