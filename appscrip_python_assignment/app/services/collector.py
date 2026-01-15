import urllib.parse
from typing import List

import httpx
from bs4 import BeautifulSoup

from app.schemas.analyze import CollectedData, MarketItem
from app.config import settings

SEARCH_URL = "https://duckduckgo.com/html"


async def _fetch_duckduckgo_html(query: str) -> str | None:
    params = {"q": query}
    url = f"{SEARCH_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": "trade-opportunities-bot/1.0 (+https://example.com)",
        "Accept-Language": "en-IN,en;q=0.9",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            return None
        return resp.text


def _parse_duckduckgo_html(html: str, max_items: int = 8) -> List[MarketItem]:
    soup = BeautifulSoup(html, "lxml")
    items: List[MarketItem] = []

    # DuckDuckGo HTML search uses .result__body etc.
    for result in soup.select(".result__body")[:max_items]:
        title_tag = result.select_one("a.result__a")
        snippet_tag = result.select_one(".result__snippet")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = title_tag.get("href")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        items.append(
            MarketItem(
                title=title,
                url=href,
                snippet=snippet,
            )
        )

    return items


async def collect_sector_info(sector: str, country: str = "India") -> CollectedData:
    """
    Fetch current-ish web information for the given sector.
    Uses DuckDuckGo HTML search and parses top results.
    """

    query = f"{sector} sector stock market news {country}"
    html = await _fetch_duckduckgo_html(query)
    if html:
        items = _parse_duckduckgo_html(html)
        if items:
            return CollectedData(
                sector=sector,
                country=country,
                source="duckduckgo",
                items=items,
            )

    # Fallback data to keep API functional even if search fails.
    fallback_items = [
        MarketItem(
            title=f"{sector.title()} sector overview in {country}",
            url=None,
            snippet=f"Fallback generated summary. Could not fetch live data, but this indicates the {sector} sector is important in {country}.",
        )
    ]
    return CollectedData(
        sector=sector,
        country=country,
        source="fallback",
        items=fallback_items,
    )
