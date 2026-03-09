"""
Abuse prevention and crawl limits (PROJECT_SPEC_CONTINUATION §10.4).
"""


class AbusePreventionConfig:
    """Configuration to prevent abusive or excessive crawling."""

    MAX_GLOBAL_REQUESTS_PER_MINUTE = 100
    MAX_PAGES_PER_DOMAIN_PER_DAY = 500
    BLACKLISTED_DOMAINS = {
        "facebook.com",
        "instagram.com",
        "linkedin.com",
    }
    PROHIBITED_CONTENT_TYPES = {
        "personal_information",
        "financial_data",
        "medical_information",
        "classified_information",
    }
    DATA_RETENTION_DAYS = 180
    AUTO_DISCOVERY_APPROVAL_THRESHOLD = 8
