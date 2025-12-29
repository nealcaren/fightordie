#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "openai>=1.0.0",
# ]
# ///
"""
Script to automatically add structured index terms to article .qmd files
using Library Science principles (subjects, people, places, organizations, events).

Usage:
    uv run add_article_index.py --dry-run  # Preview changes
    uv run add_article_index.py            # Actually update files
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
MAX_CONTENT_LENGTH = 3000  # Characters to send to LLM

def parse_qmd_file(file_path):
    """
    Parse a .qmd file and extract frontmatter and content.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^\s*---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    content = match.group(2).strip()

    # Check if already has index fields (check for subjects field specifically)
    has_index = bool(re.search(r'^subjects:', frontmatter_text, re.MULTILINE))

    # Extract title
    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?$", frontmatter_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Extract date
    date_match = re.search(r"^date:\s*(.+)$", frontmatter_text, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "Unknown"

    # Extract description
    desc_match = re.search(r'^description:\s*["\'](.+?)["\']$', frontmatter_text, re.MULTILINE)
    description = desc_match.group(1) if desc_match else ""

    return {
        'title': title,
        'date': date,
        'description': description,
        'has_index': has_index,
        'frontmatter_text': frontmatter_text,
        'content': content
    }

def extract_article_preview(content, max_length=MAX_CONTENT_LENGTH):
    """
    Extract the first few paragraphs of actual article content.
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

def generate_index_terms(title, date, description, content_preview, client):
    """
    Use GPT-5-mini to generate structured index terms.
    Returns dict with: subjects, people, places, organizations, events
    """

    prompt = f"""You are indexing an article from W.E.B. Du Bois's writings in The Crisis magazine (1910-1934) using Library Science principles.

Article Title: {title}
Publication Date: {date}
Description: {description}

Article Preview:
{content_preview}

Create a structured index with 5 fields:

**SUBJECTS** (3-6 thematic topics)
What the article is ABOUT. Use specific subject headings like:
- Lynching, Voting rights, Educational inequality, Residential segregation
- Anti-lynching legislation, Military discrimination, Labor organizing
- Pan-Africanism, Colonialism, Women's suffrage, Jim Crow laws

**PEOPLE** (2-8 proper names)
Individuals substantially discussed or mentioned:
- Political figures (Woodrow Wilson, Theodore Roosevelt, Warren G. Harding)
- Black leaders (Booker T. Washington, Marcus Garvey, James Weldon Johnson)
- NAACP leaders (Joel Spingarn, Mary White Ovington)
- Victims (if named), authors, intellectuals
Only include if SIGNIFICANTLY discussed, not passing mentions.

**PLACES** (1-5 locations)
Geographic locations central to the article:
- U.S. cities (Chicago, East St. Louis, Washington D.C., Atlanta)
- U.S. states (Mississippi, Georgia, South Carolina)
- Countries/regions (Haiti, Liberia, Africa, Europe)
- Use standard names. Include both city and state if needed for clarity.

**ORGANIZATIONS** (1-4 institutions)
Groups, parties, institutions substantially discussed:
- NAACP, Republican Party, Democratic Party, U.S. Congress
- Howard University, Tuskegee Institute, American Federation of Labor
- The Crisis magazine, League of Nations
Only include if central to article, not brief mentions.

**EVENTS** (0-3 specific incidents)
Named historical events, riots, elections, conferences:
- East St. Louis Race Riot (1917), Red Summer (1919), World War I
- Presidential Election (1920), Pan-African Congress (1919)
- Houston Mutiny (1917), Dyer Anti-Lynching Bill Campaign (1921-1922)
Include year in parentheses. Only specific events, not general topics.

CRITICAL RULES:
1. Be SPECIFIC and PRECISE - prefer concrete terms
2. Only index what is SUBSTANTIALLY discussed, not passing mentions
3. Use standard, consistent forms (full names, standard place names)
4. Subjects should be searchable thematic headings, not just keywords
5. Total of 8-15 index terms across all fields
6. Events field can be empty if no specific event is central

OUTPUT FORMAT:
Return EXACTLY this format (use "None" for empty fields):

SUBJECTS:
- [subject 1]
- [subject 2]
...

PEOPLE:
- [person 1]
- [person 2]
...

PLACES:
- [place 1]
...

ORGANIZATIONS:
- [org 1]
...

EVENTS:
- [event 1]
OR
EVENTS:
None"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=3000
        )

        response_text = response.choices[0].message.content
        if response_text:
            response_text = response_text.strip()
        else:
            print(f"  ⚠️  Empty response from API")
            print(f"  Response object: {response}")
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

            # Check for field headers
            if line.upper().startswith('SUBJECTS:'):
                current_field = 'subjects'
                continue
            elif line.upper().startswith('PEOPLE:'):
                current_field = 'people'
                continue
            elif line.upper().startswith('PLACES:'):
                current_field = 'places'
                continue
            elif line.upper().startswith('ORGANIZATIONS:'):
                current_field = 'organizations'
                continue
            elif line.upper().startswith('EVENTS:'):
                current_field = 'events'
                continue

            # Parse items (lines starting with -)
            if line.startswith('-') and current_field:
                item = line.lstrip('-').strip()
                if item and item.lower() != 'none':
                    index_terms[current_field].append(item)
            # Handle "None" on its own line
            elif line.lower() == 'none':
                continue

        # Validate we got something useful
        total_terms = sum(len(v) for v in index_terms.values())
        if total_terms < 5:
            print(f"  ⚠️  Too few index terms ({total_terms}). Response was:")
            print(f"     {response_text[:200]}...")
            return None

        # Validate field counts
        if len(index_terms['subjects']) < 2 or len(index_terms['subjects']) > 8:
            print(f"  ⚠️  Invalid subject count: {len(index_terms['subjects'])}")

        return index_terms

    except Exception as e:
        print(f"  ❌ Error generating index: {e}")
        return None

