#!/usr/bin/env python

import argparse
from pathlib import Path

from src.summariser import NewsSummariser


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise a local text/markdown file (dummy version for now)."
    )
    parser.add_argument(
        "filepath",
        type=str,
        help="Path to the .txt or .md file to summarise.",
    )
    parser.add_argument(
        "--max_chars",
        type=int,
        default=300,
        help="Maximum number of characters to keep in the TL;DR.",
    )

    args = parser.parse_args()
    file_path = Path(args.filepath)

    if not file_path.exists():
        raise SystemExit(f"Error: file not found: {file_path}")

    # Read file content
    text = file_path.read_text(encoding="utf-8", errors="ignore")

    summariser = NewsSummariser()
    result = summariser.summarise(text, max_chars=args.max_chars)

    print("\n================ TL;DR (MODEL) ================\n")
    print(result.tldr)
    print("\n============= Bullet Points (PLACEHOLDER) =====\n")

    for i, bullet in enumerate(result.bullet_points, start=1):
        print(f"{i}. {bullet}")
    print("\n===============================================\n")


if __name__ == "__main__":
    main()
