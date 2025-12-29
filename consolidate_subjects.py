#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Consolidate subject terms to broader, cleaner categories."""

import yaml
import re
from pathlib import Path
from collections import defaultdict

# Mapping from specific terms to broader preferred terms
CONSOLIDATION_MAP = {
    # LYNCHING - consolidate to 3 main terms
    'Lynching (United States)': 'Lynching',
    'Lynching (anti-lynching advocacy)': 'Lynching',
    'Lynching (racial mob violence)': 'Lynching',
    'Lynching — United States': 'Lynching',
    'Lynching and racial violence': 'Lynching and mob violence',
    'Racial violence and lynching': 'Lynching and mob violence',
    'Racial terror and mob violence': 'Lynching and mob violence',
    'Mob violence against African Americans': 'Lynching and mob violence',
    'Race riots and mob violence against African Americans': 'Lynching and mob violence',
    'Anti-lynching / mob violence': 'Anti-lynching legislation',
    'Anti-lynching activism': 'Anti-lynching legislation',
    'Anti-lynching advocacy': 'Anti-lynching legislation',
    'Anti-lynching campaigns': 'Anti-lynching legislation',
    'Anti-lynching campaigns and legislation': 'Anti-lynching legislation',
    'Federal anti-lynching legislation': 'Anti-lynching legislation',
    
    # VOTING RIGHTS - consolidate to main terms
    'Voting rights (African Americans)': 'Voting rights',
    'Voting rights — African Americans': 'Voting rights',
    'African American voting rights': 'Voting rights',
    'African American suffrage': 'Voting rights',
    'Disfranchisement (Voting rights)': 'Disfranchisement',
    'Disfranchisement (voting rights)': 'Disfranchisement',
    'Disfranchisement (voting rights suppression)': 'Disfranchisement',
    'Disfranchisement (African Americans)': 'Disfranchisement',
    'Disfranchisement of African Americans': 'Disfranchisement',
    'Disfranchisement of African Americans (voting rights)': 'Disfranchisement',
    'Disfranchisement and voting rights': 'Disfranchisement',
    'Disfranchisement and voting rights (African Americans)': 'Disfranchisement',
    'Disfranchisement and voting rights of African Americans': 'Disfranchisement',
    'Voting rights and disfranchisement': 'Disfranchisement',
    'Voting rights — disfranchisement': 'Disfranchisement',
    "Women's suffrage (United States)": "Women's suffrage",
    
    # JIM CROW & SEGREGATION
    'Jim Crow laws (racial segregation)': 'Jim Crow laws',
    'Jim Crow laws and racial segregation': 'Jim Crow laws',
    'Jim Crow segregation': 'Jim Crow laws',
    'Jim Crow laws and segregation': 'Jim Crow laws',
    'Segregation (Jim Crow laws)': 'Jim Crow laws',
    'Racial segregation (Jim Crow laws)': 'Racial segregation',
    'Residential segregation (housing discrimination)': 'Residential segregation',
    'Residential segregation and housing discrimination': 'Residential segregation',
    'Segregated schooling (Jim Crow education)': 'Educational segregation',
    'School segregation': 'Educational segregation',
    
    # EDUCATION - consolidate to main term
    'Educational inequality for African Americans': 'Educational inequality',
    'Educational inequality and access': 'Educational inequality',
    'Educational inequality (African Americans)': 'Educational inequality',
    'Educational inequality — African Americans': 'Educational inequality',
    'Educational opportunity (African Americans)': 'Educational inequality',
    'Educational equality (African Americans)': 'Educational inequality',
    'Higher education for African Americans': 'Higher education',
    'Higher education — African Americans': 'Higher education',
    
    # MILITARY DISCRIMINATION
    'Military discrimination against African Americans': 'Military discrimination',
    'Military discrimination against African American soldiers': 'Military discrimination',
    'Military discrimination against Black soldiers': 'Military discrimination',
    'Military discrimination against Black Americans': 'Military discrimination',
    'Military discrimination against Black servicemen': 'Military discrimination',
    
    # EMPLOYMENT DISCRIMINATION
    'Employment discrimination against African Americans': 'Employment discrimination',
    'Racial discrimination in employment': 'Employment discrimination',
    'Racial employment discrimination': 'Employment discrimination',
    
    # RACE RELATIONS
    'Race relations in the United States': 'Race relations',
    'Race relations — United States': 'Race relations',
    'Race relations (United States)': 'Race relations',
    'Race relations in the Southern United States': 'Race relations',
    'Race relations — Southern United States': 'Race relations',
    'Race relations—Southern United States': 'Race relations',
    
    # RACE RIOTS
    'Race riots (United States)': 'Race riots',
    'Racial violence and race riots': 'Race riots',
    
    # WHITE SUPREMACY
    'White supremacy and racial hierarchy': 'White supremacy',
    'White supremacy and racial ideology': 'White supremacy',
    
    # COLONIALISM
    'Colonialism and imperialism': 'Colonialism',
    'Imperialism and colonialism': 'Colonialism',
    'Colonialism (Imperialism)': 'Colonialism',
    'Colonialism / Imperialism': 'Colonialism',
    'Colonialism (Africa)': 'Colonialism',
    'British imperialism (Colonialism—Great Britain)': 'British imperialism',
    'British imperialism (colonialism)': 'British imperialism',
    
    # PAN-AFRICANISM  
    'Pan‑Africanism': 'Pan-Africanism',  # Fix en-dash
    
    # RACIAL VIOLENCE
    'Racial violence and lynching': 'Lynching and mob violence',
    'Lynching and racial violence': 'Lynching and mob violence',
    
    # HOUSING
    'Housing discrimination': 'Residential segregation',
    
    # CRIMINAL JUSTICE
    'Racial discrimination in the criminal justice system': 'Criminal justice discrimination',
}

