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
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

CACHE_DB = Path(__file__).parent.parent / "data" / "cache.db"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def __init__(self, cache_db: Path = CACHE_DB, max_workers: int = 4):
        """Initialize aggregator.

        Args:
            cache_db: Path to cache database
            max_workers: Number of parallel workers for fetching
        """
        self.cache_db = cache_db
        self.max_workers = max_workers
        self._init_cache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; PilkNewsTrader/1.0)'
        })

    def __del__(self):
        """Cleanup session on deletion."""
        if hasattr(self, 'session'):
            self.session.close()

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
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cached_at
            ON news_cache(cached_at)
        """
        )
        conn.commit()
        conn.close()

    def _get_cache(self, url: str) -> Optional[Dict]:
        """Get cached news item."""
        try:
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
                    # Parse JSON with datetime string handling
                    result = json.loads(data)
                    # Convert published_at string back to datetime
                    if "published_at" in result and isinstance(result["published_at"], str):
                        result["published_at"] = datetime.fromisoformat(result["published_at"])
                    return result

        except Exception as e:
            logger.warning(f"Cache get error: {e}")

        return None

    def _set_cache(self, url: str, data: Dict):
        """Cache news item."""
        try:
            conn = sqlite3.connect(self.cache_db)
            url_hash = hashlib.md5(url.encode()).hexdigest()

            # Convert datetime to string for JSON serialization
            def json_default(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")

            conn.execute(
                """
                INSERT OR REPLACE INTO news_cache (url_hash, data, cached_at)
                VALUES (?, ?, ?)
                """,
                (url_hash, json.dumps(data, default=json_default), datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    def _fetch_rss(self, source_key: str) -> List[NewsItem]:
        """Fetch news from RSS feed."""
        source = self.SOURCES[source_key]
        items = []

        try:
            feed = feedparser.parse(source["rss"])

            for entry in feed.entries[:50]:  # Limit to 50 per source
                # Check cache
                cached = self._get_cache(entry.link)
                if cached:
                    items.append(NewsItem(**cached))
                    continue

                # Parse published date
                published_at = datetime.now()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except (ValueError, TypeError):
                        pass

                # Get summary
                summary = entry.get("summary", "")
                # Strip HTML tags
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text(strip=True)

                # Create item
                item = NewsItem(
                    title=entry.get("title", "")[:200],  # Limit title length
                    url=entry.link,
                    source=source["name"],
                    published_at=published_at,
                    summary=summary[:500] if summary else None,
                )

                # Cache it
                self._set_cache(entry.link, item.model_dump())

                items.append(item)

        except Exception as e:
            logger.warning(f"Error fetching {source['name']} RSS: {e}")

        return items

    def _scrape_homepage(self, source_key: str) -> List[NewsItem]:
        """Fallback: Scrape homepage headlines."""
        source = self.SOURCES[source_key]
        items = []

        try:
            response = self.session.get(source["homepage"], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try common headline selectors
            selectors = ["h2 a", "h3 a", ".article-title a", "[data-test='article-title']", "article h2 a"]

            for selector in selectors:
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
                                title=title[:200],
                                url=url,
                                source=source["name"],
                                published_at=datetime.now(),
                            )

                            # Cache it
                            self._set_cache(url, item.model_dump())

                            items.append(item)

                    break  # Found a working selector

        except Exception as e:
            logger.warning(f"Error scraping {source['name']}: {e}")

        return items

    def fetch(
        self, hours: int = 24, sources: Optional[List[str]] = None
    ) -> List[NewsItem]:
        """Fetch news from all sources within time window."""
        if sources is None:
            sources = list(self.SOURCES.keys())

        all_items = []
        cutoff = datetime.now() - timedelta(hours=hours)

        # Parallel fetch from all sources
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(self._fetch_source, source_key): source_key
                for source_key in sources
            }

            for future in as_completed(future_to_source):
                source_key = future_to_source[future]
                try:
                    items = future.result(timeout=30)
                    all_items.extend(items)
                    logger.info(f"Fetched {len(items)} from {self.SOURCES[source_key]['name']}")
                except Exception as e:
                    logger.warning(f"Failed to fetch {source_key}: {e}")

        # Sort by published date (newest first)
        all_items.sort(key=lambda x: x.published_at, reverse=True)

        # Filter by time
        all_items = [item for item in all_items if item.published_at > cutoff]

        logger.info(f"Total: {len(all_items)} articles within {hours}h window")

        return all_items

    def _fetch_source(self, source_key: str) -> List[NewsItem]:
        """Fetch from a single source with fallback."""
        # Try RSS first
        items = self._fetch_rss(source_key)

        # Fallback to scraping if RSS is empty
        if not items:
            logger.info(f"RSS empty for {self.SOURCES[source_key]['name']}, trying scraping...")
            items = self._scrape_homepage(source_key)

        return items
