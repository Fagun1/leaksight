import re
from typing import List
from pydantic import BaseModel
import logging

logger = logging.getLogger("ai.entity_extractor")


class ExtractedEntity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    confidence: float


class EntityExtractionResult(BaseModel):
    entities: List[ExtractedEntity]
    companies: List[str]
    products: List[str]
    features: List[str]
    timeframes: List[str]
    specs: List[str]


class EntityExtractor:
    """Extracts tech-specific entities using regex patterns."""

    COMPANY_KEYWORDS = {
        "apple", "nvidia", "amd", "intel", "samsung", "google", "microsoft",
        "qualcomm", "mediatek", "sony", "meta", "openai", "anthropic",
        "tsmc", "lg", "huawei", "xiaomi", "oneplus", "valve", "nintendo",
    }

    PRODUCT_PATTERNS = [
        r"iPhone\s*\d+\s*(Pro\s*Max|Pro|Plus|Ultra|mini)?",
        r"iPad\s*(Pro|Air|mini)?\s*M?\d*",
        r"MacBook\s*(Pro|Air)\s*M?\d*",
        r"Galaxy\s*S\d+\s*(Ultra|Plus|\+|FE)?",
        r"Pixel\s*\d+\s*(Pro|a)?",
        r"RTX\s*\d{4}\s*(Ti|Super)?",
        r"RX\s*\d{4}\s*(XT|XTX)?",
        r"Ryzen\s*\d+\s*\d{4}\w*",
        r"Core\s*(Ultra\s*)?\d+\s*\d{3,4}\w*",
        r"Snapdragon\s*\d+\s*(Gen\s*\d)?",
        r"PS\d+|PlayStation\s*\d+",
        r"Switch\s*2|Nintendo\s*Switch",
        r"M\d+\s*(Pro|Max|Ultra)?",
    ]

    FEATURE_KEYWORDS = [
        "dynamic island", "face id", "touch id", "promotion", "oled",
        "mini-led", "micro-led", "under-display", "periscope lens",
        "titanium", "usb-c", "thunderbolt", "wifi 7", "foldable",
        "ray tracing", "dlss", "fsr", "cuda core", "neural engine",
    ]

    def extract(self, text: str) -> EntityExtractionResult:
        entities = []
        text_lower = text.lower()

        for company in self.COMPANY_KEYWORDS:
            for m in re.finditer(re.escape(company), text_lower, re.I):
                entities.append(ExtractedEntity(
                    text=m.group(), label="COMPANY",
                    start=m.start(), end=m.end(), confidence=0.9
                ))

        for pattern in self.PRODUCT_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=m.group(), label="PRODUCT",
                    start=m.start(), end=m.end(), confidence=0.9
                ))

        for feature in self.FEATURE_KEYWORDS:
            if feature in text_lower:
                idx = text_lower.find(feature)
                entities.append(ExtractedEntity(
                    text=text[idx:idx+len(feature)],
                    label="FEATURE", start=idx, end=idx+len(feature),
                    confidence=0.85
                ))

        timeframe_pattern = r"(Q[1-4]\s*\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}|\d{4})"
        for m in re.finditer(timeframe_pattern, text, re.I):
            entities.append(ExtractedEntity(
                text=m.group(), label="TIMEFRAME",
                start=m.start(), end=m.end(), confidence=0.8
            ))

        entities = self._deduplicate_entities(entities)

        return EntityExtractionResult(
            entities=entities,
            companies=[e.text for e in entities if e.label == "COMPANY"],
            products=[e.text for e in entities if e.label == "PRODUCT"],
            features=[e.text for e in entities if e.label == "FEATURE"],
            timeframes=[e.text for e in entities if e.label == "TIMEFRAME"],
            specs=[e.text for e in entities if e.label == "SPEC"],
        )

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        seen = {}
        for ent in entities:
            key = (ent.text.lower(), ent.label)
            if key not in seen or ent.confidence > seen[key].confidence:
                seen[key] = ent
        return list(seen.values())
