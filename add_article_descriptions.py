#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.0.0",
# ]
# ///
"""
Script to automatically add SEO descriptions to article .qmd files
using an LLM (GPT-5-mini via OpenAI API).

Usage:
    uv run add_article_descriptions.py --dry-run  # Preview changes
    uv run add_article_descriptions.py            # Actually update files
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
MAX_CONTENT_LENGTH = 25000  # Characters to send to LLM

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

    # Check if description already exists
    has_description = bool(re.search(r'^description:', frontmatter_text, re.MULTILINE))

    # Extract title from frontmatter
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?$", frontmatter_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Extract date
    date_match = re.search(r"^date:\s*(.+)$", frontmatter_text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "Unknown"

    return {
        'title': title,
        'date': date,
        'has_description': has_description,
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

def generate_description(title, date, content_preview, client):
    """
    Use GPT-5-mini to generate a concise SEO description.
    """
    prompt = f"""You are helping create SEO meta descriptions for a digital archive of W.E.B. Du Bois's writings from The Crisis magazine.

Examples
In a 1912 Crisis article, W.E.B. Du Bois argues that China’s revolution proves shared humanity and exposes white supremacy behind Western racial myths.

In a 1912 Crisis essay, W.E.B. Du Bois documents how lynching and vagrancy laws criminalize Black life and generate the very crimes they claim to stop.


Article Title: {title}
Publication Date: {date}
Article Preview:
{content_preview}

Task**Task**
Generate a compelling meta description (120–160 characters) that:

1. Clearly summarizes the article’s main argument or topic.
2. Identifies the author as W.E.B. Du Bois and the publication as *The Crisis*.
3. Includes the publication year when it can be inferred from the date.
4. Uses active voice and clear, accessible language.
5. Prioritize historically meaningful terms when relevant (e.g., race, democracy, education, labor).
6. Vary rhetorical structure across entries (e.g., causal analysis, moral critique, reversal of conventional wisdom, documentation of harm). Avoid repeating the same verb or sentence pattern.

**Output rules**
Return ONLY the description text. Do not use quotes or additional formatting.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=10000
        )

        description = response.choices[0].message.content.strip()
        # Remove quotes if LLM added them
        description = description.strip('"\'')

        return description

    except Exception as e:
        print(f"  ❌ Error generating description: {e}")
        return None

def add_description_to_frontmatter(frontmatter_text, description):
    """
    Add description field to YAML frontmatter after the title.
    """
    # Escape quotes in description for YAML
    # Replace " with \" to escape quotes inside the YAML string
    escaped_description = description.replace('"', '\\"')

    # Find where to insert (after title line)
    lines = frontmatter_text.split('\n')
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        # Insert after title
        if not inserted and re.match(r'^title:', line):
            new_lines.append(f'description: "{escaped_description}"')
            inserted = True

    return '\n'.join(new_lines)

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

    # Skip if already has description
    if parsed['has_description']:
        with print_lock:
            print("  ⏭️  Already has description, skipping")
        result['status'] = 'has_description'
        return result

    # Extract content preview
    content_preview = extract_article_preview(parsed['content'])

    if not content_preview:
        with print_lock:
            print("  ⚠️  No content found, skipping")
        result['status'] = 'parse_error'
        return result

    # Generate description
    with print_lock:
        print(f"  📝 Generating description for: {parsed['title']}")

    description = generate_description(
        parsed['title'],
        parsed['date'],
        content_preview,
        client
    )

    if not description:
        with print_lock:
            print("  ❌ Failed to generate description")
        result['status'] = 'failed'
        return result

    with print_lock:
        print(f"  ✅ Generated: {description}")

    # Update frontmatter
    if not dry_run:
        new_frontmatter = add_description_to_frontmatter(
            parsed['frontmatter_text'],
            description
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
    print(f"Model: gpt-5-nano")
    print(f"Workers: {workers} parallel threads")
    print("-" * 80)

    stats = {
        'total': len(article_files),
        'skipped_has_description': 0,
        'skipped_parse_error': 0,
        'processed': 0,
        'failed': 0
    }

    print_lock = Lock()
    completed = 0

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
            completed += 1
            try:
                result = future.result()
                status = result['status']

                if status == 'processed':
                    stats['processed'] += 1
                elif status == 'has_description':
                    stats['skipped_has_description'] += 1
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
    print(f"Skipped (already has description): {stats['skipped_has_description']}")
    print(f"Skipped (parse error): {stats['skipped_parse_error']}")
    print(f"Failed: {stats['failed']}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were changed.")
        print("Run without --dry-run to actually update files.")

def main():
    parser = argparse.ArgumentParser(
        description="Add SEO descriptions to article .qmd files using GPT-5-mini"
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
