---
name: weixin-article-to-wiki
description: "Save a WeChat Official Account (mp.weixin.qq.com) article to the personal wiki's reading_notes/ directory."
version: 2.1.0
platforms: [linux]
---

# WeChat Article → Wiki

> This skill handles WeChat-specific quirks (lazy-loaded images, code-block cleanup, magic-byte detection).
> For all wiki conventions — index format, log format, frontmatter, cross-referencing, synthesis rules,
> README updates, page counts — **always also load `llm-wiki`** and follow its ingest procedures.
> The two skills work together: `llm-wiki` defines the wiki structure and navigation updates,
> this skill handles the WeChat extraction pipeline.

Save a WeChat article URL to `~/hermes/wiki/reading_notes/` producing:

- `<slug>.html` — standalone readable HTML with inline styles and
  locally-downloaded images (zero external dependencies, works offline)
- `<slug>_files/` — downloaded images referenced by the standalone HTML

Also updates `~/hermes/wiki/index.md` with a descriptive summary.

**No markdown file is generated** — the HTML is the canonical copy.

## Trigger

User shares a `https://mp.weixin.qq.com/s/...` URL and asks to save it.

## Steps

### 1. Run the extraction script

The script lives in this skill's `scripts/` directory. Use its absolute path:

```bash
python3 ~/.hermes/skills/productivity/weixin-article-to-wiki/scripts/save_wx.py "<URL>"
```

Output: `OK|<html_path>|<title>|<author>|<slug>`

### 2. Fix slug if needed

Chinese titles produce very long auto-slugs. Rename to a short English slug:

```bash
mv "<long-slug>.html" "<short-slug>.html"
mv "<long-slug>_files" "<short-slug>_files"
```

Then fix the image paths inside the HTML:
```bash
sed -i 's/<long-slug>_files/<short-slug>_files/g' "<short-slug>.html"
```

Keep slugs under ~40 chars, kebab-case English (e.g. `multi-agent-harness-design`).

### 3. Follow llm-wiki ingest procedures

Read the article and write a descriptive summary capturing the core argument. Then
follow `llm-wiki`'s ingest step ⑤ for updating navigation:

- Add the entry to `index.md` under Reading Notes with the summary
- Update `README.md` — bump page count, domain count if applicable
- Append to `log.md` with source URL, file path, and index changes

Format for the index entry:
```markdown
- [<slug>](./<slug>.html) — <title>（<author>，<date>）  
  *<summary of the core argument>*
```

## What the Script Does

`scripts/save_wx.py` handles the full pipeline:

1. **Fetch** — downloads the article HTML from `mp.weixin.qq.com`
2. **Extract metadata** — title and author from OG meta tags
3. **Extract content** — pulls content from `id="js_content"` div
4. **Image handling** — replaces `data-src` → `src`, decodes `&amp;` in URLs,
   downloads every image to a local `_files/` directory, rewrites `src` to
   local paths
5. **Standalone HTML** — wraps content in a minimal HTML document with
   responsive CSS (no external dependencies)
6. **Post-processing** — strips `counter(line` prefix from WeChat code blocks,
   fixes `width="NNNpx"` → `width="NNN"`, adds CSS for `code-snippet__*` syntax
   highlighting classes

## Pitfalls

### Image loading
- WeChat images use **lazy loading**: real URLs are in `data-src`
  attributes, not `src`. The script converts `data-src="` → `src="`.
- Image URLs contain `&amp;` that must be decoded to `&` for the URL
  to work.
- WeChat CDN images (mmbiz.qpic.cn) may have referrer restrictions or
  short-lived tokens. **Always download images locally** — do not rely
  on the CDN for offline reading.
- **Image format detection**: do NOT guess the file extension from the
  URL path. WeChat CDN URLs often lack recognizable extensions (e.g.,
  SVG content served as `.jpg`). Use magic-byte detection in the
  script: `\xff\xd8\xff` = JPEG, `\x89PNG` = PNG, `<svg` in first 20
  bytes = SVG. The script's `download_img()` already does this.

### HTML output
- Do NOT save raw WeChat HTML — it references `res.wx.qq.com` JS/CSS
  that fails offline with 404s and console errors. Always produce the
  standalone version.
- Strip `data-*` attributes (clutter) but preserve `style` attributes
  (formatting).
- The standalone HTML must be fully self-contained: no external JS,
  CSS, fonts, or images.

### Code blocks
- WeChat's `code-snippet__*` widget uses CSS counters for line numbers.
  Offline, the `ounter(line` prefix leaks into visible text. Must be
  stripped: `re.sub(r'ounter\(<[^>]*>line</[^>]*>', 'line', html)` then
  `re.sub(r'ounter\(', '', html)` for remaining bare occurrences.
- WeChat wraps each code line in its own `<code>` tag with no whitespace
  between them. Insert `\n` between consecutive `</code><code>` pairs so
  lines render on separate rows.
- Add CSS for `code-snippet__selector-tag` (#569cd6),
  `code-snippet__selector-attr` (#9cdcfe),
  `code-snippet__selector-class` (#4ec9b0) for syntax highlighting.
- Fix invalid `width="NNNpx"` → `width="NNN"` in img tags.
- Hide `code-snippet__line-index` with `display:none`.
- Add full `pre` and `code` CSS: dark background (#1e1e1e), light text
  (#d4d4d4), monospace font, padding, border-radius, horizontal scroll.

### Wiki format
- Index entries MUST include a summary, not just a title and author.
- Index links MUST be plain markdown `[<slug>](./<slug>.html)`, not
  wikilinks. No `.md` files are generated.

### Referenced articles (when the user asks to save citations too)

When the user says "文中引用的文章也请找到并加入", only save articles
that the **author actually cited** in the body text. Do NOT save WeChat's
auto-generated "recommended reading" cards.

**Detection procedure:**

1. **Fetch the raw HTML** of the source article (the saved standalone
   version has already been stripped of these links — use the original
   WeChat URL).

2. **Extract only `js_content`** — the article body div. Recommendation
   cards live outside this div.

3. **Find real citations** — in `js_content`, search for `href="https?://mp\.weixin\.qq\.com/s/[^"]+"`.
   These are links the author intentionally placed in the article text.

4. **Identify and skip recommendation cards** — links outside `js_content`
   with `scene=21#wechat_redirect` and `__biz`-format URLs are WeChat's
   platform-generated "相关阅读" widgets. They are NOT author citations.
   Do not count them and do not save them.

5. **Count and report** — tell the user how many real citations were found
   vs. how many recommendation cards were skipped. If the only reference
   is an external paper/URL (not a WeChat article), say so explicitly
   and search for it — see `references/external-paper-search.md`.

**False-positive example:** A 4,300-character Tesla article had 0 real
WeChat citations in its body text but 43 recommendation-card links.
Saving those 43 would have added unrelated content to the wiki.
