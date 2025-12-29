#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Find semantic duplicate subject terms."""

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
        return yaml.safe_load(match.group(1))
    except:
        return None

def normalize_term(term):
    """Normalize a term for comparison."""
    # Remove parenthetical notes
    term = re.sub(r'\s*\([^)]*\)', '', term)
    # Remove em-dashes and special chars
    term = term.replace('—', ' ').replace('‑', ' ')
    # Normalize spacing
    term = ' '.join(term.split())
    return term.lower().strip()

def main():
    volumes_dir = Path('Volumes')
    article_files = list(volumes_dir.glob('**/*.qmd'))

    # Collect all subject terms
    subject_counts = defaultdict(int)
    for file_path in article_files:
        parsed = parse_qmd_file(file_path)
        if not parsed:
            continue
        subjects = parsed.get('subjects', [])
        if subjects:
            for subject in subjects:
                if isinstance(subject, str):
                    subject_counts[subject] += 1

    # Group by key concepts
    concept_groups = defaultdict(list)
    
    # Define key concepts to look for
    concepts = {
        'lynching': ['lynch', 'mob violence'],
        'voting': ['voting', 'suffrage', 'disfranchise', 'franchise', 'ballot'],
        'jim crow': ['jim crow', 'segregat'],
        'education': ['educat', 'school', 'college', 'university'],
        'military': ['military', 'soldier', 'armed forces', 'world war', 'army'],
        'pan-african': ['pan-african', 'pan african', 'panafrican'],
        'colonialism': ['colonial', 'imperial'],
        'labor': ['labor', 'labour', 'worker', 'employment', 'union'],
        'race riot': ['race riot', 'racial riot'],
        'discrimination': ['discriminat'],
        'white supremacy': ['white supremacy', 'racial hierarchy'],
        'housing': ['housing', 'residential segregation'],
        'migration': ['migration', 'great migration'],
    }

    for concept_name, keywords in concepts.items():
        for subject, count in subject_counts.items():
            subject_lower = subject.lower()
            if any(kw in subject_lower for kw in keywords):
                concept_groups[concept_name].append((subject, count))

    # Print grouped results
    print("CONCEPTUAL DUPLICATES")
    print("="*80)
    
    for concept, subjects in sorted(concept_groups.items()):
        if len(subjects) > 1:
            # Sort by count descending
            subjects.sort(key=lambda x: (-x[1], x[0]))
            total = sum(count for _, count in subjects)
            print(f"\n{concept.upper()} ({len(subjects)} variations, {total} total uses):")
            for subject, count in subjects:
                normalized = normalize_term(subject)
                print(f"  {count:3d}  {subject}")
                if normalized != subject.lower():
                    print(f"       → normalized: {normalized}")

if __name__ == '__main__':
    main()
