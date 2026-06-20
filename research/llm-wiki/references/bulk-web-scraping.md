# Bulk Web Scraping for Wiki Ingest

Proven workflow for scraping an entire static blog or documentation site and
ingesting it into the llm-wiki. Use this when the user says "抓取所有文章"
or "scrape this blog and put into wiki".

## When This Applies

- Static HTML sites (WordPress exports, Jekyll, Hugo, GitHub Pages)
- Site has a listing page exposing all article URLs (e.g. `/articles/`)
- User wants ALL content + images, not a single article
- Dozens to thousands of articles

When the site is a dynamic SPA (React, Vue) or requires JavaScript rendering,
this approach won't work — fall back to browser-based extraction.

## Proven Workflow (5 phases)

### Phase 1: Reconnaissance

① Fetch the article listing page and extract all article URLs:

```bash
curl -sL 'https://example.com/articles/' | \
  grep -oP 'href="/articles/\d+\.html"' | \
  sed 's|href="|https://example.com|;s|"||' | \
  sort -u > /tmp/urls.txt
```

② Count and inspect:

```bash
wc -l /tmp/urls.txt
# Check date range from first/last articles
```

③ Check site structure (categories, tags) by sampling a few HTML files.

### Phase 2: Parallel Download (HTML only)

**DO NOT use `wget -p` or `--page-requisites`** — for bulk downloads of shared-asset sites
(WordPress, etc.), this re-downloads the same CSS/JS/plugin files for every article page,
making download 100x slower. Download HTML first, images second.

Use xargs + curl for parallelism (20 concurrent workers):

```bash
mkdir -p "$MIRROR/site/articles"
cat /tmp/urls.txt | while read url; do
  id=$(echo "$url" | grep -oP '\d+')
  echo "$url|$MIRROR/site/articles/$id.html"
done | xargs -P 20 -I {} sh -c '
  url=$(echo "{}" | cut -d"|" -f1)
  out=$(echo "{}" | cut -d"|" -f2)
  if [ ! -f "$out" ]; then
    curl -sL -o "$out.tmp" --max-time 30 "$url" && mv "$out.tmp" "$out" || rm -f "$out.tmp"
  fi
'
```

### Phase 3: Image Extraction & Download

① Extract unique image URLs from downloaded HTML:

```python
import os, re
from collections import OrderedDict

image_urls = OrderedDict()
for f in os.listdir(articles_dir):
    with open(os.path.join(articles_dir, f), errors='ignore') as fh:
        imgs = re.findall(r'<img[^>]+src="([^"]+)"', fh.read())
        for img in imgs:
            if img.startswith('/'):
                img = base_url.rstrip('/') + img
            if domain in img and 'plugin' not in img:  # filter plugin noise
                image_urls[img] = True
```

② Filter out noise: plugin thumbs (e.g. `wordpress-23-related-posts-plugin`),
rating stars (`wp-postratings`, `stars_crystal`), loading spinners.

③ Download images in parallel (same xargs pattern as above).

### Phase 4: Metadata Extraction

Use `execute_code` to extract metadata from all articles at once:

```python
articles = []
for f in sorted(html_files):
    # Parse: title, date, categories, tags, views
    # Save to JSON: /tmp/site_articles_meta.json
```

Key regex patterns for WordPress exports:
- Title: `<title>([^<]+)</title>` (then strip site suffix)
- Date: `<time[^>]*datetime="([^"]+)"`
- Categories: `rel="category tag">([^<]+)`
- Tags: `rel="tag">([^<]+)`
- Views: `([\d,]+)\s*人阅读`

### Phase 5: Wiki Integration (SYNTHESIS, not lists)

**CRITICAL — do not create list-only pages.** The wiki's value is in knowledge extraction,
not enumeration. The raw HTML files already live in `raw/`; the wiki pages must extract
what the content *means*.

① **Symlink raw files** (not copy — preserves mirror as source of truth):

```bash
mkdir -p ~/hermes/wiki/raw/articles/site-name
ln -sf "$MIRROR/site/articles/"*.html ~/hermes/wiki/raw/articles/site-name/
```

