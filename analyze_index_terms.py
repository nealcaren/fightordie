#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Analyze subject terms across all articles to find duplicates and variations."""

import yaml
import re
from pathlib import Path
from collections import defaultdict

def parse_qmd_file(file_path):
    """Parse a .qmd file and extract frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    match = re.match(r'^\s*---\n(.*?)\n---\n', text, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        return frontmatter
    except:
        return None

def main():
    # Find all .qmd files
    volumes_dir = Path('Volumes')
    article_files = list(volumes_dir.glob('**/*.qmd'))

    # Collect all subject terms
    all_subjects = []
    subject_to_files = defaultdict(list)

    for file_path in article_files:
        parsed = parse_qmd_file(file_path)
        if not parsed:
            continue

        subjects = parsed.get('subjects', [])
        if subjects:
            for subject in subjects:
                # Skip non-string subjects (structured data)
                if not isinstance(subject, str):
                    continue
                all_subjects.append(subject)
                subject_to_files[subject].append(str(file_path))

    # Get unique subjects and their counts
    subject_counts = defaultdict(int)
    for subject in all_subjects:
        subject_counts[subject] += 1

    print(f"Total subject terms: {len(all_subjects)}")
    print(f"Unique subject terms: {len(subject_counts)}")
    print("\n" + "="*80)
    print("ALL UNIQUE SUBJECT TERMS (sorted by frequency)")
    print("="*80 + "\n")

    # Sort by count descending
    for subject, count in sorted(subject_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{count:3d}  {subject}")

    print("\n" + "="*80)
    print("POTENTIAL DUPLICATES (similar terms)")
    print("="*80 + "\n")

    # Group by similarity
    subjects_lower = {}
    for subject in subject_counts.keys():
        lower = subject.lower()
        if lower not in subjects_lower:
            subjects_lower[lower] = []
        subjects_lower[lower].append(subject)

    # Find groups with multiple variations
    duplicates_found = False
    for lower, variations in sorted(subjects_lower.items()):
        if len(variations) > 1:
            duplicates_found = True
            print(f"\nVariations of '{lower}':")
            for v in variations:
                print(f"  - {v} ({subject_counts[v]} articles)")
    
    if not duplicates_found:
        print("No exact case-insensitive duplicates found.")

    # Look for keyword overlaps
    print("\n" + "="*80)
    print("KEYWORD OVERLAP ANALYSIS")
    print("="*80 + "\n")

    keywords = defaultdict(list)
    for subject in subject_counts.keys():
        # Split on common separators
        words = re.split(r'[;,\-\(\):]|\s+and\s+|\s+or\s+|\s+', subject.lower())
        words = [w.strip() for w in words if w.strip() and len(w.strip()) > 3]
        for word in words:
            keywords[word].append(subject)

    # Show keywords that appear in many different subjects
    print("Common keywords across multiple subjects:\n")
    for keyword, subjects in sorted(keywords.items(), key=lambda x: (-len(x[1]), x[0])):
        if len(subjects) >= 5:
            print(f"\n'{keyword}' appears in {len(subjects)} subjects:")
            for s in sorted(subjects)[:10]:  # Show first 10
                print(f"  - {s}")
            if len(subjects) > 10:
                print(f"  ... and {len(subjects) - 10} more")

if __name__ == '__main__':
    main()
