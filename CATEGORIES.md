# Article Category Taxonomy

This document defines the controlled vocabulary for categorizing W.E.B. Du Bois's articles from The Crisis (1910-1934).

## Category List

### Civil Rights & Political Action
- **Lynching & Racial Violence** - Anti-lynching campaigns, documentation of lynchings, mob violence, race riots
- **Voting Rights & Disenfranchisement** - Suffrage, voter suppression, grandfather clauses, political participation
- **Segregation & Jim Crow** - Jim Crow laws, residential segregation, public accommodations, railroad cars
- **Social Equality** - Debates over social equality, interracial mixing, marriage laws
- **Law & Justice** - Court cases, legal discrimination, the justice system, Supreme Court decisions

### Organizations & Movements
- **NAACP Activities** - NAACP organizing, branches, campaigns, internal affairs
- **Pan-Africanism & International** - Pan-African Congresses, international solidarity, colonialism
- **Labor & Economics** - Labor unions, strikes, economic conditions, employment, class struggle
- **Women's Rights & Suffrage** - Women's suffrage, gender equality, women's organizations

### War & Migration
- **World War I** - WWI service, discrimination in military, "Close Ranks," Houston Mutiny
- **World War II** - WWII era writings (1930s buildup)
- **Migration** - The Great Migration, urban migration, demographic shifts

### Education & Culture
- **Education & Schools** - Public schools, colleges, educational policy, literacy
- **Arts & Culture** - Literature, music, theater, Harlem Renaissance, art
- **Religion & Church** - Black church, Christianity, religious leaders and institutions
- **The Crisis (magazine)** - Meta-commentary about The Crisis itself

### International Focus
- **Africa** - African affairs, colonialism, independence movements
- **Haiti & Caribbean** - Haitian affairs, Caribbean issues, U.S. occupation

### Other Topics
- **Politics & Elections** - Presidential elections, parties, political strategy
- **Health & Housing** - Public health, housing conditions, living standards
- **Youth & Children** - Children's issues, youth organizing, education
- **Biography & Obituary** - Profiles of individuals, death notices, biographical sketches

## Usage Guidelines

### Assigning Categories

1. **Primary Focus**: Choose categories based on the article's main topic, not every subject mentioned
2. **Quantity**: Most articles should have 2-3 categories; 4 maximum
3. **Specificity**: Choose the most specific applicable category
4. **Historical Context**: Consider how Du Bois and his contemporaries would have framed the issue

### Examples

**"Crime and Lynching" (1912)**
- Lynching & Racial Violence
- Law & Justice

**"Close Ranks" (1918)**
- World War I
- NAACP Activities

**"Returning Soldiers" (1919)**
- World War I
- Lynching & Racial Violence
- Social Equality

**"Criteria of Negro Art" (1926)**
- Arts & Culture
- Social Equality

## Auto-Categorization

Categories are assigned using the `add_article_categories.py` script:

```bash
# Test on 10 articles
uv run add_article_categories.py --dry-run --limit 10

# Categorize all articles
uv run add_article_categories.py --workers 10
```

## Category Pages

Each category has its own browse page at `browse/[category-slug].qmd` that automatically filters articles with that category.
