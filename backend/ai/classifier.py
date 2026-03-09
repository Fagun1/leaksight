"""
Rule-based leak classifier optimized for tech news headlines and article text.
No ML model needed — keyword + entity matching is fast and accurate for this domain.
"""
from typing import Dict, List
from pydantic import BaseModel
import re
import logging

logger = logging.getLogger("ai.classifier")


class ClassificationResult(BaseModel):
    label: str
    confidence: float
    is_leak: bool
    raw_scores: Dict[str, float]


LEAK_KEYWORDS_STRONG = [
    "leak", "leaked", "leaks", "leaker", "leakers",
    "rumor", "rumour", "rumors", "rumoured", "rumored",
    "unreleased", "prototype", "unannounced",
    "exclusive", "first look", "hands-on",
    "cad render", "render leak", "dummy unit",
    "supply chain", "supply-chain",
    "sources say", "according to sources", "sources claim",
    "tipster", "insider",
]

LEAK_KEYWORDS_MEDIUM = [
    "reportedly", "allegedly", "apparently",
    "expected to", "is expected", "are expected",
    "could feature", "may feature", "will feature",
    "could include", "may include", "will include",
    "tipped to", "slated for", "set to launch",
    "spotted in", "appears in", "found in",
    "benchmark", "benchmarks", "geekbench", "antutu", "3dmark",
    "specs", "specifications", "spec sheet",
    "launch date", "release date", "launch window",
    "price leak", "pricing leak",
    "certification", "fcc filing", "fcc certification",
    "patent", "patent filing", "patent application",
    "upcoming", "next-gen", "next gen", "next generation",
    "early access", "pre-release", "pre-production",
    "teardown", "disassembly",
]

LEAK_KEYWORDS_WEAK = [
    "may", "might", "could", "would", "should",
    "suggests", "hints", "hinting", "hint",
    "reveal", "reveals", "revealed",
    "confirm", "confirms", "confirmed",
    "announce", "announces", "announced",
    "launch", "launching", "unveil", "unveils",
    "feature", "features", "featuring",
    "upgrade", "upgrades", "upgraded",
    "redesign", "redesigned",
    "new", "latest", "updated",
]

TECH_ENTITIES = {
    "apple", "iphone", "ipad", "macbook", "mac pro", "mac mini", "airpods",
    "samsung", "galaxy", "pixel", "nvidia", "rtx", "geforce",
    "amd", "radeon", "ryzen", "epyc", "intel", "core ultra", "arc",
    "qualcomm", "snapdragon", "mediatek", "dimensity",
    "microsoft", "surface", "xbox", "sony", "playstation", "ps5", "ps6",
    "google", "oneplus", "xiaomi", "oppo", "vivo", "huawei",
    "openai", "gpt", "chatgpt", "anthropic", "claude", "gemini",
    "meta", "quest", "vision pro",
    "nvidia", "tesla", "switch 2", "nintendo",
    "tsmc", "3nm", "2nm", "chipset", "soc",
}


class LeakClassifier:
    """Rule-based leak classifier — fast and tuned for tech news."""

    def __init__(self, model_path: str = None):
        pass

    def classify(self, text: str) -> ClassificationResult:
        return self._classify_rules(text)

    def _classify_rules(self, text: str) -> ClassificationResult:
        if not text or len(text.strip()) < 10:
            return self._not_leak(0.1)

        text_lower = text.lower()

        strong = sum(1 for kw in LEAK_KEYWORDS_STRONG if kw in text_lower)
        medium = sum(1 for kw in LEAK_KEYWORDS_MEDIUM if kw in text_lower)
        weak = sum(1 for kw in LEAK_KEYWORDS_WEAK if kw in text_lower)
        entity_hits = sum(1 for e in TECH_ENTITIES if e in text_lower)

        score = strong * 0.35 + medium * 0.20 + weak * 0.05 + entity_hits * 0.05

        is_leak = False
        if strong >= 1:
            is_leak = True
        elif medium >= 1 and entity_hits >= 1:
            is_leak = True
        elif medium >= 2:
            is_leak = True
        elif weak >= 2 and entity_hits >= 1:
            is_leak = True

        if is_leak:
            confidence = min(0.95, 0.55 + score * 0.10)
        else:
            confidence = max(0.15, 0.50 - score * 0.10)

        label = "LEAK" if is_leak else "NOT_LEAK"
        return ClassificationResult(
            label=label,
            confidence=round(confidence, 4),
            is_leak=is_leak,
            raw_scores={
                "LEAK": round(confidence if is_leak else 1 - confidence, 4),
                "NOT_LEAK": round(1 - confidence if is_leak else confidence, 4),
            },
        )

    def _not_leak(self, conf: float) -> ClassificationResult:
        return ClassificationResult(
            label="NOT_LEAK", confidence=conf, is_leak=False,
            raw_scores={"LEAK": round(1 - conf, 4), "NOT_LEAK": round(conf, 4)},
        )

    def classify_batch(self, texts: List[str]) -> List[ClassificationResult]:
        return [self.classify(t) for t in texts]
