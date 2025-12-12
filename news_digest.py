#!/usr/bin/env python

import argparse
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from src.summariser import NewsSummariser
from summarise_url import fetch_page_text


# Simple list of RSS/Atom feeds to query.
# For v0.1 we keep this small and focused.
RSS_FEEDS: List[str] = [
    "https://feeds.bbci.co.uk/news/rss.xml",               # top stories (global-ish)
    "https://feeds.bbci.co.uk/news/world/rss.xml",         # general world
    "https://feeds.bbci.co.uk/news/uk/rss.xml",            # UK
    "https://feeds.bbci.co.uk/news/world/europe/rss.xml",  # Europe
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml",    # Asia
    "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",  # US & Canada
    "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml",    # Middle East
]


def fetch_feed_items(feed_url: str) -> List[Dict[str, str]]:
    """
    Fetch items from an RSS/Atom feed URL.

    Returns a list of dicts, each with:
      - title
      - link
      - description

    This is a simple parser using BeautifulSoup on the XML.
    """
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[warning] Failed to fetch feed {feed_url}: {e}")
        return []

    xml = response.text
    soup = BeautifulSoup(xml, "xml")  # parse as XML

    items: List[Dict[str, str]] = []

    # Typical RSS uses <item>; Atom often uses <entry>.
    # We'll try both.
    for item in soup.find_all(["item", "entry"]):
        title_tag = item.find("title")
        link_tag = item.find("link")
        desc_tag = item.find("description") or item.find("summary")

        title = title_tag.get_text(strip=True) if title_tag else ""
        # For <link>, sometimes the URL is in href attribute (Atom) or text (RSS)
        if link_tag and link_tag.has_attr("href"):
            link = link_tag["href"]
        else:
            link = link_tag.get_text(strip=True) if link_tag else ""

        description = desc_tag.get_text(strip=True) if desc_tag else ""

        if not title and not description:
            continue

        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
            }
        )

    return items

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch recent news items from predefined feeds and summarise those "
            "that match a given query (e.g. 'Colchester', 'AI in Ipswich')."
        )
    )
    parser.add_argument(
        "query",
        type=str,
        help="Keyword or phrase to search for in news items (e.g. 'Colchester').",
    )
    parser.add_argument(
        "--max_articles",
        type=int,
        default=5,
        help="Maximum number of matching articles to summarise (default: 5).",
    )

    parser.add_argument(
        "--max_chars",
        type=int,
        default=300,
        help="Approximate maximum number of characters to keep in the TL;DR.",
    )

    args = parser.parse_args()

    query = args.query.strip()
    max_articles = args.max_articles
    max_chars = args.max_chars


    print("\n[news-digest] Starting digest")
    print(f"Query       : {query!r}")
    print(f"Max articles: {max_articles}")
    print(f"Max chars   : {max_chars}")
    print("\nFetching feeds...\n")

    if not query:
        raise SystemExit("Error: query must not be empty.")

    # Collect items from all feeds
    all_items: List[Dict[str, str]] = []
    for feed_url in RSS_FEEDS:
        print(f"- Fetching feed: {feed_url}")
        feed_items = fetch_feed_items(feed_url)
        print(f"  -> {len(feed_items)} items retrieved")
        all_items.extend(feed_items)

    print(f"\nTotal items from all feeds: {len(all_items)}")

    # Filter items whose title or description contains the query (case-insensitive)
    query_lower = query.lower()
    matching_items: List[Dict[str, str]] = []
    for item in all_items:
        haystack = (item.get("title", "") + " " + item.get("description", "")).lower()
        if query_lower in haystack:
            matching_items.append(item)

    if not matching_items:
        print(f"\nNo items matched query {query!r}.")
        return

    print(f"\nFound {len(matching_items)} matching items.")
    print(f"Summarising up to {max_articles} article(s):\n")

    summariser = NewsSummariser()

    # Limit to max_articles
    for i, item in enumerate(matching_items[:max_articles], start=1):
        title = item.get("title", "").strip()
        link = item.get("link", "").strip()

        print(f"================ Article {i} ================")
        print(f"Title: {title}")
        if link:
            print(f"Link : {link}")

        if not link:
            print("No link available; skipping summarisation.\n")
            continue

        try:
            page_text = fetch_page_text(link)
        except Exception as e:
            print(f"Error fetching article text: {e}\n")
            continue

        if not page_text:
            print("Could not extract text from this article.\n")
            continue

        result = summariser.summarise(page_text, max_chars=max_chars)

        print("\n--- TL;DR ---\n")
        print(result.tldr)

        print("\n--- Bullet Points ---\n")
        for j, bullet in enumerate(result.bullet_points, start=1):
            print(f"{j}. {bullet}")

        print("\n============================================\n")




if __name__ == "__main__":
    main()
