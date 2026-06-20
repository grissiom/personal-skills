# Wiki Integration: Mirror + Synthesis Page

When saving a web article into the personal wiki at `~/hermes/wiki/`, use a **two-track** approach:

1. **Raw HTML mirror** — full offline copy with wget, preserved as-is (like coolshell)
2. **Wiki synthesis page** — a hand-written summary that distills the article's key insights, organized thematically (NOT a markdown conversion of the original)

**Do NOT** convert the article body to markdown and save it as the wiki page. The wiki page is a **synthesis/study note**, not a mirror. The original HTML mirror serves as the authoritative reference.

## Why This Approach

The user maintains a knowledge wiki where pages are structured summaries — thematic distillations with key takeaways, organized by concept, with links back to source material. This is the same pattern used for coolshell articles: the mirror has 740 raw HTML files, and the wiki has 6 synthesis pages that extract and organize the knowledge by theme.

## Step 1: Download Raw Mirror

Use the standard wget command from the main skill:

```bash
mkdir -p ~/mirror/domain.tld
wget -nc -p -k -E \
  --restrict-file-names=windows \
  -e robots=off \
  --wait=0.3 \
  --directory-prefix=~/mirror/domain.tld \
  "https://domain.tld/path/to/article"
```

The mirror at `~/mirror/domain.tld/` preserves the original HTML with all assets. It can be opened with `file://` for offline browsing. **Do not delete or convert this mirror.**

## Step 2: Read the Article Thoroughly

Read the full article content from the mirror (not just a skim). Identify:
- The article's structure (sections, headings)
- Key insights per section
- Notable facts, data points, or quotes worth preserving
- The overall thesis and takeaways

## Step 3: Write the Synthesis Page

Create `~/hermes/wiki/concepts/{slug}.md` with:

### Frontmatter
```yaml
---
title: "中文标题 — English Title 总结"
author: Original Author
source: https://original-url
mirror: ~/mirror/domain.tld/path/to/article.html   # path to local mirror
date: YYYY-MM-DD      # article publish date
saved: YYYY-MM-DD     # date saved to wiki
tags: [relevant, tags]
status: reference
type: concept
domain: relevant-domain
---
```

### Body Structure

Follow the coolshell synthesis page style:

1. **Header** — `# Title` with source attribution and mirror path in blockquote
2. **Numbered sections** — one per major topic in the article, each with:
   - Section heading (`## N. Topic Name`)
   - Key insight in bold or as bullet points
   - Notable details, data, or quotes
   - Core mechanism / "why it matters"
3. **Summary table** (if comparing multiple things)
4. **Key takeaways** section at the end

Style guidelines:
- Write in **Chinese** (user's language), with English technical terms preserved
- Use **bold** for key terms and core insights
- Use blockquotes (`>`) for source attribution only, not for content
- Keep it concise — this is a study note, not a transcript
- Use `[[wikilinks]]` for cross-references to other wiki pages
- Mention the mirror path so the user knows where to find the original

## Step 4: Update Wiki Index Files

Two files must be patched:

### README.md (知识地图 — by domain)
- Increment total page count
- Find the relevant domain section, increment its count
- Add `[[concepts/slug|Display Title]] — one-line summary` entry
- Update `updated:` date in frontmatter

### index.md (完整目录 — by type)
- Increment `Concepts（概念，N 页）` count and total pages
- Insert entry in **alphabetical order** with one-line summary
- Update date in header

## Complete Workflow

```
1. wget -p -k -E URL → ~/mirror/domain.tld/          (raw mirror, keep forever)
2. Read article from mirror                            (understand fully)
3. Write synthesis → ~/hermes/wiki/concepts/{slug}.md  (hand-written, not converted)
4. Patch README.md (stats + domain entry)
5. Patch index.md (stats + alphabetical entry)
```

## Comparison: What NOT to Do

| ❌ Wrong | ✅ Right |
|----------|---------|
| Convert HTML to markdown with parser | Read and write synthesis by hand |
| Save MD conversion as wiki page | Save hand-written summary as wiki page |
| Delete mirror after conversion | Keep mirror as authoritative reference |
| Raw copy-paste of article text | Distill, organize, add structure |