② **Analyze for thematic clusters** (not categories). Use `execute_code` to scan titles,
tags, and content to identify 3-6 coherent knowledge clusters. Examples from CoolShell:
- Programming Mindset & Career (132 articles → one synthesis page on growth paths, judgment, efficiency)
- Go Programming Patterns (21 articles → one page on the 9-pattern evolution)
- Linux & Systems Knowledge (87 articles → one page on TCP, Shell, containers, caching)
- Distributed Systems & Architecture (7+ articles → one page on CAP, HA, design principles)
- C/C++ Deep Understanding (93 articles → one page on memory model, concurrency, compiler behavior)

③ **Create one synthesis page per cluster** (NOT one list page per category). Each page:
- Has a clear thesis or organizing principle
- Extracts key insights, patterns, and principles from the source articles
- Links to specific raw articles for deep dives using local paths: `[title](raw/articles/site-name/123.html)`
- Cross-references existing wiki pages via `[[wikilinks]]`
- Uses tables to compare positions/approaches, not to list article metadata
- NEVER contains a full-dump table of "date | title | views | tags"

④ **Create an overview page** (`concepts/site-name.md`): author, scope, date range, the
knowledge map (links to each cluster synthesis page), and cross-references.

⑤ **Update `index.md`** with the overview + cluster pages. Update total page count.

⑥ **Update `log.md`** with a single comprehensive entry.

**Anti-pattern (what NOT to do):**
```
## 文章列表
| # | 日期 | 标题 | 阅读量 | 标签 |
|---|------|------|--------|------|
| 1 | 2022-07 | [文章A](https://external.com/...) | 37K | TCP, Linux |
| 2 | 2022-05 | [文章B](https://external.com/...) | 33K | Go, etcd |
... (repeated for 200+ rows)
```

**Correct pattern:**
```
## 成长路径
陈皓定义了程序员的四个阶段：[启蒙→入门→提高→设计]...
关键文章：[练级攻略](raw/articles/coolshell/4990.html)

## 三条核心建议
1. 学好 C 语言 — 不是为了用 C，而是理解计算机
2. 深入一个领域 — 不要追逐每个新技术
3. 持续输出 — 写博客、做开源
... (principles, patterns, conclusions — knowledge)
```

## Pitfalls

- **wget -p is a trap for bulk**: kills performance on shared-asset sites. Split into HTML-then-images.
- **xargs -P 20 is safe**: curl parallel downloads at P=20 won't hammer most sites. Use --max-time as safety net.
- **--max-time 30** per curl call: prevents hung connections from blocking the pipeline.
- **Symlinks, not copies**: raw/ should symlink to the mirror directory. This preserves the mirror as the canonical copy and costs zero extra disk.
- **Filter image noise**: WordPress plugin directories (related-posts, postratings) produce hundreds of non-article images. Filter them before downloading.
- **Use execute_code for metadata**: 740 articles × regex parsing is instant in execute_code, but would flood context if done manually.
- **Programmatic page generation**: use write_file inside execute_code loops to generate 10+ sub-index pages in one pass. Don't write them one at a time manually.
- **Mirror won't render offline without CSS/JS**: HTML-only download produces broken layout.
  Fix it (Phase 6 below): download theme CSS/JS, fonts, plugin assets, strip `?ver=` query
  strings from HTML references, create symlinks for `@ver=` filenames.

### Phase 6: Local Mirror Repair (CSS/JS/Fonts for offline rendering)

After HTML + images are downloaded, the mirror will render broken in a browser because:
1. Theme CSS/JS (e.g. `/wp-content/themes/MyNisarg/`) was never downloaded
2. jQuery and other shared JS libs are missing
3. Plugin CSS/JS directories return 404 on static site mirrors (no directory listing)
4. Asset URLs in HTML carry `?ver=X.Y` query strings that break local file resolution
5. `wget` may save CSS files with `@ver=X.Y` in the filename

**① Identify missing assets.** Sample a few HTML files for all CSS/JS references:

