#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.0.0",
# ]
# ///
"""
Find articles not by Du Bois and fix descriptions that incorrectly attribute to him.

Usage:
    python fix_non_dubois_descriptions.py --dry-run  # Preview
    python fix_non_dubois_descriptions.py            # Fix
"""

import os
import re
import argparse
from pathlib import Path
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VOLUMES_DIR = Path("Volumes")
MAX_CONTENT_LENGTH = 3000

def parse_qmd_file(file_path):
    """Parse a .qmd file and extract frontmatter and content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    match = re.match(r'^\s*---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    content = match.group(2).strip()

    # Extract author - check for both simple string and structured format
    author = "W.E.B. Du Bois"  # default

    # Try simple string format first: "author: Miller, Kelly"
    simple_match = re.search(r'^author:\s*([^\n-]+)$', frontmatter_text, re.MULTILINE)
    if simple_match:
        author_line = simple_match.group(1).strip()
        if author_line and not any(x in author_line.lower() for x in ['given:', 'family:', 'name:']):
            author = author_line
    else:
        # Try structured format
        family_match = re.search(r'family:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if family_match:
            family = family_match.group(1).strip()
            given_match = re.search(r'given:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if given_match:
                given = given_match.group(1).strip()
                author = f"{given} {family}"
            else:
                author = family

    # Extract title, date, description
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?$", frontmatter_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    date_match = re.search(r"^date:\s*(.+)$", frontmatter_text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "Unknown"

    desc_match = re.search(r'^description:\s*["\'](.+?)["\']$', frontmatter_text, re.MULTILINE)
    description = desc_match.group(1) if desc_match else ""

    return {
        'title': title,
        'date': date,
        'author': author,
        'description': description,
        'frontmatter_text': frontmatter_text,
        'content': content
    }

def is_dubois(author):
    """Check if author is Du Bois."""
    if not author:
        return True
    author_lower = author.lower()
    return 'du bois' in author_lower or 'dubois' in author_lower

def extract_preview(content, max_length=MAX_CONTENT_LENGTH):
    """Extract preview of article content."""
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)
    return content[:max_length].strip()

def generate_description(title, author, date, content_preview, client):
    """Generate SEO description with correct author attribution."""
    prompt = f"""Write a one-sentence SEO meta description (150 chars max) for this article from The Crisis magazine.

Title: {title}
Author: {author}
Date: {date}

Article preview:
{content_preview}

Requirements:
- ONE sentence only, under 150 characters
- Start with the AUTHOR'S name: "{author}"
- Format: "{author} in The Crisis (YEAR) argues/discusses/examines..."
- Focus on main argument or topic
- Be specific and compelling
- No quotes around the description itself

Example format: "Kelly Miller in The Crisis (1915) argues against woman suffrage, claiming gender differences make women unfit for politics."

Description:"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=200
        )

        description = response.choices[0].message.content
        if description:
            description = description.strip().strip('"').strip("'")
            description = description.replace('"', '\\"')
            return description
        return None
    except Exception as e:
        print(f"  ❌ Error generating description: {e}")
        return None

def update_description(frontmatter_text, new_description):
    """Replace description in frontmatter."""
    # Replace existing description
    new_frontmatter = re.sub(
        r'^description:\s*["\'].*?["\']$',
        f'description: "{new_description}"',
        frontmatter_text,
        flags=re.MULTILINE
    )
    return new_frontmatter

def main():
    parser = argparse.ArgumentParser(
        description="Fix descriptions for non-Du Bois articles"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Find all articles
    article_files = list(VOLUMES_DIR.rglob("*.qmd"))

    # Filter to non-Du Bois articles
    non_dubois_articles = []
    for file_path in article_files:
        parsed = parse_qmd_file(file_path)
        if parsed and not is_dubois(parsed['author']):
            # Check if description mentions Du Bois incorrectly
            if parsed['description'] and 'du bois' in parsed['description'].lower():
                non_dubois_articles.append((file_path, parsed))

    print(f"Found {len(non_dubois_articles)} non-Du Bois articles with incorrect descriptions")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 80)

    if not non_dubois_articles:
        print("✅ No articles need fixing!")
        return

    for file_path, parsed in non_dubois_articles:
        print(f"\n📄 {file_path}")
        print(f"  Author: {parsed['author']}")
        print(f"  Old: {parsed['description'][:80]}...")

        # Generate new description
        content_preview = extract_preview(parsed['content'])
        new_description = generate_description(
            parsed['title'],
            parsed['author'],
            parsed['date'],
            content_preview,
            client
        )

        if new_description:
            print(f"  New: {new_description}")

            if not args.dry_run:
                # Update file
                new_frontmatter = update_description(
                    parsed['frontmatter_text'],
                    new_description
                )
                new_content = f"---\n{new_frontmatter}\n---\n\n{parsed['content']}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print("  ✅ Updated")
            else:
                print("  (DRY RUN - would update)")
        else:
            print("  ❌ Failed to generate description")

    print("\n" + "=" * 80)
    print(f"Processed {len(non_dubois_articles)} articles")

    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. Run without --dry-run to update files.")

if __name__ == "__main__":
    main()
