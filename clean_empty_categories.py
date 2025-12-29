#!/usr/bin/env python3
"""
Quick script to remove empty category entries from .qmd files.
Fixes cases where categories have empty strings.
"""

import re
from pathlib import Path

VOLUMES_DIR = Path("Volumes")

def clean_categories(file_path):
    """Remove empty category entries from a .qmd file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match empty category entries
    # Match: categories: \n  - ""  OR  categories: \n  - ''  OR  categories: \n  -
    original = content

    # Remove empty string entries in categories
    content = re.sub(r'categories:\s*\n\s*-\s*["\']?\s*["\']?\s*\n', 'categories: []\n', content)

    # Also handle trailing empty entries after valid categories
    content = re.sub(r'(categories:\s*\n(?:\s*-\s*.+\n)*)\s*-\s*["\']?\s*["\']?\s*\n', r'\1', content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    article_files = list(VOLUMES_DIR.rglob("*.qmd"))
    cleaned = 0

    for file_path in article_files:
        if clean_categories(file_path):
            cleaned += 1
            print(f"✅ Cleaned: {file_path}")

    print(f"\nCleaned {cleaned} files")

if __name__ == "__main__":
    main()