```bash
grep -oh 'href="/[^"]*\.css"' articles/sample.html | sort -u
grep -oh 'src="/[^"]*\.js"' articles/sample.html | sort -u
```

**② Test which files actually exist on the live site** (individual files often return 200
even when directory listing returns 404):

```bash
for path in /wp-content/themes/.../style.css /wp-includes/js/jquery/jquery.min.js ...; do
  curl -sL -o /dev/null -w "%{http_code}" "https://example.com$path"
done
```

**③ Download missing files individually** (NOT with `wget -r` on directories — those
404 on static site mirrors). Use xargs+curl same as Phase 2:

```bash
cat /tmp/assets.txt | while read path; do
  url="${BASE}${path}"
  out="${MIRROR}/site${path}"
  echo "$url|$out"
done | xargs -P 15 -I {} sh -c '
  url=$(echo "{}" | cut -d"|" -f1)
  out=$(echo "{}" | cut -d"|" -f2)
  mkdir -p "$(dirname "$out")"
  curl -sL -o "$out" --max-time 15 "$url"
'
```

**④ Fix HTML references** — strip `?ver=X.Y` query strings from all CSS/JS references
so local files are found:

```bash
cd articles/
for f in *.html; do
  sed -i 's/\.css?ver=[^"]*/\.css/g; s/\.js?ver=[^"]*/\.js/g' "$f"
done
```

Also strip image query strings: `sed -i 's/\(src="[^"]*\.\(jpg\|png\|gif\|jpeg\)\)?[^"]*"/\1"/g'`

**⑤ Fix wget artifact filenames.** If earlier `wget` runs saved files as
`bootstrap.css@ver=6.2.css`, create clean-name symlinks:

```bash
for f in $(find . -name "*@ver=*" -type f); do
  clean=$(basename "$f" | sed 's/@ver=[0-9.]*\.css$//')
  ln -sf "$(basename "$f")" "$(dirname "$f")/$clean"
done
```

**⑥ Strip external tracking** (Google Analytics, AdSense, googletagmanager) which produce
console errors offline:

```bash
for f in *.html; do
  sed -i '/googletagmanager\|google-analytics\|adsbygoogle\|pagead2/d' "$f"
done
```

**⑦ Cloudflare protection cleanup (CRITICAL — blocks all interactivity).**
Static sites proxied through Cloudflare inject three classes of code that break
local rendering. Present on every Cloudflare-hosted static mirror:

- **onclick handlers**: Every link/button gets `onclick="if (!window.__cfRLUnblockHandlers)
  return false; ACTION"`. Since `__cfRLUnblockHandlers` is undefined locally, every
  click returns false and ALL links stop working.
- **Rocket Loader**: `<script src="/cdn-cgi/scripts/.../rocket-loader.min.js" defer>`
  defers JS via Cloudflare edge — useless locally, and often shares a line with `</body>`.
- **data-cf-modified attributes**: Cloudflare HTML-rewriting markers. Harmless but noise.

Fix:

```bash
for f in *.html; do
  # Strip the Cloudflare guard from onclick, keep the actual action
  sed -i 's/if (!window\.__cfRLUnblockHandlers) return false; //g' "$f"
  # Remove data-cf-modified attributes
  sed -i 's/ data-cf-modified-[a-f0-9]*-//g' "$f"
  # Remove rocket-loader and email-decode script tags
  sed -i '\|<script[^>]*rocket-loader[^>]*></script>|d' "$f"
  sed -i '\|<script[^>]*email-decode[^>]*></script>|d' "$f"
  # Fix Cloudflare-mangled type attributes
  sed -i 's/type="[a-f0-9]*-text\/javascript"/type="text\/javascript"/g' "$f"
done
```

⚠ **PITFALL: Deleting `</body>` along with rocket-loader.** The rocket-loader `<script>`
tag often shares a line with `</body>` — the line-deletion sed kills both. Restore:

```bash
for f in *.html; do
  if ! grep -q '</body>' "$f"; then
    sed -i 's|</html>|</body>\n</html>|' "$f"
  fi
done
```

