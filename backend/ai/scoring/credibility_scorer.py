"""
Rumor credibility scoring with breakdown and grade (PROJECT_SPEC_CONTINUATION §5.4).
"""
import math
import re
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class CredibilityScore:
    overall: float
    breakdown: Dict[str, float]
    grade: str


class RumorCredibilityScorer:
    """Computes credibility score for a rumor cluster with dimension breakdown."""

    WEIGHTS = {
        "source_accuracy": 0.30,
        "independent_sources": 0.20,
        "source_reputation": 0.15,
        "temporal_consistency": 0.10,
        "specificity": 0.10,
        "engagement": 0.10,
        "cross_platform": 0.05,
    }

    def score(
        self,
        rumor: dict,
        posts: List[dict],
        source_stats: Optional[Dict[str, dict]] = None,
    ) -> CredibilityScore:
        source_stats = source_stats or {}
        breakdown = {}

        author_key = "author_username"
        domain_key = "source_platform"

        accuracy_scores = []
        for post in posts:
            author = post.get(author_key) or post.get("author", "unknown")
            stats = source_stats.get(author, {})
            acc = stats.get("accuracy_rate", stats.get("accuracy", 0))
            if isinstance(acc, (int, float)):
                accuracy_scores.append(acc if acc <= 1 else acc / 100.0)
            else:
                accuracy_scores.append(0.0)
        breakdown["source_accuracy"] = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        )

        unique_domains = set(p.get(domain_key, p.get("source_domain", "")) for p in posts)
        unique_authors = set(p.get(author_key, p.get("author", "")) for p in posts)
        n_sources = len(unique_authors)
        breakdown["independent_sources"] = min(
            0.3 + 0.2 * math.log(max(n_sources, 1)), 1.0
        )

        reputation_scores = []
        tier_scores = {
            "elite": 1.0,
            "verified": 0.8,
            "established": 0.6,
            "new": 0.3,
            "unknown": 0.2,
        }
        for post in posts:
            author = post.get(author_key) or post.get("author", "unknown")
            stats = source_stats.get(author, {})
            tier = stats.get("tier", "unknown")
            reputation_scores.append(tier_scores.get(tier, 0.2))
        breakdown["source_reputation"] = (
            max(reputation_scores) if reputation_scores else 0.0
        )

        breakdown["temporal_consistency"] = self._score_temporal(rumor)
        breakdown["specificity"] = self._score_specificity(rumor, posts)
        breakdown["engagement"] = self._score_engagement(posts)
        breakdown["cross_platform"] = min(len(unique_domains) / 4.0, 1.0)

        overall = sum(
            breakdown.get(dim, 0) * weight for dim, weight in self.WEIGHTS.items()
        )
        grade = self._assign_grade(overall)

        return CredibilityScore(
            overall=round(overall, 2),
            breakdown={k: round(v, 3) for k, v in breakdown.items()},
            grade=grade,
        )

    def _score_temporal(self, rumor: dict) -> float:
        timeline = rumor.get("timeline", [])
        if len(timeline) <= 1:
            return 0.2
        dates = set()
        for event in timeline:
            d = event.get("date", event.get("timestamp", ""))
            if d:
                dates.add(str(d)[:10])
        return min(len(dates) / 7.0, 1.0)

    def _score_specificity(self, rumor: dict, posts: List[dict]) -> float:
        score = 0.0
        entities = rumor.get("entities", {})
        if entities.get("products"):
            score += 0.3
        if entities.get("features"):
            score += 0.3
        spec_pattern = re.compile(
            r"\d+\s*(?:nm|GB|TB|MP|mAh|GHz|cores?|threads?|TOPS|W)"
        )
        for post in posts:
            text = post.get("full_text", post.get("content", ""))
            if spec_pattern.search(text):
                score += 0.2
                break
        date_pattern = re.compile(
            r"(?:Q[1-4]\s*\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|"
            r"Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})"
        )
        for post in posts:
            text = post.get("full_text", post.get("content", ""))
            if date_pattern.search(text):
                score += 0.2
                break
        return min(score, 1.0)

    def _score_engagement(self, posts: List[dict]) -> float:
        total_score = 0
        total_comments = 0
        for post in posts:
            eng = post.get("engagement", {})
            total_score += eng.get("score", eng.get("upvotes", eng.get("likes", 0)))
            total_comments += eng.get("comments", eng.get("replies", 0))
        engagement_score = 0.0
        if total_score > 0:
            engagement_score += min(math.log10(total_score) / 4.0, 0.5)
        if total_comments > 0:
            engagement_score += min(math.log10(total_comments) / 3.0, 0.5)
        return min(engagement_score, 1.0)

    def _assign_grade(self, score: float) -> str:
        if score >= 0.85:
            return "A"
        if score >= 0.70:
            return "B"
        if score >= 0.55:
            return "C"
        if score >= 0.40:
            return "D"
        return "F"
