import math
from datetime import datetime, timezone
from backend.pipeline.cleaner import TextCleaner


class PostEnricher:
    """Adds computed metadata fields to a post before storage."""

    def __init__(self):
        self.cleaner = TextCleaner()

    def enrich(self, post_dict: dict) -> dict:
        content = post_dict.get("content", "")
        title = post_dict.get("title", "")
        full_text = f"{title} {content}".strip()
        post_dict["cleaned_content"] = self.cleaner.clean(content)
        post_dict["cleaned_title"] = self.cleaner.clean(title) if title else None
        post_dict["full_text"] = self.cleaner.clean(full_text)
        post_dict["word_count"] = len(post_dict["full_text"].split())
        post_dict["char_count"] = len(post_dict["full_text"])
        post_dict["urls_extracted"] = self.cleaner.extract_urls(content)
        post_dict["mentions_extracted"] = self.cleaner.extract_mentions(content)
        post_dict["hashtags_extracted"] = self.cleaner.extract_hashtags(content)
        post_dict["processed_at"] = datetime.now(timezone.utc)
        post_dict["pipeline_version"] = "1.0.0"
        engagement = post_dict.get("engagement", {})
        post_dict["engagement_score"] = self._compute_engagement_score(engagement)
        post_dict["is_leak"] = False
        post_dict["leak_confidence"] = 0.0
        post_dict["leak_category"] = "NONE"
        post_dict["rumor_id"] = None
        post_dict["entities"] = {"companies": [], "products": [], "features": []}
        return post_dict

    def _compute_engagement_score(self, engagement: dict) -> float:
        likes = engagement.get("likes", engagement.get("upvotes", 0))
        retweets = engagement.get("retweets", 0)
        comments = engagement.get("comments", engagement.get("replies", 0))
        raw_score = (likes * 1.0) + (retweets * 2.0) + (comments * 1.5)
        if raw_score <= 0:
            return 0.0
        return min(1.0, math.log10(raw_score + 1) / 5.0)