**⑧ Strip Google Analytics from onclick handlers.** `pageTracker._trackPageview()` fails
locally and produces console noise:

```bash
for f in *.html; do
  sed -i 's/ onclick="pageTracker\._trackPageview([^)]*);"//g' "$f"
  sed -i 's/; pageTracker\._trackPageview([^)]*);//g' "$f"
done
```

**⑨ Absolute → relative path conversion (CRITICAL for file:// rendering).**
HTML files reference assets with absolute paths (e.g. `/wp-content/themes/.../style.css`).
When opened via `file://`, the browser resolves `/` to the filesystem root, not the
mirror directory. ALL asset references must become relative.

Since HTML files are in `articles/` and assets are siblings (`wp-content/`, `wp-includes/`,
`favicon.png`), the relative prefix from `articles/foo.html` is `../`:

```bash
for f in *.html; do
  sed -i '
    s|src="/wp-content/|src="../wp-content/|g
    s|src="/wp-includes/|src="../wp-includes/|g
    s|src="/cdn-cgi/|src="../cdn-cgi/|g
    s|src="/favicon\.png|src="../favicon.png|g
    s|href="/wp-content/|href="../wp-content/|g
    s|href="/wp-includes/|href="../wp-includes/|g
    s|href="/cdn-cgi/|href="../cdn-cgi/|g
    s|href="/favicon\.png|href="../favicon.png|g
  ' "$f"
done
```

Also convert inter-article links (same directory) and homepage:

```bash
for f in *.html; do
  sed -i 's|href="/articles/\([^"]*\.html\)|href="\1|g' "$f"
  sed -i 's|href="/"|href="../"|g' "$f"
done
```

Tag/category links (`/tag/xxx`, `/category/xxx`) can stay absolute — those pages
don't exist in the mirror and are harmless dead links.

**⑩-a. Missing Bootstrap/Font-Awesome fonts from static exports.**

GitHub Pages and other static site hosts often strip standard library fonts that
WordPress themes expect. Two common cases:

**Glyphicons (Bootstrap 3):** Used for navbar hamburger icon, form icons, etc.
The live site returns 404 for `wp-content/themes/.../fonts/glyphicons-*`.
Download from Bootstrap CDN (match the Bootstrap version the theme uses — check
`bootstrap.css` for `Bootstrap v3.X.X`):

```bash
FONTS_DIR=wp-content/themes/MyNisarg/fonts
mkdir -p "$FONTS_DIR"
BASE="https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/fonts"
for font in glyphicons-halflings-regular.eot svg ttf woff woff2; do
  curl -sL -o "$FONTS_DIR/$font" "$BASE/$font"
done
# Verify: files should be 18-108KB, NOT ~9KB (9KB = 404 error page)
```

**Font Awesome:** The theme's `font-awesome/css/font-awesome.min.css` references
`../fonts/fontawesome-webfont.*`. Test and download if missing:

```bash
curl -sI "https://example.com/wp-content/themes/MyNisarg/font-awesome/fonts/fontawesome-webfont.woff2"
# If 404, download from Font Awesome CDN (match version from CSS)
```

**⑩-b. Double-protocol prefix from sed.**

When converting `//fonts.googleapis.com` → `https://fonts.googleapis.com`, ensure
the sed only runs once. Running `s|//fonts.googleapis.com|https://fonts.googleapis.com|g`
on already-fixed HTML produces `https:https://fonts.googleapis.com`. Fix:

```bash
sed -i 's|https:https://fonts.googleapis.com|https://fonts.googleapis.com|g' *.html
```

Prevention: check before converting:
```bash
grep -l '//fonts.googleapis.com' *.html | wc -l  # only convert if >0
```
step ⑨, paths are relative from `articles/`):

```bash
cd articles/
grep -oP '(?:href|src)="\.\./(wp-content|wp-includes)[^"]*\.(css|js)"' sample.html | \
  sed 's/.*"//;s/"//' | while read rel; do
  [ -f "$rel" ] && echo "OK: $rel" || echo "MISSING: $rel"
done
```
