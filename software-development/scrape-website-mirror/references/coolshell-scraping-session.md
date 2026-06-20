# Case Study: Scraping coolshell.org (740 articles, 1354 images)

## Site Profile

- **URL**: https://coolshell.org (redirects to coolshell.cn on GitHub Pages)
- **Type**: Static WordPress export on GitHub Pages
- **Content**: 740 articles (2009-2023), ~1354 images
- **Structure**: `/articles/{id}.html` with shared CSS/JS at `/wp-content/`

## What Worked (Final Approach)

```bash
# 1. Collect URLs from article listing page
curl -sL 'https://coolshell.org/articles/' \
  | grep -oP 'href="/articles/\d+\.html"' \
  | sed 's|href="|https://coolshell.org|;s|"||' \
  | sort -u > /tmp/coolshell_urls.txt

# 2. Download with wget -p -k (the key flags)
wget -nc -p -k -E \
  --restrict-file-names=windows \
  -e robots=off \
  --wait=0.3 --random-wait \
  --limit-rate=1m \
  --directory-prefix=~/mirror \
  -i /tmp/coolshell_urls.txt
```

This produced 3157 files (228 MB): 742 HTML, 2405 CSS/JS, 2338 images.
Links auto-converted to relative. Files named with `@ver=` (wget replaces `?`).

## What Didn't Work (and Why)

### ❌ `wget --mirror -np`
`-np` (no-parent) blocks access to `/wp-content/` sibling directory.
Only downloaded 4 files — the listing page and its direct requisites.

### ❌ Individual file downloads + manual path fixing
Downloaded HTML with xargs+curl (fast), then tried to download CSS/JS/fonts
separately. Every fix introduced new edge cases:
- Relative path conversion was error-prone
- `@ver=` filename matching broke
- Glyphicon fonts not on GitHub Pages → 404
- Cloudflare protection blocked onclick handlers

### ❌ `wget -p` on 740 URLs with `--wait=0.2`
`-p` + individual URLs means wget checks ALL shared CSS/JS for EVERY page.
Even with `-nc`, the HEAD requests alone are a bottleneck. At `--wait=0.2`,
this would take hours.

## Cloudflare Cleanup

The site had Cloudflare protection. Three critical fixes:

1. **onclick blocking**: `if (!window.__cfRLUnblockHandlers) return false; ACTION` → `ACTION`
2. **Rocket-loader script**: Must be deleted, but WARNING: `</body>` tag is on the same line
3. **data-cf-modified attributes**: Remove `data-cf-modified-<hash>-` from all elements

### The `</body>` Trap (CRITICAL)

The rocket-loader script tag and `</body>` are on the same line:
```html
<script src="...rocket-loader.min.js" ... defer></script></body>
```

Using `sed '/rocket-loader/d'` deletes the ENTIRE line including `</body>`.
Result: 740 files missing `</body>`. Fix: after deletion, check and restore:
```bash
grep -q '</body>' "$f" || sed -i 's|</html>|</body>\n</html>|' "$f"
```

## Glyphicon Fonts

GitHub Pages static exports of WordPress don't include Bootstrap's glyphicon
fonts (they're standard Bootstrap assets, not theme-specific). The CSS still
references them at absolute URLs. Two-step fix:

1. Download from Bootstrap CDN:
```bash
mkdir -p wp-content/themes/MyNisarg/fonts
for f in glyphicons-halflings-regular.{eot,woff2,woff,ttf,svg}; do
  curl -sL -o "wp-content/themes/MyNisarg/fonts/$f" \
    "https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/fonts/$f"
done
```

2. Fix absolute font URLs in CSS:
```bash
sed -i 's|url(https://coolshell.org/...fonts/|url(../...fonts/|g' bootstrap.css@ver=*.css
```

## Final Stats

- **3157 files, 228 MB**
- **741 wiki symlinks** to `raw/articles/coolshell/`
- Page opens correctly at `file:///.../articles/914.html`
- External Google Fonts work when online; system fallback when offline
