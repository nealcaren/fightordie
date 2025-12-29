#!/usr/bin/env python3
"""
Create index pages for browse/subjects/, browse/people/, and browse/places/
that list all available browse pages.
"""

import yaml
import re
from pathlib import Path
from collections import Counter

VOLUMES_DIR = Path("Volumes")
BROWSE_DIR = Path("browse")

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

def create_subjects_index(subjects):
    """Create browse/subjects/index.qmd"""
    file_path = BROWSE_DIR / "subjects" / "index.qmd"

    # Build list of subjects with 5+ articles
    subject_list = []
    for subject, count in subjects.most_common():
        if count >= 5:
            filename = re.sub(r'[^\w\s-]', '', subject.lower())
            filename = re.sub(r'[-\s]+', '_', filename)
            subject_list.append(f"- [{subject}]({filename}.html) ({count} articles)")

    content = f'''---
title: "Browse by Subject"
description: "Explore W.E.B. Du Bois's writings organized by major themes and topics"
---

## All Subject Browse Pages

Browse articles by major themes in Du Bois's writings from *The Crisis* (1910-1934).

{chr(10).join(subject_list)}

---

**Note:** Only subjects with 5 or more articles are listed. The archive contains 2,750+ unique subjects total.

[← Back to Browse Index](../index.html)
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created {file_path}")

def create_people_index(people):
    """Create browse/people/index.qmd"""
    file_path = BROWSE_DIR / "people" / "index.qmd"

    # Build list of people with 5+ articles (excluding Du Bois)
    people_list = []
    for person, count in people.most_common():
        if count >= 5 and 'Du Bois' not in person:
            filename = re.sub(r'[^\w\s-]', '', person.lower())
            filename = re.sub(r'[-\s]+', '_', filename)
            people_list.append(f"- [{person}]({filename}.html) ({count} articles)")

    content = f'''---
title: "Browse by People"
description: "Explore articles discussing specific historical figures and leaders"
---

## All People Browse Pages

Browse articles by the people substantially discussed in *The Crisis* (1910-1934).

{chr(10).join(people_list)}

---

**Note:** Only people discussed in 5 or more articles are listed. The archive mentions 620+ unique people total. W.E.B. Du Bois is excluded as the author of most articles.

[← Back to Browse Index](../index.html)
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created {file_path}")

def create_places_index(places):
    """Create browse/places/index.qmd"""
    file_path = BROWSE_DIR / "places" / "index.qmd"

    # Build list of places with 10+ articles
    places_list = []
    for place, count in places.most_common():
        if count >= 10:
            filename = re.sub(r'[^\w\s-]', '', place.lower())
            filename = re.sub(r'[-\s]+', '_', filename)
            places_list.append(f"- [{place}]({filename}.html) ({count} articles)")

    content = f'''---
title: "Browse by Place"
description: "Explore articles by geographic location and region"
---

## All Place Browse Pages

Browse articles by the geographic locations that are central to Du Bois's writings in *The Crisis* (1910-1934).

{chr(10).join(places_list)}

---

**Note:** Only places mentioned in 10 or more articles are listed. The archive references 493+ unique places total.

[← Back to Browse Index](../index.html)
'''

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Created {file_path}")

def main():
    print("Collecting index terms...")
    subjects, people, places = collect_terms()

    print("\nCreating index pages...")
    create_subjects_index(subjects)
    create_people_index(people)
    create_places_index(places)

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
