# Dare You Fight: W.E.B. Du Bois Digital Archive

A comprehensive digital archive of W.E.B. Du Bois's writings from *The Crisis* magazine (1910-1934), featuring 700+ articles with Library Science-based indexing and scholarly metadata.

🌐 **Live Site:** [www.dareyoufight.org](https://www.dareyoufight.org)

## Overview

This archive preserves and makes accessible Du Bois's editorial writings from his tenure as editor of *The Crisis*, the official magazine of the NAACP. The collection documents 25 years of commentary on racial violence, voting rights, education, Pan-Africanism, and the ongoing struggle for Black liberation in America.

### Key Features

- **708 articles** with full text and scholarly metadata
- **Library Science indexing** with 5 structured metadata fields
- **76 browse pages** organized by subject, person, and place
- **Full-text search** across all articles
- **SEO optimized** for discoverability
- **Mobile responsive** design
- **Citation support** with DOIs and Google Scholar integration

## Archive Statistics

- **2,750+ unique subjects** indexed
- **620+ people** discussed across articles
- **493+ places** referenced
- **585+ organizations** documented
- **229+ historical events** tagged

### Top Subjects
- Lynching (72 articles)
- Voting rights (16 articles)
- Pan-Africanism (16 articles)
- Educational inequality (18 articles)
- Jim Crow laws (15 articles)

### Featured Historical Figures
- Woodrow Wilson (34 articles)
- Booker T. Washington (17 articles)
- Marcus Garvey (7 articles)
- Theodore Roosevelt (14 articles)
- Herbert Hoover (12 articles)

## Browse the Archive

The archive offers multiple ways to explore Du Bois's writings:

- **[By Subject](https://www.dareyoufight.org/browse/subjects/)** - Browse by theme (lynching, voting rights, education, etc.)
- **[By People](https://www.dareyoufight.org/browse/people/)** - Browse by historical figures discussed
- **[By Place](https://www.dareyoufight.org/browse/places/)** - Browse by geographic location
- **[By Decade](https://www.dareyoufight.org/browse.html)** - Browse by time period
- **[Chronological](https://www.dareyoufight.org/listing.html)** - Complete listing with search
- **[Visual Map](https://www.dareyoufight.org/map.html)** - Geographic visualization

## Project Structure

```
fightordie/
├── Volumes/              # Article files organized by volume/issue
│   ├── 01/              # Volume 1 (Nov 1910 - Oct 1911)
│   ├── 02/              # Volume 2 (Nov 1911 - Oct 1912)
│   └── ...
├── browse/              # Browse pages by subject/people/places
│   ├── subjects/        # Subject browse pages
│   ├── people/          # People browse pages
│   └── places/          # Place browse pages
├── docs/                # Rendered HTML output (GitHub Pages)
├── _quarto.yml          # Quarto configuration
├── index.qmd            # Homepage
├── listing.qmd          # Complete article listing
└── README.md            # This file
```

## Technology Stack

- **[Quarto](https://quarto.org/)** - Publishing system for scholarly content
- **GitHub Pages** - Hosting and deployment
- **OpenAI GPT-5-mini** - Automated metadata generation
- **Python** - Data processing and workflow automation

## Metadata Structure

Each article includes comprehensive metadata following Library Science principles:

```yaml
---
title: 'Article Title'
description: "SEO-optimized description"
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: March 1916

# Structured index terms
subjects:
  - Lynching
  - Voting rights
people:
  - Woodrow Wilson
  - Booker T. Washington
places:
  - Washington, D.C.
  - Mississippi
organizations:
  - NAACP
  - U.S. Congress
events:
  - World War I (1914-1918)

# Citation metadata
citation:
  type: article-journal
  container-title: The Crisis
  volume: 12
  issue: 3
  page: 113-114
---
```

## Adding New Articles

We've created a streamlined workflow for adding articles to the archive:

### Quick Start

```bash
# 1. Create article from template
python new_article.py \
  --volume 12 \
  --issue 3 \
  --title "The Crisis of Democracy" \
  --date "March 1916" \
  --pages "113-114"

# 2. Edit the created file and add article content

# 3. Auto-generate metadata (description + index terms)
python process_new_articles.py

# 4. Preview locally
quarto preview

# 5. Commit and deploy
git add Volumes/
git commit -m "Add article: The Crisis of Democracy"
git push
```

See [ARTICLE_WORKFLOW.md](ARTICLE_WORKFLOW.md) for complete documentation.

## Available Scripts

### Article Management
- `new_article.py` - Create new article from template
- `process_new_articles.py` - Auto-generate descriptions and index terms
- `add_article_descriptions.py` - Add SEO descriptions only
- `add_article_index.py` - Add Library Science index terms only

### Browse Page Generation
- `generate_browse_pages.py` - Generate subject/people/place browse pages
- `create_browse_indexes.py` - Generate browse directory indexes
- `analyze_index_terms.py` - Analyze index term frequency

### Utilities
- `clean_empty_categories.py` - Clean up empty category entries
- `fix_categories.py` - Fix category YAML formatting

## Development

### Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) (latest version)
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- OpenAI API key (for metadata generation)

### Setup

```bash
# Clone repository
git clone https://github.com/nealcaren/fightordie.git
cd fightordie

# Set OpenAI API key
export OPENAI_API_KEY='your-key-here'

# Install dependencies (handled by uv automatically)

# Preview site locally
quarto preview
```

### Build and Deploy

```bash
# Render site
quarto render

# Output is in docs/ directory
# Push to GitHub and it auto-deploys via GitHub Pages
git push
```

## Documentation

- **[ARTICLE_WORKFLOW.md](ARTICLE_WORKFLOW.md)** - Complete guide for adding articles
- **[INDEX_TAXONOMY.md](INDEX_TAXONOMY.md)** - Library Science indexing guidelines
- **[CATEGORIES.md](CATEGORIES.md)** - Original category taxonomy (legacy)

## Citation

If you use this archive in your research, please cite:

```bibtex
@misc{dubois_crisis_archive,
  title = {Dare You Fight: W.E.B. Du Bois Digital Archive},
  author = {Caren, Neal},
  year = {2024},
  url = {https://www.dareyoufight.org},
  note = {Digital archive of W.E.B. Du Bois's writings from The Crisis magazine, 1910-1934}
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow the article workflow for new content
4. Submit a pull request

## Acknowledgments

- **W.E.B. Du Bois** - Author of all articles
- **The Crisis Magazine** - Original publisher (1910-1934)
- **NAACP** - Publisher of The Crisis
- **Modernist Journals Project** - Source for many articles
- **HathiTrust Digital Library** - Additional source materials

## License

The articles by W.E.B. Du Bois are in the public domain. The website code and structure are available under the MIT License.

## Contact

For questions or feedback:
- **GitHub Issues:** [github.com/nealcaren/fightordie/issues](https://github.com/nealcaren/fightordie/issues)
- **Website:** [www.dareyoufight.org](https://www.dareyoufight.org)

---

*"Dare you fight or would you rather die?"* - W.E.B. Du Bois, The Crisis
