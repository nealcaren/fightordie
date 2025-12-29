# Workflow for Adding New Articles

This guide explains how to add new articles to the W.E.B. Du Bois digital archive.

## Quick Start

```bash
# 1. Create new article from template
python new_article.py --volume 12 --issue 3 --title "My Article Title" --date "March 1916"

# 2. Edit the content in the created file

# 3. Auto-generate metadata
python process_new_articles.py

# 4. Render and preview
quarto preview

# 5. Commit when ready
git add Volumes/
git commit -m "Add article: My Article Title"
git push
```

## Step-by-Step Guide

### 1. Create Article File

Use the `new_article.py` script to create a new article from the template:

```bash
python new_article.py \
  --volume 12 \
  --issue 3 \
  --title "The Crisis of Democracy" \
  --date "March 1916" \
  --pages "113-114"
```

This creates: `Volumes/12/03/the_crisis_of_democracy.qmd`

The file will have:
- Proper YAML frontmatter with placeholders
- Standard author info (W.E.B. Du Bois)
- Citation metadata
- Ready for content

### 2. Add Article Content

Edit the file and paste the article text below the frontmatter:

```markdown
---
title: 'The Crisis of Democracy'
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: March 1916
...
---

[Your article content here]
```

### 3. Auto-Generate Metadata

Run the processing script to add:
- SEO description
- Structured index terms (subjects, people, places, organizations, events)

```bash
python process_new_articles.py
```

This script:
1. Finds articles missing descriptions
2. Finds articles missing index terms
3. Uses GPT-5-mini to generate both
4. Updates the files

**Options:**
```bash
# Dry run to preview changes
python process_new_articles.py --dry-run

# Process specific volume
python process_new_articles.py --volume 12

# Limit number of articles
python process_new_articles.py --limit 5
```

### 4. Preview Changes

```bash
# Preview locally
quarto preview

# Or render specific article
quarto render Volumes/12/03/the_crisis_of_democracy.qmd
```

### 5. Update Browse Pages (if needed)

If you've added many new articles with new subjects/people/places:

```bash
# Regenerate browse pages for new index terms
python generate_browse_pages.py

# Create new directory indexes
python create_browse_indexes.py

# Render browse pages
quarto render browse/
```

### 6. Commit and Deploy

```bash
# Add all changes
git add Volumes/ browse/ docs/

# Commit with descriptive message
git commit -m "Add article: The Crisis of Democracy (Vol 12, Issue 3)"

# Push to GitHub (auto-deploys to GitHub Pages)
git push
```

## Article File Structure

### Required Frontmatter Fields

```yaml
---
title: 'Article Title'
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: March 1916
citation:
  type: article-journal
  container-title: The Crisis
  volume: 12
  issue: 3
  page: 113-114
google-scholar: true
format:
  html:
    toc: false
    appendix-cite-as: display
---
```

### Auto-Generated Fields

These are added automatically by `process_new_articles.py`:

```yaml
description: "Brief SEO-friendly description of article content"
categories: []
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
```

## Manual Override

If you want to manually set any metadata:

1. Add it to the frontmatter before running `process_new_articles.py`
2. The script will skip fields that already exist
3. You can regenerate by removing the field and re-running

## Tips

**File Naming:**
- Use lowercase
- Replace spaces with underscores
- Keep it short but descriptive
- Example: `the_crisis_of_democracy.qmd`

**Dates:**
- Use format: "March 1916" or "Jan. 1912"
- Script will parse and format correctly

**Categories:**
- Always initialize as empty array: `categories: []`
- We use structured index fields instead

**Images:**
- Place in `Volumes/[volume]/[issue]/images/`
- Reference with relative path: `images/photo.png`

## Troubleshooting

**Missing API Key:**
```bash
export OPENAI_API_KEY='your-key-here'
```

**YAML Errors:**
- Check quote escaping in description
- Ensure proper indentation (2 spaces)
- Run: `quarto check` to validate

**Index Terms Not Generated:**
- Check article has content (not just frontmatter)
- Ensure OpenAI API key is set
- Try with `--dry-run` to see error messages

## Batch Processing

Adding multiple articles at once:

```bash
# Create multiple articles
python new_article.py --volume 12 --issue 3 --title "Article 1" --date "March 1916"
python new_article.py --volume 12 --issue 3 --title "Article 2" --date "March 1916"
python new_article.py --volume 12 --issue 3 --title "Article 3" --date "March 1916"

# Edit all the files with content

# Process all new articles in one go
python process_new_articles.py

# Render everything
quarto render

# Commit all at once
git add Volumes/12/03/
git commit -m "Add 3 articles from Volume 12, Issue 3"
git push
```

## Scripts Reference

- `new_article.py` - Create new article from template
- `process_new_articles.py` - Auto-generate descriptions and index terms
- `generate_browse_pages.py` - Regenerate subject/people/place browse pages
- `create_browse_indexes.py` - Regenerate browse directory indexes
- `add_article_descriptions.py` - (Legacy) Add descriptions only
- `add_article_index.py` - (Legacy) Add index terms only
