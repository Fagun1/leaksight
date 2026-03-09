import re
import html
import unicodedata


class TextCleaner:
    """Normalizes and cleans raw post text."""

    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    MENTION_PATTERN = re.compile(r"@\w+")
    EMOJI_PATTERN = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE,
    )
    MULTI_SPACE = re.compile(r"\s+")
    HASHTAG_PATTERN = re.compile(r"#(\w+)")

    def clean(self, text: str, preserve_mentions: bool = False) -> str:
        if not text:
            return ""
        text = html.unescape(text)
        text = unicodedata.normalize("NFKC", text)
        text = self.URL_PATTERN.sub("", text)
        if not preserve_mentions:
            text = self.MENTION_PATTERN.sub("", text)
        text = self.HASHTAG_PATTERN.sub(r"\1", text)
        text = self.EMOJI_PATTERN.sub(" ", text)
        text = self.MULTI_SPACE.sub(" ", text).strip()
        return text

    def extract_urls(self, text: str) -> list:
        return self.URL_PATTERN.findall(text or "")

    def extract_mentions(self, text: str) -> list:
        return [m.lstrip("@") for m in self.MENTION_PATTERN.findall(text or "")]

    def extract_hashtags(self, text: str) -> list:
        return self.HASHTAG_PATTERN.findall(text or "")
