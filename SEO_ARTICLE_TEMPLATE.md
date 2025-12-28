# SEO Template for Individual Articles

To improve SEO for individual articles, add a `description` field to each article's frontmatter.

## Example: Current Article Format

```yaml
---
title: 'Agitation'
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: Nov. 1910
categories:
  - Tactics
  - NAACP
citation:
  type: article-journal
  container-title: The Crisis
  volume: 1
  issue: 1
  page: 11
google-scholar: true
format:
  html:
    toc: false
    appendix-cite-as: display
---
```

## Updated Format with SEO

```yaml
---
title: 'Agitation'
description: "W.E.B. Du Bois argues that agitation is essential for exposing racial injustice, comparing it to pain that alerts the body to disease. Published in The Crisis (1910)."
author:
  - name:
      given: W.E.B.
      family: Du Bois
date: Nov. 1910
categories:
  - Tactics
  - NAACP
citation:
  type: article-journal
  container-title: The Crisis
  volume: 1
  issue: 1
  page: 11
google-scholar: true
format:
  html:
    toc: false
    appendix-cite-as: display
---
```

## Tips for Writing Descriptions

1. **Length**: Keep between 120-160 characters
2. **Content**: Briefly summarize the main argument or topic
3. **Keywords**: Include relevant terms (e.g., "racial justice," "civil rights," "NAACP")
4. **Context**: Mention it's from The Crisis and the year
5. **Action**: What does Du Bois argue, discuss, or analyze?

## Template Formula

```
"W.E.B. Du Bois [argues/discusses/examines] [main topic/argument]. Published in The Crisis ([year])."
```

## More Examples

### For a political article:
```yaml
description: "W.E.B. Du Bois critiques President Taft's approach to racial issues and argues for stronger federal protection of Black voting rights. From The Crisis (1911)."
```

### For an analysis piece:
```yaml
description: "Du Bois examines the economic factors driving the Great Migration of African Americans from the South to northern cities. The Crisis (1917)."
```

### For a cultural piece:
```yaml
description: "W.E.B. Du Bois celebrates the emergence of the Harlem Renaissance and calls for authentic Black artistic expression free from white expectations. The Crisis (1926)."
```

## Batch Processing Tip

You could create a Python script to automatically add descriptions based on:
- The article's first paragraph
- Existing categories
- Title analysis

This would help process the 600+ articles more efficiently.
