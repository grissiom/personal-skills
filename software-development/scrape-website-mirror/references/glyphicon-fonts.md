# Missing Bootstrap Glyphicon Fonts (GitHub Pages Static Sites)

When a WordPress site is exported to GitHub Pages, Bootstrap 3 glyphicon fonts are typically NOT included in the static export. The CSS still references them, and wget leaves absolute URLs when it can't download the files (they 404).

## Symptom

Navbar hamburger icon missing, other glyphicon-based UI elements broken. Browser console shows 404 errors for:
- `glyphicons-halflings-regular.woff2`
- `glyphicons-halflings-regular.woff`
- `glyphicons-halflings-regular.ttf`
- `glyphicons-halflings-regular.eot`
- `glyphicons-halflings-regular.svg`

And the CSS has absolute URLs like:
```css
@font-face {
  font-family: 'glyphicons halflings';
  src: url(https://example.com/wp-content/themes/ThemeName/fonts/glyphicons-halflings-regular.eot);
}
```

## Fix

### 1. Download fonts from Bootstrap CDN

```bash
cd MIRROR/example.com
mkdir -p wp-content/themes/THEME_NAME/fonts
cd wp-content/themes/THEME_NAME/fonts

for font in glyphicons-halflings-regular.eot woff2 woff ttf svg; do
  curl -sL -o "$font" \
    "https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/fonts/$font"
  echo "  $font: $(wc -c < $font) bytes"
done
# Expected sizes: eot=20127, woff2=18028, woff=23424, ttf=45404, svg=108738
# If files are ~9KB, they're 404 error pages — the CDN URL is wrong
```

### 2. Fix CSS font URLs

```bash
BOOTSTRAP_CSS=$(ls wp-content/themes/*/css/bootstrap.css@ver=*.css | head -1)
sed -i 's|url(https://EXAMPLE.COM/wp-content/themes/[^/]*/fonts/|url(../wp-content/themes/THEME_NAME/fonts/|g' "$BOOTSTRAP_CSS"
```

Replace `EXAMPLE.COM` and `THEME_NAME` with actual values. The `../` path resolves correctly from `css/bootstrap.css` up to the theme root, then into `fonts/`.

### 3. Verify

```bash
grep -o 'url([^)]*glyphicons[^)]*)' "$BOOTSTRAP_CSS"
# Should show relative paths like: url(../wp-content/themes/MyNisarg/fonts/glyphicons-halflings-regular.woff2)
```

## Why This Happens

GitHub Pages serves a static export of the WordPress site. The export includes theme CSS and plugin files but typically excludes Bootstrap's standard distribution fonts since they're not custom assets — they ship with every Bootstrap install. The live WordPress site served them from `wp-content/themes/THEME/fonts/` but the static export omitted them.
