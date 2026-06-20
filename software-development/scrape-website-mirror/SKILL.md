---
name: scrape-website-mirror
description: "Download a complete offline mirror of a website — HTML, CSS, JS, images, fonts — with wget."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
---

# Scrape Website to Offline Mirror

Download a complete, self-contained offline copy of a website. All links converted to relative paths, all page requisites (CSS, JS, images, fonts) included. Open any page with `file://` in a browser and it renders correctly.

All mirrors go under `~/mirror/<domain>/` — a flat, unified directory for all scraped sites (coolshell.org, 0xkato.xyz, anthropic.com, etc.).

## When to Use

- Archiving a blog or documentation site for offline reading
- **Saving articles for wiki integration**: ⚠️ This is the most common use case. You MUST load `references/wiki-integration.md` before proceeding. The wiki uses a two-track approach: (1) raw HTML mirror preserved as-is, (2) hand-written synthesis page. Do NOT convert articles to markdown — the wiki page is a study note, not a mirror.
- Any time you need a complete local copy of a website

## Core Command

```bash
wget -nc -p -k -E \
  --restrict-file-names=windows \
  -e robots=off \
  --wait=0.3 --random-wait \
  --limit-rate=1m \
  --directory-prefix=MIRROR_DIR \
  -i urls.txt
```

### Flag explanation

| Flag | Purpose |
|------|---------|
| `-nc` | No-clobber: skip already-downloaded files (safe to resume) |
| `-p` | **Page requisites**: download ALL CSS, JS, images, fonts each page needs |
| `-k` | **Convert links**: rewrite all URLs to relative paths for local viewing |
| `-E` | Adjust extensions: add `.html` to pages that lack it |
| `--restrict-file-names=windows` | Safe filenames: replace `?` with `@` etc. |
| `-e robots=off` | Ignore robots.txt |
| `--wait=0.3 --random-wait` | Be polite to the server |
| `--limit-rate=1m` | Cap bandwidth at 1 MB/s |
| `-i urls.txt` | Read URLs from file (one per line) |

## Workflow

### Step 1: Collect article URLs

For WordPress/blog sites, find the article listing page (e.g., `/articles/`) and extract all links:

```bash
curl -sL 'https://example.com/articles/' \
  | grep -oP 'href="/articles/\d+\.html"' \
  | sed 's|href="|https://example.com|;s|"||' \
  | sort -u > /tmp/urls.txt
```

### Step 2: Run wget with `-p -k`

All mirrors live under `~/mirror/<domain>/`. This is a flat, unified directory — do not scatter mirrors elsewhere.

```bash
mkdir -p ~/mirror/example.com
wget -nc -p -k -E \
  --restrict-file-names=windows \
  -e robots=off \
  --wait=0.3 --random-wait \
  --directory-prefix=~/mirror/example.com \
  -i /tmp/urls.txt
```

The `-p` flag downloads ALL requisites for each page. The `-k` flag converts all absolute URLs to relative. Combined, this produces a fully self-contained mirror.

### Step 3: Handle Cloudflare protection (if present)

If the site uses Cloudflare, inline JS may block links. Check for and clean:

```bash
cd ~/mirror/example.com/articles
for f in *.html; do
  # Remove Cloudflare onclick blocking
  sed -i 's/if (!window\.__cfRLUnblockHandlers) return false; //g' "$f"
  # Remove rocket-loader scripts — WARNING: </body> may be on same line!
  sed -i '\|<script[^>]*rocket-loader[^>]*></script>|d' "$f"
  # CRITICAL: Fix body tag if deleted with rocket-loader (they share a line)
  grep -q '</body>' "$f" || sed -i 's|</html>|</body>\n</html>|' "$f"
  # Remove Cloudflare data attributes
  sed -i 's/ data-cf-modified-[a-f0-9]*-//g' "$f"
done
```

### Step 4: Fix missing Bootstrap fonts (GitHub Pages static sites)

GitHub Pages exports of WordPress sites often lack Bootstrap glyphicon fonts. Download from CDN:

