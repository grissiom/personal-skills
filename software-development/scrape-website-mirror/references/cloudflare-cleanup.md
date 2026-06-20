# Cloudflare Cleanup for Offline Mirrors

When scraping sites behind Cloudflare, the downloaded HTML contains inline protection code that breaks local rendering. Apply these fixes to all articles.

## Detection

```bash
grep -l '__cfRLUnblockHandlers\|rocket-loader\|data-cf-modified' articles/*.html | wc -l
# If > 0, the site uses Cloudflare
```

## Cleanup Script

Run from the articles directory:

```bash
cd MIRROR/example.com/articles

for f in *.html; do
  # 1. Strip Cloudflare onclick blocking but keep the actual action
  #    "if (!window.__cfRLUnblockHandlers) return false; ACTION" -> "ACTION"
  sed -i 's/if (!window\.__cfRLUnblockHandlers) return false; //g' "$f"

  # 2. Remove data-cf-modified attributes
  sed -i 's/ data-cf-modified-[a-f0-9]*-//g' "$f"

  # 3. Remove rocket-loader script tags (CAUTION: may remove </body> if on same line!)
  sed -i '\|<script[^>]*rocket-loader[^>]*></script>|d' "$f"

  # 4. Remove email-decode script tags
  sed -i '\|<script[^>]*email-decode[^>]*></script>|d' "$f"

  # 5. Fix type attributes mangled by Cloudflare
  sed -i 's/type="[a-f0-9]*-text\/javascript"/type="text\/javascript"/g' "$f"

  # 6. Remove data-cfasync and data-cfbeacon
  sed -i 's/ data-cfasync="[^"]*"//g; s/ data-cfbeacon="[^"]*"//g' "$f"

  # 7. Strip Google Analytics tracking from onclick handlers
  sed -i 's/ onclick="pageTracker\._trackPageview([^)]*);"//g' "$f"
  sed -i 's/; pageTracker\._trackPageview([^)]*);//g' "$f"

  # 8. Fix missing </body> (step 3 may have deleted it)
  grep -q '</body>' "$f" || sed -i 's|</html>|</body>\n</html>|' "$f"
done
```

## Pitfall: </body> Deletion

The rocket-loader `<script>` tag often shares a line with `</body>`:

```html
<script src="...rocket-loader.min.js" defer></script></body>
```

The `sed` delete pattern removes the entire line, taking `</body>` with it. Step 8 restores it.

## Verification

```bash
# These should all return 0
grep -l '__cfRLUnblockHandlers' *.html | wc -l
grep -l 'data-cf-modified' *.html | wc -l
grep -l 'rocket-loader' *.html | wc -l

# Every file should have </body>
for f in *.html; do grep -q '</body>' "$f" || echo "MISSING: $f"; done
```
