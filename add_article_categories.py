#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.0.0",
# ]
# ///
"""
Script to automatically add categories to article .qmd files
using an LLM (GPT-5-mini via OpenAI API).

Usage:
    uv run add_article_categories.py --dry-run  # Preview changes
    uv run add_article_categories.py            # Actually update files
"""

import os
import re
import argparse
from pathlib import Path
from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
VOLUMES_DIR = Path("Volumes")
MAX_CONTENT_LENGTH = 2000  # Characters to send to LLM

# Controlled category vocabulary
CATEGORIES = [
    "Lynching & Racial Violence",
    "Voting Rights & Disenfranchisement",
    "Segregation & Jim Crow",
    "Education & Schools",
    "Labor & Economics",
    "Migration",
    "World War I",
    "World War II",
    "Politics & Elections",
    "Pan-Africanism & International",
    "Arts & Culture",
    "Social Equality",
    "Law & Justice",
    "NAACP Activities",
    "Religion & Church",
    "Women's Rights & Suffrage",
    "Haiti & Caribbean",
    "Africa",
    "Health & Housing",
    "Youth & Children",
    "Biography & Obituary",
    "The Crisis (magazine)",
]

def parse_qmd_file(file_path):
    """
    Parse a .qmd file and extract frontmatter and content.

    Returns:
        dict or None: Dictionary with parsed data, or None if parsing fails
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract YAML frontmatter (handle optional leading whitespace)
    match = re.match(r'^\s*---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    content = match.group(2).strip()

    # Check if categories already exist and are non-empty
    categories_match = re.search(r'^categories:\s*\n((?:  - .+\n)+)', frontmatter_text, re.MULTILINE)
    has_categories = False
    if categories_match:
        # Check if any category is not empty string
        category_lines = categories_match.group(1)
        has_real_categories = bool(re.search(r'  - (?!""$).+', category_lines))
        has_categories = has_real_categories

    # Extract title from frontmatter
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?$", frontmatter_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Extract date
    date_match = re.search(r"^date:\s*(.+)$", frontmatter_text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "Unknown"

    # Extract description if exists
    desc_match = re.search(r'^description:\s*["\'](.+?)["\']$', frontmatter_text, re.MULTILINE)
    description = desc_match.group(1) if desc_match else ""

    return {
        'title': title,
        'date': date,
        'description': description,
        'has_categories': has_categories,
        'frontmatter_text': frontmatter_text,
        'content': content
    }

def extract_article_preview(content, max_length=MAX_CONTENT_LENGTH):
    """
    Extract the first few paragraphs of actual article content,
    excluding HTML comments and similar articles sections.
    """
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Stop at "Similar articles" or "Related Articles" sections
    similar_match = re.search(r'(<!-- Similar articles|#### Related Articles)', content)
    if similar_match:
        content = content[:similar_match.start()]

    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Get first N characters
    preview = content[:max_length].strip()

    return preview

def generate_categories(title, date, description, content_preview, client):
    """
    Use GPT-5-mini to generate 2-4 relevant categories.
    """
    categories_list = "\n".join(f"- {cat}" for cat in CATEGORIES)

    prompt = f"""You are categorizing articles from W.E.B. Du Bois's writings in The Crisis magazine (1910-1934).

Article Title: {title}
Publication Date: {date}
Description: {description}
Article Preview:
{content_preview}

Available Categories:
{categories_list}

Task: Select 2-4 categories that best describe this article's PRIMARY topics.

Guidelines:
1. Choose categories based on the article's main focus, not tangential mentions
2. Select 2-4 categories (usually 2-3 is ideal)
3. Use ONLY categories from the list above
4. Consider the historical context and Du Bois's typical themes
5. If multiple categories seem equally important, choose the most specific ones

Output: Return ONLY the category names, one per line, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=200
        )

        categories_text = response.choices[0].message.content.strip()

        # Parse the categories from the response
        categories = []
        for line in categories_text.split('\n'):
            line = line.strip().strip('-').strip('*').strip()
            # Try exact match first
            if line in CATEGORIES:
                categories.append(line)
            else:
                # Try fuzzy match - find closest category
                for cat in CATEGORIES:
                    if cat.lower() in line.lower() or line.lower() in cat.lower():
                        if cat not in categories:  # Avoid duplicates
                            categories.append(cat)
                        break

        # Validate we got 2-4 categories
        if not categories:
            print(f"  ⚠️  No valid categories found. Response was: {categories_text}")
            return None
        if len(categories) > 4:
            # Just take first 4
            categories = categories[:4]

        return categories

    except Exception as e:
        print(f"  ❌ Error generating categories: {e}")
        return None

