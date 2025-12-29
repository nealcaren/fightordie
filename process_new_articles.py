#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.0.0",
# ]
# ///
"""
Unified script to process new articles:
1. Add descriptions (if missing)
2. Add index terms (if missing)

Usage:
    python process_new_articles.py              # Process all articles
    python process_new_articles.py --dry-run    # Preview changes
    python process_new_articles.py --volume 12  # Process specific volume
    python process_new_articles.py --limit 5    # Process max 5 articles
"""

import os
import re
import argparse
from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

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

    # Check what's missing
    has_description = bool(re.search(r'^description:', frontmatter_text, re.MULTILINE))
    has_subjects = bool(re.search(r'^subjects:', frontmatter_text, re.MULTILINE))

    # Extract title and date
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?$", frontmatter_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    date_match = re.search(r"^date:\s*(.+)$", frontmatter_text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "Unknown"

    return {
        'title': title,
        'date': date,
        'has_description': has_description,
        'has_subjects': has_subjects,
        'frontmatter_text': frontmatter_text,
        'content': content
    }

def extract_preview(content, max_length=MAX_CONTENT_LENGTH):
    """Extract preview of article content."""
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    # Get first N characters
    return content[:max_length].strip()

def generate_description(title, date, content_preview, client):
    """Generate SEO description using GPT-5-mini."""
    prompt = f"""Write a one-sentence SEO meta description (150 chars max) for this article from The Crisis magazine.

Title: {title}
Date: {date}

Article preview:
{content_preview}

Requirements:
- ONE sentence only, under 150 characters
- Start with context (author/publication/date if relevant)
- Focus on main argument or topic
- Be specific and compelling
- No quotes around the description itself

Example format: "W.E.B. Du Bois argues in The Crisis (1920) that lynching provokes crime, calling for an end to racial violence."

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
            # Escape quotes for YAML
            description = description.replace('"', '\\"')
            return description
        return None
    except Exception as e:
        print(f"  ❌ Error generating description: {e}")
        return None

def generate_index_terms(title, date, content_preview, client):
    """Generate structured index terms using GPT-5-mini."""
    prompt = f"""You are indexing an article from W.E.B. Du Bois's writings in The Crisis magazine (1910-1934).

Article Title: {title}
Publication Date: {date}

Article Preview:
{content_preview}

Create a structured index with 5 fields:

**SUBJECTS** (3-6 thematic topics) - Specific subject headings like:
- Lynching, Voting rights, Educational inequality
- Anti-lynching legislation, Military discrimination
- Pan-Africanism, Colonialism, Women's suffrage

**PEOPLE** (2-8 proper names) - Individuals substantially discussed
**PLACES** (1-5 locations) - Geographic locations central to article
**ORGANIZATIONS** (1-4 institutions) - Groups, parties, institutions
**EVENTS** (0-3 specific incidents) - Named historical events with year

OUTPUT FORMAT (use "None" for empty fields):

SUBJECTS:
- [subject 1]
- [subject 2]

PEOPLE:
- [person 1]

PLACES:
- [place 1]

ORGANIZATIONS:
- [org 1]

EVENTS:
- [event 1]
OR
EVENTS:
None"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=3000
        )

        response_text = response.choices[0].message.content
        if not response_text:
            return None

        # Parse the structured response
        index_terms = {
            'subjects': [],
            'people': [],
            'places': [],
            'organizations': [],
            'events': []
        }

        current_field = None
        for line in response_text.split('\n'):
            line = line.strip()

            if line.upper().startswith('SUBJECTS:'):
                current_field = 'subjects'
            elif line.upper().startswith('PEOPLE:'):
                current_field = 'people'
            elif line.upper().startswith('PLACES:'):
                current_field = 'places'
            elif line.upper().startswith('ORGANIZATIONS:'):
                current_field = 'organizations'
            elif line.upper().startswith('EVENTS:'):
                current_field = 'events'
            elif line.startswith('-') and current_field:
                item = line.lstrip('-').strip()
                if item and item.lower() != 'none':
                    index_terms[current_field].append(item)

        total_terms = sum(len(v) for v in index_terms.values())
        if total_terms < 5:
            return None

        return index_terms

    except Exception as e:
        print(f"  ❌ Error generating index: {e}")
        return None

