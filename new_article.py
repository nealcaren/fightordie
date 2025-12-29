#!/usr/bin/env python3
"""
Create a new article file from template.

Usage:
    python new_article.py --volume 12 --issue 3 --title "The Crisis" --date "March 1916"
"""

import argparse
import re
from pathlib import Path

VOLUMES_DIR = Path("Volumes")

def slugify(text):
    """Convert title to filename-safe slug."""
    # Remove non-alphanumeric characters
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces and multiple hyphens with single underscore
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug

def create_article(volume, issue, title, date, pages=None):
    """Create a new article file from template."""

    # Create directory path
    issue_str = str(issue).zfill(2)
    article_dir = VOLUMES_DIR / str(volume) / issue_str
    article_dir.mkdir(parents=True, exist_ok=True)

    # Create filename
    filename = slugify(title) + ".qmd"
    file_path = article_dir / filename

    # Check if file already exists
    if file_path.exists():
        print(f"❌ File already exists: {file_path}")
        return None

    # Build page range
    page_field = f"  page: {pages}" if pages else "  page: XXX"

    # Create content from template
    content = f"""---
title: '{title}'
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: {date}
categories: []
citation:
  type: article-journal
  container-title: The Crisis
  volume: {volume}
  issue: {issue}
{page_field}
google-scholar: true

format:
  html:
    toc: false
    appendix-cite-as: display
---

<!-- Add article content below -->
"""

    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created: {file_path}")
    print(f"\nNext steps:")
    print(f"1. Edit {file_path} and add article content")
    print(f"2. Run: python process_new_articles.py")
    print(f"3. Preview: quarto preview")

    return file_path

def main():
    parser = argparse.ArgumentParser(
        description="Create a new article file from template"
    )
    parser.add_argument(
        '--volume',
        type=int,
        required=True,
        help='Volume number (e.g., 12)'
    )
    parser.add_argument(
        '--issue',
        type=int,
        required=True,
        help='Issue number (e.g., 3)'
    )
    parser.add_argument(
        '--title',
        type=str,
        required=True,
        help='Article title (e.g., "The Crisis of Democracy")'
    )
    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help='Publication date (e.g., "March 1916")'
    )
    parser.add_argument(
        '--pages',
        type=str,
        help='Page range (e.g., "113-114" or "113")'
    )

    args = parser.parse_args()

    create_article(
        volume=args.volume,
        issue=args.issue,
        title=args.title,
        date=args.date,
        pages=args.pages
    )

if __name__ == "__main__":
    main()
