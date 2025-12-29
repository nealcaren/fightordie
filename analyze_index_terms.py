#!/usr/bin/env python3
"""
Analyze index terms across all articles to identify most common
subjects, people, places, organizations, and events.
"""

import yaml
import re
from pathlib import Path
from collections import Counter

VOLUMES_DIR = Path("Volumes")

def parse_frontmatter(file_path):
    """Extract YAML frontmatter from .qmd file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except:
        return None

def analyze_index_terms():
    """Analyze all index terms across the corpus."""
    subjects = Counter()
    people = Counter()
    places = Counter()
    organizations = Counter()
    events = Counter()

    article_files = list(VOLUMES_DIR.rglob("*.qmd"))

    for file_path in article_files:
        fm = parse_frontmatter(file_path)
        if not fm:
            continue

        # Count terms from each field
        if 'subjects' in fm and fm['subjects']:
            for subject in fm['subjects']:
                if subject and isinstance(subject, str):
                    subjects[subject] += 1

        if 'people' in fm and fm['people']:
            for person in fm['people']:
                if person and isinstance(person, str):
                    people[person] += 1

        if 'places' in fm and fm['places']:
            for place in fm['places']:
                if place and isinstance(place, str):
                    places[place] += 1

        if 'organizations' in fm and fm['organizations']:
            for org in fm['organizations']:
                if org and isinstance(org, str):
                    organizations[org] += 1

        if 'events' in fm and fm['events']:
            for event in fm['events']:
                if event and isinstance(event, str):
                    events[event] += 1

    return {
        'subjects': subjects,
        'people': people,
        'places': places,
        'organizations': organizations,
        'events': events
    }

def print_top_terms(counter, label, n=30):
    """Print top N terms from a counter."""
    print(f"\n{'='*80}")
    print(f"TOP {n} {label.upper()}")
    print(f"{'='*80}")
    for term, count in counter.most_common(n):
        print(f"{count:4d}  {term}")

def main():
    print("Analyzing index terms across all articles...")
    print(f"Scanning {len(list(VOLUMES_DIR.rglob('*.qmd')))} files")

    results = analyze_index_terms()

    print_top_terms(results['subjects'], 'Subjects', 30)
    print_top_terms(results['people'], 'People', 30)
    print_top_terms(results['places'], 'Places', 30)
    print_top_terms(results['organizations'], 'Organizations', 20)
    print_top_terms(results['events'], 'Events', 20)

    # Summary stats
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Unique subjects: {len(results['subjects'])}")
    print(f"Unique people: {len(results['people'])}")
    print(f"Unique places: {len(results['places'])}")
    print(f"Unique organizations: {len(results['organizations'])}")
    print(f"Unique events: {len(results['events'])}")

if __name__ == "__main__":
    main()
