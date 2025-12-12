#!/usr/bin/env python

import argparse
from pathlib import Path  # not really needed yet, but nice to have if we log later

import requests
from bs4 import BeautifulSoup

from src.summariser import NewsSummariser


def fetch_page_text(url: str) -> str:
    """
    Download the web page at `url` and extract plain text using BeautifulSoup.

    This is a very simple first version:
    - we fetch the HTML,
    - parse it,
    - and return all visible text.

    Later we could get smarter about extracting just the main article body.
    """
    headers = {
        "User-Agent": "news-tldr-toolkit/0.1 (+https://github.com/your-username/news-tldr-toolkit)"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # raise an error if status code is not 200

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Simple approach: get all text from the page.
    # This may include menus/footer etc., but it's okay for v1.
    text = soup.get_text(separator="\n")
    # Clean up extra whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return clean_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise a news article from a URL into a TL;DR and bullet points."
    )
    parser.add_argument(
        "url",
        type=str,
        help="URL of the news article or web page to summarise.",
    )
    parser.add_argument(
        "--max_chars",
        type=int,
        default=300,
        help="Approximate maximum number of characters to keep in the TL;DR.",
    )

    args = parser.parse_args()
    url = args.url

    print(f"\nFetching page: {url}\n")

    try:
        text = fetch_page_text(url)
    except Exception as e:
        raise SystemExit(f"Error fetching URL: {e}")

    if not text:
        raise SystemExit("Could not extract any text from the page.")

    summariser = NewsSummariser()
    result = summariser.summarise(text, max_chars=args.max_chars)

    print("\n================ TL;DR (MODEL) ================\n")
    print(result.tldr)
    print("\n============= Bullet Points (MODEL) ==========\n")
    for i, bullet in enumerate(result.bullet_points, start=1):
        print(f"{i}. {bullet}")
    print("\n===============================================\n")


if __name__ == "__main__":
    main()
