"""
URL normalization for crawl deduplication (PROJECT_SPEC_CONTINUATION §1.6).
"""
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term",
    "utm_content", "fbclid", "gclid", "ref", "source",
    "share_id", "si", "t", "s",
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL to prevent duplicate crawling of the same content.
    Lowercase scheme/host, remove default ports, tracking params, trailing slash.
    """
    if not url or not url.strip():
        return ""
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = (parsed.netloc or "").lower()

    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
    if netloc.startswith("www."):
        netloc = netloc[4:]

    params = parse_qs(parsed.query, keep_blank_values=False)
    cleaned_params = {
        k: v for k, v in params.items()
        if k.lower() not in TRACKING_PARAMS
    }
    sorted_query = urlencode(sorted(cleaned_params.items()), doseq=True)
    path = parsed.path.rstrip("/") or "/"

    return urlunparse((scheme, netloc, path, "", sorted_query, ""))
