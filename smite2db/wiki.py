"""MediaWiki API client for the official SMITE 2 wiki only."""

from __future__ import annotations

import json
import time
from typing import Any, Iterator
from urllib.parse import quote

import requests

WIKI_ORIGIN = "https://wiki.smite2.com"
API_URL = f"{WIKI_ORIGIN}/api.php"
USER_AGENT = "Smite2Database/1.0 (local research; SMITE 2 only; contact: local)"


class WikiClient:
    """Thin, polite client for wiki.smite2.com."""

    def __init__(self, delay: float = 0.35, session: requests.Session | None = None):
        self.delay = delay
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request = 0.0

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.monotonic()

    def api(self, **params: Any) -> dict[str, Any]:
        params.setdefault("format", "json")
        params.setdefault("formatversion", "2")
        self._throttle()
        resp = self.session.get(API_URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"Wiki API error: {data['error']}")
        return data

    def get_wikitext(self, title: str) -> str:
        data = self.api(action="parse", page=title, prop="wikitext")
        return data["parse"]["wikitext"]

    def get_page_json(self, title: str) -> Any:
        """Load a Data:*.json page (or any page that is pure JSON)."""
        data = self.api(
            action="query",
            titles=title,
            prop="revisions",
            rvprop="content",
            rvslots="main",
        )
        pages = data["query"]["pages"]
        if not pages:
            raise FileNotFoundError(title)
        page = pages[0]
        if page.get("missing"):
            raise FileNotFoundError(title)
        content = page["revisions"][0]["slots"]["main"]["content"]
        return json.loads(content)

    def category_members(self, category: str, limit: int = 500) -> list[str]:
        """Return page titles in a category (handles continuation)."""
        titles: list[str] = []
        cont: dict[str, str] = {}
        while True:
            params: dict[str, Any] = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category if category.startswith("Category:") else f"Category:{category}",
                "cmlimit": min(limit, 500),
                "cmtype": "page",
            }
            params.update(cont)
            data = self.api(**params)
            for m in data["query"]["categorymembers"]:
                titles.append(m["title"])
            if "continue" not in data:
                break
            cont = data["continue"]
            if len(titles) >= limit:
                break
        return titles

    def all_pages(self, prefix: str, namespace: int = 0, limit: int = 500) -> list[str]:
        titles: list[str] = []
        cont: dict[str, str] = {}
        while True:
            params: dict[str, Any] = {
                "action": "query",
                "list": "allpages",
                "apprefix": prefix,
                "apnamespace": namespace,
                "aplimit": min(limit, 500),
            }
            params.update(cont)
            data = self.api(**params)
            for p in data["query"]["allpages"]:
                titles.append(p["title"])
            if "continue" not in data:
                break
            cont = data["continue"]
            if len(titles) >= limit:
                break
        return titles

    @staticmethod
    def page_url(title: str) -> str:
        return f"{WIKI_ORIGIN}/w/{quote(title.replace(' ', '_'), safe='()%')}"
