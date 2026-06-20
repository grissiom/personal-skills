# WeChat Article Extraction (SUPERSEDED)

> **This reference is superseded.** The workflow described here (regex text extraction → .md) has been replaced by the `weixin-article-to-wiki` skill, which produces self-contained `.html` files with locally-downloaded images and proper CSS styling.

For WeChat article saving, load `weixin-article-to-wiki` and run:

```bash
python3 /tmp/save_wx.py "<URL>"
```

The old `.md` extraction approach is preserved below for historical reference only — it produces lossy plain text with no images, code formatting, or styling.

---

## Historical: Markdown Extraction (deprecated)

WeChat articles render content client-side via JavaScript in a `<div id="js_content">` element. A simple curl gets the HTML but not the rendered text.

### Step 1: Download HTML

```bash
curl -sL --max-time 30 \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  "ARTICLE_URL" \
  -o /tmp/weixin_article.html
```

### Step 2: Extract js_content

```python
import re

with open('/tmp/weixin_article.html', 'r') as f:
    html = f.read()

m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
if m:
    content = m.group(1)
    text = re.sub(r'<[^>]+>', '', content)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&\w+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
```

### Pitfalls (historical, mostly resolved by the new HTML pipeline)

- WeChat HTML is large (~4MB) due to inline JS
- The regex `</div>\s*<script` is safe because WeChat always follows `js_content` with a `<script` tag
- NEVER use `python3 -c "..."` for scripts with Chinese smart quotes — use `write_file` or heredocs instead
