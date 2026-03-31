"""Google Fact Check Tools API integration."""

import httpx
from ..config import settings


FACT_CHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


async def check_facts(query: str, language_code: str = "en") -> dict:
    """Search for existing fact-checks related to a claim.

    Uses Google Fact Check Tools API to find matching fact-checks.
    Degrades gracefully if API key is not configured or API is unavailable.

    Returns:
        dict with matching fact-checks, scores, and metadata.
    """
    if not settings.google_fact_check_api_key:
        return _no_api_key_result()

    try:
        # Truncate query to first 200 chars for API search
        search_query = query[:200] if len(query) > 200 else query

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                FACT_CHECK_API_URL,
                params={
                    "query": search_query,
                    "languageCode": language_code,
                    "key": settings.google_fact_check_api_key,
                },
            )

        if response.status_code != 200:
            return _api_error_result(f"API returned status {response.status_code}")

        data = response.json()
        claims = data.get("claims", [])

        if not claims:
            return _no_matches_result()

        # Process matched claims
        matched_checks = []
        for claim in claims[:5]:  # Top 5 matches
            claim_review = claim.get("claimReview", [{}])[0]
            matched_checks.append({
                "claim_text": claim.get("text", ""),
                "claimant": claim.get("claimant", "Unknown"),
                "rating": claim_review.get("textualRating", "Unknown"),
                "publisher": claim_review.get("publisher", {}).get("name", "Unknown"),
                "url": claim_review.get("url", ""),
                "review_date": claim_review.get("reviewDate", ""),
                "language": claim_review.get("languageCode", language_code),
            })

        # Calculate fact-check score based on ratings
        fact_check_score = _calculate_score(matched_checks)

        return {
            "has_matches": True,
            "match_count": len(matched_checks),
            "matches": matched_checks,
            "fact_check_score": fact_check_score,
            "api_available": True,
        }

    except httpx.TimeoutException:
        return _api_error_result("API request timed out")
    except Exception as e:
        return _api_error_result(str(e))


def _calculate_score(matches: list) -> float:
    """Calculate a fake-news score from fact-check ratings.

    Returns 0-1 where 0 = confirmed true, 1 = confirmed false.
    """
    if not matches:
        return 0.5  # Neutral when no data

    # Map common ratings to scores
    rating_scores = {
        # Confirmed true
        "true": 0.0, "correct": 0.0, "accurate": 0.0,
        # Mostly true
        "mostly true": 0.15, "mostly correct": 0.15,
        # Half true
        "half true": 0.35, "mixture": 0.4, "mixed": 0.4,
        "partly true": 0.35, "partially true": 0.35,
        # Mostly false
        "mostly false": 0.7, "mostly incorrect": 0.7,
        "misleading": 0.65, "exaggerated": 0.6,
        # False
        "false": 0.9, "incorrect": 0.9, "wrong": 0.9,
        "pants on fire": 1.0, "fabricated": 1.0,
        # Unverifiable
        "unproven": 0.5, "unverified": 0.5,
    }

    scores = []
    for match in matches:
        rating = match["rating"].lower().strip()
        # Try exact match first
        if rating in rating_scores:
            scores.append(rating_scores[rating])
        else:
            # Try partial match
            matched = False
            for key, score in rating_scores.items():
                if key in rating:
                    scores.append(score)
                    matched = True
                    break
            if not matched:
                scores.append(0.5)  # Unknown rating

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def _no_api_key_result() -> dict:
    """Result when no API key is configured."""
    return {
        "has_matches": False,
        "match_count": 0,
        "matches": [],
        "fact_check_score": 0.5,
        "api_available": False,
        "note": "Google Fact Check API key not configured. Set GOOGLE_FACT_CHECK_API_KEY in .env",
    }


def _no_matches_result() -> dict:
    """Result when API returns no matches."""
    return {
        "has_matches": False,
        "match_count": 0,
        "matches": [],
        "fact_check_score": 0.5,
        "api_available": True,
    }


def _api_error_result(error: str) -> dict:
    """Result when API call fails."""
    return {
        "has_matches": False,
        "match_count": 0,
        "matches": [],
        "fact_check_score": 0.5,
        "api_available": False,
        "error": error,
    }
