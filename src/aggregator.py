"""News aggregator module."""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import hashlib
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl

CACHE_DB = Path(__file__).parent.parent / "data" / "cache.db"


class NewsItem(BaseModel):
    """Single news item."""

    title: str
    url: str
    source: str
    published_at: datetime
    content: Optional[str] = None
    summary: Optional[str] = None


class NewsAggregator:
    """Fetches news from various sources."""

    SOURCES = {
        "coindesk": {
            "name": "CoinDesk",
            "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "homepage": "https://www.coindesk.com/",
        },
        "cointelegraph": {
            "name": "Cointelegraph",
            "rss": "https://cointelegraph.com/rss",
            "homepage": "https://cointelegraph.com/",
        },
        "bitcoin_magazine": {
            "name": "Bitcoin Magazine",
            "rss": "https://bitcoinmagazine.com/.rss/full/",
            "homepage": "https://bitcoinmagazine.com/",
        },
        "decrypt": {
            "name": "Decrypt",
            "rss": "https://decrypt.co/feed",
            "homepage": "https://decrypt.co/",
        },
    }

    def __init__(self, cache_db: Path = CACHE_DB):
        self.cache_db = cache_db
        self._init_cache()

    def _init_cache(self):
        """Initialize SQLite cache."""
        self.cache_db.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.cache_db)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS news_cache (
                url_hash TEXT PRIMARY KEY,
                data TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()

    def _get_cache(self, url: str) -> Optional[Dict]:
        """Get cached news item."""
        conn = sqlite3.connect(self.cache_db)
        url_hash = hashlib.md5(url.encode()).hexdigest()

        cursor = conn.execute(
            "SELECT data, cached_at FROM news_cache WHERE url_hash = ?",
            (url_hash,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            data, cached_at = row
            # Cache is valid for 2 hours
            if datetime.now() - datetime.fromisoformat(cached_at) < timedelta(hours=2):
                return json.loads(data)

        return None

    def _set_cache(self, url: str, data: Dict):
        """Cache news item."""
        conn = sqlite3.connect(self.cache_db)
        url_hash = hashlib.md5(url.encode()).hexdigest()

        conn.execute(
            """
            INSERT OR REPLACE INTO news_cache (url_hash, data, cached_at)
            VALUES (?, ?, ?)
            """,
            (url_hash, json.dumps(data), datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

    def _fetch_rss(self, source_key: str) -> List[NewsItem]:
        """Fetch news from RSS feed."""
        source = self.SOURCES[source_key]
        items = []

        try:
            feed = feedparser.parse(source["rss"])

            for entry in feed.entries:
                # Check cache
                cached = self._get_cache(entry.link)
                if cached:
                    items.append(NewsItem(**cached))
                    continue

                # Parse published date
                published_at = datetime.now()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])

                # Get summary
                summary = entry.get("summary", "")
                # Strip HTML tags
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text(strip=True)

                # Create item
                item = NewsItem(
                    title=entry.get("title", ""),
                    url=entry.link,
                    source=source["name"],
                    published_at=published_at,
                    summary=summary[:500] if summary else None,
                )

                # Cache it
                self._set_cache(entry.link, item.model_dump())

                items.append(item)

        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")

        return items

    def _scrape_homepage(self, source_key: str) -> List[NewsItem]:
        """Fallback: Scrape homepage headlines."""
        source = self.SOURCES[source_key]
        items = []

        try:
            response = requests.get(source["homepage"], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try common headline selectors
            for selector in ["h2 a", "h3 a", ".article-title a", "[data-test='article-title']"]:
                links = soup.select(selector)
                if links:
                    for link in links[:10]:  # Max 10 articles per source
                        url = link.get("href", "")
                        title = link.get_text(strip=True)

                        if url and title:
                            # Resolve relative URLs
                            if not url.startswith("http"):
                                url = source["homepage"].rstrip("/") + url

                            # Check cache
                            cached = self._get_cache(url)
                            if cached:
                                items.append(NewsItem(**cached))
                                continue

                            item = NewsItem(
                                title=title,
                                url=url,
                                source=source["name"],
                                published_at=datetime.now(),
                            )

                            # Cache it
                            self._set_cache(url, item.model_dump())

                            items.append(item)

                    break  # Found a working selector

        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")

        return items

    def fetch(
        self, hours: int = 24, sources: Optional[List[str]] = None
    ) -> List[NewsItem]:
        """Fetch news from all sources within time window."""
        if sources is None:
            sources = list(self.SOURCES.keys())

        all_items = []
        cutoff = datetime.now() - timedelta(hours=hours)

        for source_key in sources:
            # Try RSS first
            items = self._fetch_rss(source_key)

            # Fallback to scraping if RSS is empty
            if not items:
                print(f"RSS empty for {self.SOURCES[source_key]['name']}, trying scraping...")
                items = self._scrape_homepage(source_key)

            # Filter by time
            items = [item for item in items if item.published_at > cutoff]
            all_items.extend(items)

        # Sort by published date (newest first)
        all_items.sort(key=lambda x: x.published_at, reverse=True)

        return all_items