def update_index_in_frontmatter(frontmatter_text, index_terms):
    """
    Add index fields to YAML frontmatter after categories.
    """
    # Build index section
    index_section = ""

    if index_terms['subjects']:
        index_section += "subjects:\n"
        for subject in index_terms['subjects']:
            index_section += f"  - {subject}\n"

    if index_terms['people']:
        index_section += "people:\n"
        for person in index_terms['people']:
            index_section += f"  - {person}\n"

    if index_terms['places']:
        index_section += "places:\n"
        for place in index_terms['places']:
            index_section += f"  - {place}\n"

    if index_terms['organizations']:
        index_section += "organizations:\n"
        for org in index_terms['organizations']:
            index_section += f"  - {org}\n"

    if index_terms['events']:
        index_section += "events:\n"
        for event in index_terms['events']:
            index_section += f"  - {event}\n"

    # Find where to insert (after categories or after date if no categories)
    lines = frontmatter_text.split('\n')
    new_lines = []
    inserted = False

    # Try to find categories section to insert after
    in_categories = False
    for i, line in enumerate(lines):
        new_lines.append(line)

        if line.startswith('categories:'):
            in_categories = True
        elif in_categories and not line.startswith('  -') and not line.strip() == '':
            # End of categories section, insert here
            if not inserted:
                new_lines.insert(-1, index_section.rstrip())
                inserted = True
            in_categories = False
        elif line.startswith('citation:') and not inserted:
            # Insert before citation if we haven't inserted yet
            new_lines.insert(-1, index_section.rstrip())
            inserted = True

    # If still not inserted, add at end
    if not inserted:
        new_lines.append(index_section.rstrip())

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
    """
    result = {
        'status': 'unknown',
        'file_path': file_path,
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

    # Skip if already has index
    if parsed['has_index']:
        with print_lock:
            print("  ⏭️  Already has index, skipping")
        result['status'] = 'has_index'
        return result

    # Extract content preview
    content_preview = extract_article_preview(parsed['content'])

    if not content_preview:
        with print_lock:
            print("  ⚠️  No content found, skipping")
        result['status'] = 'parse_error'
        return result

    # Generate index
    with print_lock:
        print(f"  📝 Generating index for: {parsed['title']}")

    index_terms = generate_index_terms(
        parsed['title'],
        parsed['date'],
        parsed['description'],
        content_preview,
        client
    )

    if not index_terms:
        with print_lock:
            print("  ❌ Failed to generate index")
        result['status'] = 'failed'
        return result

    # Print summary
    with print_lock:
        summary = []
        if index_terms['subjects']:
            summary.append(f"Subjects: {', '.join(index_terms['subjects'][:3])}")
        if index_terms['people']:
            summary.append(f"People: {', '.join(index_terms['people'][:3])}")
        if index_terms['places']:
            summary.append(f"Places: {', '.join(index_terms['places'][:2])}")
        print(f"  ✅ {' | '.join(summary)}")

    # Update frontmatter
    if not dry_run:
        new_frontmatter = update_index_in_frontmatter(
            parsed['frontmatter_text'],
            index_terms
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
        'skipped_has_index': 0,
        'skipped_parse_error': 0,
        'processed': 0,
        'failed': 0
    }

    print_lock = Lock()

    # Process articles in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
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

        for future in as_completed(future_to_file):
            try:
                result = future.result()
                status = result['status']

                if status == 'processed':
                    stats['processed'] += 1
                elif status == 'has_index':
                    stats['skipped_has_index'] += 1
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
    print(f"Skipped (already has index): {stats['skipped_has_index']}")
    print(f"Skipped (parse error): {stats['skipped_parse_error']}")
    print(f"Failed: {stats['failed']}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were changed.")
        print("Run without --dry-run to actually update files.")

def main():
    parser = argparse.ArgumentParser(
        description="Add structured index terms to article .qmd files using GPT-5-mini"
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
        help='Number of parallel workers (default: 5)'
    )

    args = parser.parse_args()

    process_articles(dry_run=args.dry_run, limit=args.limit, workers=args.workers)

if __name__ == "__main__":
    main()
