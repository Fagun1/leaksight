"""
Crawl depth and limits per domain (PROJECT_SPEC_CONTINUATION §1.5).
"""
CRAWL_DEPTH_CONFIG = {
    "reddit.com": {
        "max_depth": 2,
        "follow_external_links": True,
        "max_pages_per_session": 50,
    },
    "macrumors.com": {
        "max_depth": 1,
        "follow_external_links": False,
        "max_pages_per_session": 30,
    },
    "notebookcheck.net": {
        "max_depth": 1,
        "follow_external_links": False,
        "max_pages_per_session": 40,
    },
    "twitter.com": {
        "max_depth": 1,
        "follow_external_links": True,
        "max_pages_per_session": 100,
    },
    "x.com": {
        "max_depth": 1,
        "follow_external_links": True,
        "max_pages_per_session": 100,
    },
    "__default__": {
        "max_depth": 1,
        "follow_external_links": False,
        "max_pages_per_session": 20,
    },
}


def get_depth_config(domain: str) -> dict:
    """Return config for domain or default."""
    if not domain:
        return CRAWL_DEPTH_CONFIG["__default__"].copy()
    domain = domain.lower().replace("www.", "")
    return CRAWL_DEPTH_CONFIG.get(domain, CRAWL_DEPTH_CONFIG["__default__"]).copy()