def update_categories_in_frontmatter(frontmatter_text, categories):
    """
    Replace empty categories with new ones in YAML frontmatter.
    """
    # Find and replace the categories section
    # Match either empty categories or categories with just empty strings
    pattern = r'^categories:\s*\n(?:  - ""\s*\n)*'

    # Build new categories section
    new_categories = "categories:\n" + "\n".join(f"  - {cat}" for cat in categories) + "\n"

    # Try to replace
    new_frontmatter = re.sub(pattern, new_categories, frontmatter_text, flags=re.MULTILINE)

    # If no match (shouldn't happen based on our parsing), add it after date
    if new_frontmatter == frontmatter_text:
        lines = frontmatter_text.split('\n')
        new_lines = []
        inserted = False

        for line in lines:
            new_lines.append(line)
            # Insert after date
            if not inserted and re.match(r'^date:', line):
                new_lines.append("categories:")
                for cat in categories:
                    new_lines.append(f"  - {cat}")
                inserted = True

        new_frontmatter = '\n'.join(new_lines)

    return new_frontmatter

def update_qmd_file(file_path, frontmatter_text, content):
    """
    Write updated .qmd file with new frontmatter.
    """
    new_content = f"---\n{frontmatter_text}\n---\n\n{content}"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def process_single_article(file_path, client, dry_run, file_number, total_files, print_lock):
    """
    Process a single article file.
    Returns a dict with status and stats.
    """
    result = {
        'status': 'unknown',
        'file_path': file_path,
        'message': ''
    }

    with print_lock:
        print(f"\n[{file_number}/{total_files}] Processing: {file_path}")

    # Parse file
    parsed = parse_qmd_file(file_path)
    if not parsed:
        with print_lock:
            print("  ⚠️  Could not parse frontmatter, skipping")
        result['status'] = 'parse_error'
        return result

    # Skip if already has real categories
    if parsed['has_categories']:
        with print_lock:
            print("  ⏭️  Already has categories, skipping")
        result['status'] = 'has_categories'
        return result

    # Extract content preview
    content_preview = extract_article_preview(parsed['content'])

    if not content_preview:
        with print_lock:
            print("  ⚠️  No content found, skipping")
        result['status'] = 'parse_error'
        return result

    # Generate categories
    with print_lock:
        print(f"  📝 Generating categories for: {parsed['title']}")

    categories = generate_categories(
        parsed['title'],
        parsed['date'],
        parsed['description'],
        content_preview,
        client
    )

    if not categories:
        with print_lock:
            print("  ❌ Failed to generate categories")
        result['status'] = 'failed'
        return result

    with print_lock:
        print(f"  ✅ Generated: {', '.join(categories)}")

    # Update frontmatter
    if not dry_run:
        new_frontmatter = update_categories_in_frontmatter(
            parsed['frontmatter_text'],
            categories
        )
        update_qmd_file(file_path, new_frontmatter, parsed['content'])
        with print_lock:
            print("  💾 File updated")
    else:
        with print_lock:
            print("  (DRY RUN - would update file)")

    result['status'] = 'processed'
    return result


def process_articles(dry_run=True, limit=None, workers=5):
    """
    Process all articles in the Volumes directory.

    Args:
        dry_run: If True, don't actually update files
        limit: Maximum number of files to process
        workers: Number of parallel workers (default: 5)
    """
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Find all .qmd files in Volumes directory
    article_files = list(VOLUMES_DIR.rglob("*.qmd"))

    if limit:
        article_files = article_files[:limit]

    print(f"Found {len(article_files)} article files")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (files will be updated)'}")
    print(f"Model: gpt-5-mini")
    print(f"Workers: {workers} parallel threads")
    print("-" * 80)

    stats = {
        'total': len(article_files),
        'skipped_has_categories': 0,
        'skipped_parse_error': 0,
        'processed': 0,
        'failed': 0
    }

    print_lock = Lock()

    # Process articles in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_single_article,
                file_path,
                client,
                dry_run,
                i,
                len(article_files),
                print_lock
            ): file_path
            for i, file_path in enumerate(article_files, 1)
        }

        # Process completed tasks
        for future in as_completed(future_to_file):
            try:
                result = future.result()
                status = result['status']

                if status == 'processed':
                    stats['processed'] += 1
                elif status == 'has_categories':
                    stats['skipped_has_categories'] += 1
                elif status == 'parse_error':
                    stats['skipped_parse_error'] += 1
                elif status == 'failed':
                    stats['failed'] += 1

            except Exception as e:
                with print_lock:
                    print(f"  ❌ Unexpected error: {e}")
                stats['failed'] += 1

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files: {stats['total']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Skipped (already has categories): {stats['skipped_has_categories']}")
    print(f"Skipped (parse error): {stats['skipped_parse_error']}")
    print(f"Failed: {stats['failed']}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were changed.")
        print("Run without --dry-run to actually update files.")

def main():
    parser = argparse.ArgumentParser(
        description="Add categories to article .qmd files using GPT-5-mini"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to process (for testing)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of parallel workers (default: 5). Increase for faster processing.'
    )

    args = parser.parse_args()

    process_articles(dry_run=args.dry_run, limit=args.limit, workers=args.workers)

if __name__ == "__main__":
    main()
