#!/usr/bin/env python3
"""Save a WeChat article to the wiki with local images."""
import re, sys, urllib.request, os, hashlib

url = sys.argv[1]
wiki = os.path.expanduser("~/hermes/wiki/reading_notes")
os.makedirs(wiki, exist_ok=True)

# Fetch
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"
})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")

# Metadata
title = (re.search(r'<meta property="og:title" content="([^"]+)"', html) or
         re.search(r'<title>([^<]+)</title>', html))
title = title.group(1).strip() if title else "Unknown"
author = re.search(r'<meta property="og:article:author" content="([^"]+)"', html)
author = author.group(1).strip() if author else "Unknown"

# Slug from title
slug = re.sub(r'[^\w\s-]', '', title)[:40].strip().lower().replace(' ', '-') or "article"
slug = re.sub(r'-+', '-', slug)

# Resolve duplicate slugs
base_slug = slug
i = 1
while os.path.exists(os.path.join(wiki, f"{slug}.html")):
    slug = f"{base_slug}-{i}"
    i += 1

# Extract js_content
m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if not m:
    print("ERROR: js_content not found")
    sys.exit(1)
content = m.group(1)

# Fix images: data-src → src, decode entities
content = content.replace('data-src="', 'src="')
content = re.sub(r'src="//', 'src="https://', content)
content = content.replace('&amp;', '&')
content = re.sub(r' data-[a-z-]+="[^"]*"', '', content)

# Download images locally
img_dir = os.path.join(wiki, f"{slug}_files")
os.makedirs(img_dir, exist_ok=True)

def download_img(img_url):
    try:
        req = urllib.request.Request(img_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://mp.weixin.qq.com/"
        })
        data = urllib.request.urlopen(req, timeout=15).read()
        # Detect format from actual content, not URL
        content = data.lstrip()
        if content.startswith(b'\xff\xd8\xff'):
            suffix = 'jpg'
        elif content.startswith(b'\x89PNG'):
            suffix = 'png'
        elif content.startswith(b'GIF8'):
            suffix = 'gif'
        elif b'WEBP' in content[:12]:
            suffix = 'webp'
        elif b'<svg' in content[:20]:
            suffix = 'svg'
        else:
            # Fallback: try wx_fmt query param
            import re as _re
            m = _re.search(r'wx_fmt=(\w+)', img_url)
            suffix = m.group(1) if m else 'jpg'
        h = hashlib.md5(img_url.encode()).hexdigest()[:8]
        fname = f"{h}.{suffix}"
        fpath = os.path.join(img_dir, fname)
        with open(fpath, 'wb') as f:
            f.write(data)
        return f"{slug}_files/{fname}"
    except Exception as e:
        print(f"  WARN: image download failed: {e}")
        return None

imgs = re.findall(r'src="(https?://[^"]+)"', content)
print(f"Images: {len(imgs)}")
for img_url in imgs:
    local = download_img(img_url)
    if local:
        content = content.replace(f'src="{img_url}"', f'src="{local}"')

# Build standalone HTML
html_out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  body {{ max-width:680px; margin:0 auto; padding:24px 16px;
         font:16px/1.8 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
         color:#333; background:#fff; }}
  img {{ max-width:100%; height:auto; margin:12px 0; border-radius:4px; display:block; }}
  section {{ margin:0 0 16px; }}
  p {{ margin:0 0 16px; }}
  pre {{ background:#1e1e1e; color:#d4d4d4; padding:16px; border-radius:6px;
        overflow-x:auto; font:13px/1.5 "SF Mono","Fira Code",monospace; margin:12px 0; }}
  pre code {{ background:none; padding:0; font-size:inherit; }}
  .code-snippet__line-index {{ display:none; }}
  .code-snippet__selector-tag {{ color:#569cd6; }}
  .code-snippet__selector-attr {{ color:#9cdcfe; }}
  .code-snippet__selector-class {{ color:#4ec9b0; }}
  table {{ border-collapse:collapse; width:100%; margin:12px 0; font-size:14px; }}
  th,td {{ border:1px solid #ddd; padding:8px 12px; text-align:left; }}
  th {{ background:#f5f5f5; font-weight:600; }}
</style>
</head>
<body>
{content}
</body>
</html>"""

# Post-process HTML
html_out = html_out.replace('ounter(line', '')
html_out = re.sub(r'width="(\d+)px"', r'width="\1"', html_out)
# Fix WeChat code blocks: insert newlines between consecutive </code><code>
html_out = re.sub(r'(</code>)(<code>)', r'\1\n\2', html_out)

html_path = os.path.join(wiki, f"{slug}.html")
with open(html_path, 'w') as f:
    f.write(html_out)

print(f"OK|{html_path}|{title}|{author}|{slug}")
