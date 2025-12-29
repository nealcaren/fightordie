#!/usr/bin/env python3
"""
Generate browse pages for major index terms.
Creates .qmd files that use Quarto listings to filter by index fields.
"""

import yaml
import re
from pathlib import Path
from collections import Counter

VOLUMES_DIR = Path("Volumes")
BROWSE_DIR = Path("browse")
BROWSE_DIR.mkdir(exist_ok=True)

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

def collect_terms():
    """Collect all index terms with counts."""
    subjects = Counter()
    people = Counter()
    places = Counter()

    article_files = list(VOLUMES_DIR.rglob("*.qmd"))

    for file_path in article_files:
        fm = parse_frontmatter(file_path)
        if not fm:
            continue

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

    return subjects, people, places

def create_subject_page(subject, count):
    """Create a browse page for a subject."""
    # Create URL-friendly filename
    filename = re.sub(r'[^\w\s-]', '', subject.lower())
    filename = re.sub(r'[-\s]+', '_', filename)
    file_path = BROWSE_DIR / "subjects" / f"{filename}.qmd"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create description based on subject
    descriptions = {
        "Lynching": "W.E.B. Du Bois documented lynching with relentless detail, exposing it as a tool of racial terror rather than a response to crime.",
        "Educational inequality": "Du Bois championed liberal arts education and documented systematic inequality in Southern schools.",
        "Voting rights": "Articles documenting disfranchisement, poll taxes, grandfather clauses, and the fight for Black political power.",
        "Pan-Africanism": "Du Bois's vision of global Black solidarity, including coverage of Pan-African Congresses and anti-colonial movements.",
        "Women's suffrage": "Du Bois was an early supporter of women's suffrage, connecting it to Black liberation.",
        "Jim Crow laws": "Documentation of segregation laws, their enforcement, and their devastating impact on Black communities.",
    }

    description = descriptions.get(subject, f"Articles on {subject} from The Crisis (1910-1934)")

    content = f'''---
title: "{subject}"
description: "{description}"
listing:
  contents: "../../Volumes/**/*.qmd"
  type: table
  sort: "date"
  date-format: "YYYY (MMM)"
  page-size: 50
  fields: [date, title, description]
  filter-ui: true
  include:
    subjects: "{subject}"
---

## {subject} ({count} articles)

{description}

Use the search box below to find specific articles on this topic.
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path

def create_person_page(person, count):
    """Create a browse page for a person."""
    filename = re.sub(r'[^\w\s-]', '', person.lower())
    filename = re.sub(r'[-\s]+', '_', filename)
    file_path = BROWSE_DIR / "people" / f"{filename}.qmd"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    content = f'''---
title: "{person}"
description: "Articles discussing {person} from The Crisis (1910-1934)"
listing:
  contents: "../../Volumes/**/*.qmd"
  type: table
  sort: "date"
  date-format: "YYYY (MMM)"
  page-size: 50
  fields: [date, title, description]
  filter-ui: true
  include:
    people: "{person}"
---

## {person} ({count} articles)

Articles from *The Crisis* that substantially discuss {person}.

Use the search box below to find specific articles.
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path

def create_place_page(place, count):
    """Create a browse page for a place."""
    filename = re.sub(r'[^\w\s-]', '', place.lower())
    filename = re.sub(r'[-\s]+', '_', filename)
    file_path = BROWSE_DIR / "places" / f"{filename}.qmd"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    content = f'''---
title: "{place}"
description: "Articles about {place} from The Crisis (1910-1934)"
listing:
  contents: "../../Volumes/**/*.qmd"
  type: table
  sort: "date"
  date-format: "YYYY (MMM)"
  page-size: 50
  fields: [date, title, description]
  filter-ui: true
  include:
    places: "{place}"
---

## {place} ({count} articles)

Articles from *The Crisis* that focus on {place}.

Use the search box below to find specific articles.
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path

def main():
    print("Collecting index terms...")
    subjects, people, places = collect_terms()

    # Generate pages for top subjects (those with 5+ articles)
    print("\nGenerating subject browse pages...")
    subject_pages = 0
    for subject, count in subjects.most_common():
        if count >= 5:
            create_subject_page(subject, count)
            subject_pages += 1
            print(f"  ✅ {subject} ({count})")

    # Generate pages for top people (those with 5+ articles)
    print("\nGenerating people browse pages...")
    people_pages = 0
    for person, count in people.most_common():
        if count >= 5 and 'Du Bois' not in person:  # Skip DuBois (author of all)
            create_person_page(person, count)
            people_pages += 1
            print(f"  ✅ {person} ({count})")

    # Generate pages for top places (those with 10+ articles)
    print("\nGenerating place browse pages...")
    place_pages = 0
    for place, count in places.most_common():
        if count >= 10:
            create_place_page(place, count)
            place_pages += 1
            print(f"  ✅ {place} ({count})")

    print(f"\n{'='*80}")
    print(f"Generated {subject_pages} subject pages")
    print(f"Generated {people_pages} people pages")
    print(f"Generated {place_pages} place pages")

if __name__ == "__main__":
    main()
