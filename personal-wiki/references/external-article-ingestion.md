# Ingesting External Web Articles into Wiki

Pattern for saving a web article to both the local mirror (original HTML + assets, offline-browsable) and the wiki (Chinese synthesis page with structured takeaways).

## Scope

This covers **non-WeChat web articles** (blogs, research posts, tech articles on custom domains). For WeChat Official Account articles (`mp.weixin.qq.com`), use the `weixin-article-to-wiki` skill instead — those go to `reading_notes/` as standalone HTML, not to `concepts/`.

## Workflow

### Step 0: Present a plan first

Before any download or writing, present a concise plan to the user:

1. What will be downloaded and where (`~/mirror/<domain>/`)
2. What the wiki synthesis page will cover (key sections)
3. Which index files will be updated

Wait for user confirmation before executing. This avoids wasted work if the user wants a different approach.

### Step 1: Download the full page mirror

```bash
mkdir -p ~/mirror/<domain>
cd ~/mirror/<domain>
wget -nc -p -k -E --restrict-file-names=windows -e robots=off --wait=0.3 \
  --directory-prefix=. "https://<full-url>"
```

This produces `~/mirror/<domain>/<hostname>/<path>.html` with all CSS/JS/images as relative paths. The page is fully offline-browsable via `file://`.

### Step 2: Extract article metadata

Quick Python scan to get title, description, heading structure, and image count:

```python
import re
with open('/tmp/page.html') as f:
    html = f.read()
title = re.search(r'<title>(.*?)</title>', html)
desc = re.search(r'<meta name="description" content="([^"]+)"', html)
headings = re.findall(r'<(h[12])[^>]*>(.*?)</\1>', html)
imgs = re.findall(r'<img[^>]+src="([^"]+)"', html)
```

### Step 3: Write the wiki synthesis page

Save to `~/hermes/wiki/concepts/<slug>.md`.

**Frontmatter template:**
```yaml
---
title: "<中文标题> — <英文原标题> 总结"
author: <original author>
source: <original URL>
mirror: ~/mirror/<domain>/<host>/<path>.html
date: <publication date>
saved: <today>
tags: [<relevant tags>]
status: reference
type: concept
domain: <wiki domain>
---
```

**Body structure** (follow coolshell synthesis style):
- `> 原文` blockquote with source link and local mirror path
- One-line description of the article
- `---` separator
- Numbered sections, each with:
  - Bold key term + Chinese explanation
  - Bullet points for key insights (concise, no filler)
  - Quotes from the article in `>` blockquotes where impactful
- Final `## 关键 takeaways` section
- Reference to local mirror for full original

**Style rules:**
- Chinese-language synthesis, not raw translation
- Thematic organization by concepts, not chronological
- Concise bullets — each line carries one insight
- No verbose preamble or "这篇文章讨论了…" filler

### Step 4: Update wiki indexes

Two files to update:

**`~/hermes/wiki/README.md`:**
- Increment total page count (line ~11)
- Increment `concepts (N)` count in overview block
- Increment domain section heading count and add page link
- Increment concepts count in bottom table
- Update `updated:` date in frontmatter

**`~/hermes/wiki/index.md`:**
- Increment total page count in header line
- Increment `Concepts（概念，N 页）` heading
- Add new entry in alphabetical order under Concepts section
- Update date in header line

## Pitfalls

- **DO NOT convert to markdown as the primary artifact.** The original HTML is the authoritative copy. The wiki synthesis page is a derivative summary with structured takeaways and Chinese explanations.
- **DO NOT put images in wiki assets.** Images stay in the mirror directory. The synthesis page is text-only (or links to mirror images).
- **Mirror path convention:** All website mirrors live under `~/mirror/<domain>/`. This was consolidated from an earlier split where coolshell lived under `~/hermes/coolshell-mirror/`.
- **Index updates are mechanical but error-prone:** The four files to touch are:
  1. `README.md` — total page count, concepts count in overview block, domain section count + page link, bottom table count, frontmatter date
  2. `index.md` — total page count in header, `Concepts` heading count, new entry in alphabetical order, header date
  Missing any one creates inconsistency. Verify with `grep -n "页" README.md index.md` that all counts agree.

## Examples

| Article | Mirror | Wiki Synthesis |
|---------|--------|----------------|
| How LLMs Actually Work | `~/mirror/0xkato.xyz/` (6.8MB) | `concepts/how-llms-actually-work.md` (9KB) |
| CoolShell (740 articles) | `~/mirror/coolshell.org/` (228MB) | `concepts/coolshell.md` + 5 topic pages |