def update_frontmatter(frontmatter_text, description=None, index_terms=None):
    """Add description and/or index terms to frontmatter."""
    lines = frontmatter_text.split('\n')
    new_lines = []
    inserted_description = False
    inserted_index = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Insert description after date
        if description and not inserted_description and line.startswith('date:'):
            new_lines.append(f'description: "{description}"')
            inserted_description = True

        # Insert index fields after categories
        if index_terms and not inserted_index:
            if line.startswith('categories:'):
                # Look ahead to find end of categories
                j = i + 1
                while j < len(lines) and (lines[j].startswith('  -') or lines[j].strip() == ''):
                    new_lines.append(lines[j])
                    j += 1

                # Add index fields
                if index_terms['subjects']:
                    new_lines.append('subjects:')
                    for subject in index_terms['subjects']:
                        new_lines.append(f'  - {subject}')

                if index_terms['people']:
                    new_lines.append('people:')
                    for person in index_terms['people']:
                        new_lines.append(f'  - {person}')

                if index_terms['places']:
                    new_lines.append('places:')
                    for place in index_terms['places']:
                        new_lines.append(f'  - {place}')

                if index_terms['organizations']:
                    new_lines.append('organizations:')
                    for org in index_terms['organizations']:
                        new_lines.append(f'  - {org}')

                if index_terms['events']:
                    new_lines.append('events:')
                    for event in index_terms['events']:
                        new_lines.append(f'  - {event}')

                inserted_index = True
                # Skip the category list items we already added
                return '\n'.join(new_lines[:i+1] + new_lines[j:])

    return '\n'.join(new_lines)

def process_article(file_path, client, dry_run, print_lock):
    """Process a single article."""
    with print_lock:
        print(f"\n📄 {file_path}")

    parsed = parse_qmd_file(file_path)
    if not parsed:
        with print_lock:
            print("  ⚠️  Could not parse file")
        return {'status': 'parse_error'}

    needs_description = not parsed['has_description']
    needs_index = not parsed['has_subjects']

    if not needs_description and not needs_index:
        with print_lock:
            print("  ✅ Already complete")
        return {'status': 'complete'}

    content_preview = extract_preview(parsed['content'])
    if not content_preview:
        with print_lock:
            print("  ⚠️  No content found")
        return {'status': 'no_content'}

    # Generate what's needed
    description = None
    index_terms = None

    if needs_description:
        with print_lock:
            print("  📝 Generating description...")
        description = generate_description(
            parsed['title'],
            parsed['date'],
            content_preview,
            client
        )
        if description:
            with print_lock:
                print(f"  ✅ Description: {description[:80]}...")

    if needs_index:
        with print_lock:
            print("  📝 Generating index terms...")
        index_terms = generate_index_terms(
            parsed['title'],
            parsed['date'],
            content_preview,
            client
        )
        if index_terms:
            with print_lock:
                summary = []
                if index_terms['subjects']:
                    summary.append(f"Subjects: {', '.join(index_terms['subjects'][:2])}")
                if index_terms['people']:
                    summary.append(f"People: {', '.join(index_terms['people'][:2])}")
                print(f"  ✅ {' | '.join(summary)}")

    # Update file
    if (description or index_terms) and not dry_run:
        new_frontmatter = update_frontmatter(
            parsed['frontmatter_text'],
            description=description,
            index_terms=index_terms
        )
        new_content = f"---\n{new_frontmatter}\n---\n\n{parsed['content']}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        with print_lock:
            print("  💾 File updated")
    elif dry_run:
        with print_lock:
            print("  (DRY RUN - would update)")

    return {'status': 'processed'}

def main():
    parser = argparse.ArgumentParser(
        description="Process new articles: add descriptions and index terms"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--volume',
        type=int,
        help='Process only specific volume'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of files to process'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=5,
        help='Number of parallel workers (default: 5)'
    )

    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Find articles
    if args.volume:
        article_files = list(VOLUMES_DIR.glob(f"{args.volume}/**/*.qmd"))
    else:
        article_files = list(VOLUMES_DIR.rglob("*.qmd"))

    # Filter to articles missing description or index
    articles_to_process = []
    for file_path in article_files:
        parsed = parse_qmd_file(file_path)
        if parsed and (not parsed['has_description'] or not parsed['has_subjects']):
            articles_to_process.append(file_path)

    if args.limit:
        articles_to_process = articles_to_process[:args.limit]

    print(f"Found {len(articles_to_process)} articles to process")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Workers: {args.workers}")
    print("=" * 80)

    if not articles_to_process:
        print("✅ All articles already have descriptions and index terms!")
        return

    # Process articles
    print_lock = Lock()
    stats = {'processed': 0, 'complete': 0, 'failed': 0}

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_article, fp, client, args.dry_run, print_lock): fp
            for fp in articles_to_process
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                if result['status'] == 'processed':
                    stats['processed'] += 1
                elif result['status'] == 'complete':
                    stats['complete'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                stats['failed'] += 1

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Processed: {stats['processed']}")
    print(f"Already complete: {stats['complete']}")
    print(f"Failed: {stats['failed']}")

    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. Run without --dry-run to update files.")

if __name__ == "__main__":
    main()