```bash
cd ~/mirror/example.com
mkdir -p wp-content/themes/THEME_NAME/fonts
for font in glyphicons-halflings-regular.eot woff2 woff ttf svg; do
  curl -sL -o "wp-content/themes/THEME_NAME/fonts/$font" \
    "https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/fonts/$font"
done

# Fix font URLs in CSS (wget may leave them absolute if they 404'd)
BOOTSTRAP_CSS=$(ls wp-content/themes/*/css/bootstrap.css@ver=*.css | head -1)
sed -i 's|url(https://example.com/wp-content/themes/[^/]*/fonts/|url(../wp-content/themes/...fonts/|g' "$BOOTSTRAP_CSS"
```

Adjust the `sed` pattern to match the actual domain and theme path.

## Common Pitfalls

### DO NOT convert articles to markdown for the wiki

The wiki uses hand-written synthesis pages, not markdown conversions. When the task says "save to wiki", this means: (1) download raw HTML mirror with wget, (2) write a synthesis page by hand. Do NOT run an HTML→MD converter and save its output as the wiki page. **Always load `references/wiki-integration.md` first** when wiki is involved.

### DO NOT use `--mirror` with `-np` for WordPress sites

`--mirror` implies `-r` (recursive). With `-np` (no-parent), wget will NOT download assets in sibling directories like `/wp-content/`. This silently breaks CSS/JS/images.

**Wrong**: `wget --mirror -np https://example.com/articles/`
**Right**: `wget -nc -p -k -E -i urls.txt`

### DO NOT download individual files piecemeal

Manually downloading CSS, then JS, then images, then fixing paths... each step introduces new edge cases. Let wget `-p -k` handle everything atomically.

### DO NOT strip `?ver=` query strings yourself

wget saves files with `@` replacing `?` (e.g., `style.css?ver=6.2` → `style.css@ver=6.2.css`). It also updates all HTML references to match. If you manually strip query strings, the references won't match the filenames.

### Google Fonts are OK as external

`https://fonts.googleapis.com/...` references will work when the user is online. The theme's CSS already has system font fallbacks (`font-family: 'Source Sans Pro', sans-serif`).

## Verification Checklist

After downloading, verify:

```bash
cd ~/mirror/example.com

# 1. All CSS/JS references resolve
grep -oP '(src|href)="\.\./[^"]+"' articles/sample.html | while read line; do
  path=$(echo "$line" | sed 's/.*="//;s/"//' | sed 's|^\.\./||')
  [ -f "$path" ] || echo "MISSING: $path"
done

# 2. No remaining absolute local paths (should all be relative after -k)
grep -c 'src="/' articles/sample.html  # should be 0
grep -c 'href="/wp-content' articles/sample.html  # should be 0

# 3. Glyphicon fonts present
find wp-content/themes/*/fonts -name "glyphicons*" | wc -l  # should be 5
```

## Wiki Integration

When scraping for a personal wiki: after the mirror is downloaded,
**load `llm-wiki`** and follow its ingest procedures — read the article,
write a concept synthesis page to `<wiki>/concepts/`, and update
`index.md`, `README.md`, and `log.md`. The mirror at `~/mirror/` is the
immutable raw source; the concept page is the wiki's synthesis.

## Known Limitations

- JavaScript-heavy SPAs won't work offline (wget downloads static HTML, not JS-rendered content)
- Cloudflare-protected email addresses remain obfuscated
- Comment systems and dynamic features won't work
- Google Analytics / tracking scripts should be removed (they only cause console errors)

## Reference

- `references/coolshell-scraping-session.md` — Full worked example: scraping 740 articles from coolshell.org (GitHub Pages WordPress export), including Cloudflare cleanup, glyphicon font fix, and wiki integration.
- GitHub Pages static WordPress exports often lack Bootstrap glyphicon fonts — see `references/glyphicon-fonts.md` for the fix

## Reference Files

- `references/cloudflare-cleanup.md` — Exact sed patterns for stripping Cloudflare protection code
- `references/glyphicon-fonts.md` — Fix missing Bootstrap 3 glyphicon fonts on GitHub Pages mirrors
- `references/wiki-integration.md` — Single-article workflow: mirror preservation + hand-written wiki synthesis page (NOT markdown conversion), with index update steps
