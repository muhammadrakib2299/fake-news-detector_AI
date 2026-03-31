"""Source credibility checker service."""

import json
from pathlib import Path
from urllib.parse import urlparse


_credibility_data = None


def _load_credibility_data():
    """Load credibility database on first use."""
    global _credibility_data
    if _credibility_data is None:
        data_path = Path(__file__).parent / "sources_credibility.json"
        with open(data_path, "r") as f:
            raw = json.load(f)
        _credibility_data = raw["domains"]
    return _credibility_data


def extract_domain(url: str) -> str:
    """Extract the root domain from a URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # Remove www. prefix
    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname.lower()


def check_credibility(url: str) -> dict:
    """Check the credibility of a source URL.

    Returns:
        dict with credibility score, category, bias, and flags.
    """
    domains = _load_credibility_data()
    domain = extract_domain(url)

    if not domain:
        return _unknown_source(url)

    # Direct lookup
    if domain in domains:
        entry = domains[domain]
        return _build_result(domain, entry)

    # Try parent domain (e.g., news.bbc.co.uk -> bbc.co.uk)
    parts = domain.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[i:])
        if parent in domains:
            entry = domains[parent]
            return _build_result(domain, entry)

    return _unknown_source(domain)


def check_credibility_from_domain(domain: str) -> dict:
    """Check credibility using just a domain string (no URL parsing)."""
    domains = _load_credibility_data()
    domain = domain.lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    if domain in domains:
        return _build_result(domain, domains[domain])

    return _unknown_source(domain)


def _build_result(domain: str, entry: dict) -> dict:
    """Build credibility result from database entry."""
    score = entry["score"]

    # Determine credibility level
    if score >= 80:
        level = "high"
    elif score >= 60:
        level = "medium"
    elif score >= 40:
        level = "low"
    else:
        level = "very_low"

    # Flag unreliable categories
    unreliable_categories = {
        "conspiracy", "fake_news", "state_propaganda", "pseudoscience",
        "health_misinformation", "satire", "extreme_partisan",
    }
    is_flagged = entry.get("category", "") in unreliable_categories

    return {
        "domain": domain,
        "score": score,
        "credibility_level": level,
        "category": entry.get("category", "unknown"),
        "bias": entry.get("bias", "unknown"),
        "is_flagged": is_flagged,
        "in_database": True,
        # Normalized score for pipeline (0 = very credible, 1 = not credible)
        "credibility_score": round(1 - (score / 100), 4),
    }


def _unknown_source(domain: str) -> dict:
    """Return result for unknown sources."""
    return {
        "domain": domain,
        "score": 50,
        "credibility_level": "unknown",
        "category": "unknown",
        "bias": "unknown",
        "is_flagged": False,
        "in_database": False,
        "credibility_score": 0.5,
    }
