# Index Taxonomy for W.E.B. Du Bois Digital Archive

This document defines the controlled vocabularies and guidelines for indexing articles using Library Science principles.

## Five Index Fields

Each article will have up to 5 structured index fields:

1. **subjects** - What the article is about (thematic subject headings)
2. **people** - Who is discussed or mentioned (proper names)
3. **places** - Geographic locations referenced
4. **organizations** - Institutions, groups, parties, unions
5. **events** - Specific historical events or incidents

## Field Guidelines

### Subjects (3-6 per article)

Thematic subject headings describing what the article is about. Use Library of Congress style headings when possible.

**Examples:**
- Lynching
- Voting rights
- Educational inequality
- Residential segregation
- Military discrimination
- Anti-lynching legislation
- Labor organizing
- Racial violence
- Political disenfranchisement
- Jim Crow laws
- Interracial marriage
- Economic discrimination
- Police brutality
- Housing discrimination
- School segregation
- Literary criticism
- Cultural nationalism
- Pan-Africanism
- Colonialism
- Women's suffrage
- Constitutional rights
- Criminal justice
- Public health
- Migration patterns

**Format:** Use specific, searchable terms. Prefer concrete subjects to abstract concepts.

### People (2-8 per article)

Proper names of individuals discussed, quoted, or significantly mentioned. Include:
- Political figures
- Civil rights leaders
- Victims of violence (if named)
- Authors and intellectuals
- International figures
- Opponents and allies

**Common people in The Crisis:**

*Presidents:*
- Woodrow Wilson
- Theodore Roosevelt
- William Howard Taft
- Warren G. Harding
- Calvin Coolidge
- Herbert Hoover
- Franklin D. Roosevelt

*Black Leaders:*
- Booker T. Washington
- Marcus Garvey
- Mary Church Terrell
- Ida B. Wells-Barnett
- James Weldon Johnson
- Walter White
- Charles Chesnutt
- Paul Robeson
- Langston Hughes

*NAACP Leaders:*
- Joel Spingarn
- Mary White Ovington
- Moorfield Storey
- James Weldon Johnson
- Walter White

*Politicians:*
- Charles Sumner
- Benjamin Tillman
- James K. Vardaman
- Theodore Bilbo
- Leonidas C. Dyer

**Format:** Use full names when known. For common figures, use consistent form (e.g., "Booker T. Washington" not "Booker Washington").

### Places (1-5 per article)

Geographic locations that are central to the article's content.

**U.S. Cities (common in The Crisis):**
- Chicago
- New York City
- Washington, D.C.
- East St. Louis
- Atlanta
- Philadelphia
- Detroit
- Houston
- Memphis
- Birmingham

**U.S. States/Regions:**
- Mississippi
- Georgia
- South Carolina
- The South (as region)
- The North (as region)

**Countries/Regions:**
- Haiti
- Liberia
- South Africa
- Africa (general)
- Europe
- Caribbean

**Format:** Use standard place names. Include U.S. state for cities when needed for clarity.

### Organizations (1-4 per article)

Institutions, political parties, unions, churches, schools, government bodies.

**Common organizations:**

*Civil Rights:*
- NAACP
- National Urban League
- Brotherhood of Sleeping Car Porters
- Niagara Movement

*Political:*
- Republican Party
- Democratic Party
- Socialist Party
- U.S. Congress
- U.S. Supreme Court

*Educational:*
- Howard University
- Fisk University
- Tuskegee Institute
- Atlanta University
- Hampton Institute

*Labor:*
- American Federation of Labor (AFL)
- Congress of Industrial Organizations (CIO)

*Religious:*
- African Methodist Episcopal Church
- Baptist Church

*Publications:*
- The Crisis
- New York Times
- Chicago Defender

*International:*
- League of Nations
- Pan-African Congress

**Format:** Use full official names. Spell out abbreviations on first use.

### Events (0-3 per article)

Specific historical events, incidents, riots, conferences, elections, court cases.

**Common events:**

*Racial Violence:*
- East St. Louis Race Riot (1917)
- Red Summer (1919)
- Chicago Race Riot (1919)
- Tulsa Race Massacre (1921)
- Houston Mutiny (1917)
- Atlanta Riot (1906)

*Political Events:*
- Presidential Election (1912)
- Presidential Election (1916)
- Presidential Election (1920)
- etc.

*International:*
- World War I
- Pan-African Congress (1919)
- Pan-African Congress (1921)
- Pan-African Congress (1923)

*Legal:*
- Buchanan v. Warley (1917)
- Guinn v. United States (1915)

*Campaigns:*
- Dyer Anti-Lynching Bill Campaign (1921-1922)

**Format:** Include year in parentheses when helpful. Be specific rather than general.

## Indexing Principles

1. **Specificity**: Use specific terms, not general ones
   - Good: "Educational inequality"
   - Avoid: "Education"

2. **Consistency**: Use the same form for recurring topics
   - Always: "Booker T. Washington" (not variations)

3. **Relevance**: Only index what's substantially discussed
   - Don't index brief mentions or passing references

4. **Completeness**: Include all significant topics, people, places
   - Aim for 8-15 total index terms per article

5. **User-Centered**: Think about what researchers would search for
   - Include both formal and common terms when useful

## Example: Fully Indexed Article

**"The Souls of White Folk" (1920)**

```yaml
subjects:
  - White supremacy
  - Colonialism
  - World War I
  - Racial psychology
  - Imperialism

people:
  - Woodrow Wilson

places:
  - Europe
  - Africa
  - United States

organizations:
  - League of Nations

events:
  - World War I
  - Paris Peace Conference (1919)
```

## Auto-Indexing Process

Index terms are generated using `add_article_index.py`:

```bash
# Test on 10 articles
uv run add_article_index.py --dry-run --limit 10

# Index all articles
uv run add_article_index.py --workers 10
```

The script uses GPT-5-mini to extract structured index terms from article titles, descriptions, and content previews.
