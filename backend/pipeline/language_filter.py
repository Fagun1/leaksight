class LanguageFilter:
    """Filters posts to English-only content."""

    ACCEPTED_LANGUAGES = {"en"}
    MIN_TEXT_LENGTH = 20

    def is_accepted(self, text: str) -> bool:
        if not text or len(text.strip()) < self.MIN_TEXT_LENGTH:
            return False
        try:
            from langdetect import detect, LangDetectException
            lang = detect(text)
            return lang in self.ACCEPTED_LANGUAGES
        except Exception:
            return True
