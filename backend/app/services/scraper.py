"""URL to article text extraction service."""

from urllib.parse import urlparse
from newspaper import Article
from bs4 import BeautifulSoup
import requests


def scrape_article(url: str) -> dict:
    """Extract article content from a URL.

    Uses newspaper3k as primary extractor, falls back to BeautifulSoup.

    Returns:
        dict with title, text, authors, publish_date, source_domain, success.
    """
    domain = _extract_domain(url)

    try:
        result = _newspaper_extract(url)
        if result["text"] and len(result["text"]) > 100:
            result["source_domain"] = domain
            return result
    except Exception:
        pass

    # Fallback to BeautifulSoup
    try:
        result = _beautifulsoup_extract(url)
        result["source_domain"] = domain
        return result
    except Exception as e:
        return {
            "title": "",
            "text": "",
            "authors": [],
            "publish_date": None,
            "source_domain": domain,
            "success": False,
            "error": str(e),
        }


def _newspaper_extract(url: str) -> dict:
    """Extract article using newspaper3k."""
    article = Article(url)
    article.download()
    article.parse()

    return {
        "title": article.title or "",
        "text": article.text or "",
        "authors": article.authors or [],
        "publish_date": str(article.publish_date) if article.publish_date else None,
        "success": bool(article.text),
    }


def _beautifulsoup_extract(url: str) -> dict:
    """Fallback extraction using BeautifulSoup."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Extract title
    title = ""
    if soup.title:
        title = soup.title.string or ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"]

    # Extract main article text
    text = ""
    # Try common article containers
    article_selectors = [
        "article",
        '[role="article"]',
        ".article-body",
        ".story-body",
        ".post-content",
        ".entry-content",
        "#article-body",
        ".article-content",
    ]
    for selector in article_selectors:
        container = soup.select_one(selector)
        if container:
            paragraphs = container.find_all("p")
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if len(text) > 100:
                break

    # Fallback: get all paragraphs
    if len(text) < 100:
        paragraphs = soup.find_all("p")
        text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    # Extract authors
    authors = []
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta and author_meta.get("content"):
        authors = [author_meta["content"]]

    # Extract publish date
    publish_date = None
    date_meta = soup.find("meta", attrs={"property": "article:published_time"})
    if date_meta and date_meta.get("content"):
        publish_date = date_meta["content"]

    return {
        "title": title,
        "text": text,
        "authors": authors,
        "publish_date": publish_date,
        "success": bool(text),
    }


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.lower()