def parse_qmd_file(file_path):
    """Parse a .qmd file and extract frontmatter and content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    match = re.match(r'^(\s*---\n)(.*?)(\n---\n)(.*)', text, re.DOTALL)
    if not match:
        return None
    
    try:
        frontmatter = yaml.safe_load(match.group(2))
        return {
            'frontmatter': frontmatter,
            'frontmatter_text': match.group(2),
            'content': match.group(4),
            'yaml_start': match.group(1),
            'yaml_end': match.group(3),
        }
    except:
        return None

def update_subjects(subjects):
    """Update subjects list with consolidated terms."""
    if not subjects:
        return subjects, []
    
    updated = []
    changes = []
    
    for subject in subjects:
        if not isinstance(subject, str):
            # Skip non-string subjects (structured data)
            updated.append(subject)
            continue
            
        if subject in CONSOLIDATION_MAP:
            new_subject = CONSOLIDATION_MAP[subject]
            updated.append(new_subject)
            changes.append(f"{subject} → {new_subject}")
        else:
            updated.append(subject)
    
    # Remove duplicates while preserving order
    seen = set()
    deduped = []
    for item in updated:
        # Only dedupe string items
        if isinstance(item, str):
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        else:
            deduped.append(item)
    
    return deduped, changes

def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    volumes_dir = Path('Volumes')
    article_files = sorted(volumes_dir.glob('**/*.qmd'))
    
    total_changes = 0
    files_changed = 0
    all_changes = defaultdict(int)
    
    print("Consolidating subject terms to broader categories...")
    print(f"Mode: {'DRY RUN - no changes' if dry_run else 'LIVE - will modify files'}")
    print("="*80)
    
    for file_path in article_files:
        parsed = parse_qmd_file(file_path)
        if not parsed:
            continue
        
        frontmatter = parsed['frontmatter']
        subjects = frontmatter.get('subjects', [])
        
        if not subjects:
            continue
        
        new_subjects, changes = update_subjects(subjects)
        
        if changes:
            files_changed += 1
            total_changes += len(changes)
            
            print(f"\n{file_path}:")
            for change in changes:
                print(f"  {change}")
                all_changes[change] += 1
            
            if not dry_run:
                # Update the frontmatter
                frontmatter['subjects'] = new_subjects
                
                # Write back
                new_yaml = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True, width=1000)
                new_content = f"---\n{new_yaml}---\n{parsed['content']}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files changed: {files_changed}")
    print(f"Total changes: {total_changes}")
    
    print("\n" + "="*80)
    print("MOST COMMON CONSOLIDATIONS")
    print("="*80)
    for change, count in sorted(all_changes.items(), key=lambda x: (-x[1], x[0]))[:20]:
        print(f"{count:3d}  {change}")

if __name__ == '__main__':
    main()
