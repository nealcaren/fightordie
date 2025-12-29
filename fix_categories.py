#!/usr/bin/env python3
"""
Fix category YAML formatting in .qmd files.
Removes empty entries and ensures proper YAML structure.
"""

import re
from pathlib import Path

VOLUMES_DIR = Path("Volumes")

def fix_categories_in_file(file_path):
    """Fix category formatting in a .qmd file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return False

    frontmatter = match.group(1)
    body = match.group(2)

    # Find categories section
    # Pattern to match: categories: followed by potential list items
    categories_pattern = r'categories:(?:\s*\[\])?((?:\s*-\s*[^\n]*\n)*)'

    def process_categories(m):
        categories_content = m.group(1)
        # Extract all non-empty category values
        categories = []
        for line in categories_content.split('\n'):
            line = line.strip()
            if line.startswith('-'):
                value = line[1:].strip().strip('"').strip("'").strip()
                if value:  # Only keep non-empty categories
                    categories.append(value)

        # Return formatted YAML
        if categories:
            result = "categories:\n"
            for cat in categories:
                result += f"  - {cat}\n"
            return result.rstrip()
        else:
            return "categories: []"

    new_frontmatter = re.sub(categories_pattern, process_categories, frontmatter)

    if new_frontmatter != frontmatter:
        new_content = f"---\n{new_frontmatter}\n---\n{body}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False

def main():
    article_files = list(VOLUMES_DIR.rglob("*.qmd"))
    fixed = 0

    for file_path in article_files:
        try:
            if fix_categories_in_file(file_path):
                fixed += 1
                print(f"✅ Fixed: {file_path}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\nFixed {fixed} files")

if __name__ == "__main__":
    main()
