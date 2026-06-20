# Batch Wiki Repair Methodology

Full procedure for diagnosing and fixing a degraded wiki. Use when the user
says "完善 wiki", "improve wiki", "fix wiki", or when initial orientation
reveals missing index, widespread orphans, or many stubs.

## Phase 1: Orientation + Diagnosis

Always start with a full lint. The script below handles wikilink resolution
correctly (both dir-prefixed and bare-name links) and reports all key metrics.

```python
# Proven lint script — use with execute_code
import os, re, yaml
from collections import defaultdict

WIKI = "<wiki_path>"
PAGE_DIRS = ["entities", "concepts", "comparisons", "queries"]

all_pages = {}
all_links = defaultdict(set)
status_dist = defaultdict(int)

for d in PAGE_DIRS:
    dirpath = os.path.join(WIKI, d)
    if not os.path.isdir(dirpath):
        continue
    for fname in sorted(os.listdir(dirpath)):
        if not fname.endswith('.md'):
            continue
        page_id = f"{d}/{fname}"
        filepath = os.path.join(dirpath, fname)
        with open(filepath, 'r') as f:
            text = f.read()
        fm = {}
        body = text
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except:
                    pass
                body = parts[2]
        links = set(re.findall(r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]', body))
        all_pages[page_id] = True
        all_links[page_id] = links
        status_dist[fm.get('status', '?')] += 1

def resolve(link):
    """Resolve wikilink to page_id. Handles both dir-prefixed and bare names."""
    # Try with dir prefix first (e.g., "concepts/linux-kernel")
    for d in PAGE_DIRS:
        for suffix in ['.md', '']:
            test = f"{d}/{link}{suffix}"
            if test in all_pages:
                return test
    # Try as bare name (e.g., "linux-kernel")
    for d in PAGE_DIRS:
        if f"{d}/{link}.md" in all_pages:
            return f"{d}/{link}.md"
    # Try as-is
    if link + '.md' in all_pages:
        return link + '.md'
    if link in all_pages:
        return link
    return None

incoming = defaultdict(set)
broken = []
for from_p, links in all_links.items():
    for link in links:
        target = resolve(link)
        if target:
            incoming[target].add(from_p)
        else:
            broken.append((from_p, link))

orphans = [p for p in all_pages if p not in incoming or len(incoming[p]) == 0]
linked_count = len(all_pages) - len(orphans)
no_out = [p for p in all_pages if len(all_links[p]) == 0]

print(f"Total pages: {len(all_pages)}")
print(f"Linked: {linked_count} | Orphans: {len(orphans)}")
print(f"No outbound links: {len(no_out)}")
print(f"Broken wikilinks: {len(broken)}")
print(f"Status: {dict(status_dist)}")
```

## Phase 2: Rebuild Missing Infrastructure

If `index.md` or `log.md` are missing (orientation reads fail):

### Rebuild index.md

```python
# Extract all page titles and generate index
for d in PAGE_DIRS:
    dirpath = os.path.join(WIKI, d)
    for fname in sorted(os.listdir(dirpath)):
        if not fname.endswith('.md'):
            continue
        slug = f"{d}/{fname.replace('.md', '')}"
        # Parse frontmatter for title, status, tags
        # Generate: [[dir/filename]] — summary
```

Format the index with sections for Entities, Concepts, Comparisons, Queries.
Include total page count and last-updated date. Each entry: `[[dir/slug]] — summary`.

### Rebuild log.md

Start fresh with a creation entry documenting the rebuild. Use the template from SKILL.md.

## Phase 3: Fix Broken Links

1. Fix each broken wikilink: either correct the target or remove it
2. Common causes: wrong directory (concepts/can-protocols → comparisons/can-protocols),
   raw/ path used as wikilink, deleted pages

## Phase 4: Add Cross-Links

### Empty "相关页面" sections

Many pages from older sessions have `## 相关页面` with no links. Pattern to detect:

```python
# Check for empty related sections
m = re.search(r'## 相关页面\n\n(.*?)(?:\n##|\Z)', text, re.DOTALL)
if m and not re.findall(r'\[\[', m.group(1)):
    # Empty — needs filling
```

To fix: replace the empty section with actual links. Use `re.sub` to match the
full section including its content:

```python
text = re.sub(
    r'## 相关页面\n\n.*?(?=\n## |\Z)',
    new_section.rstrip(),
    text, flags=re.DOTALL
)
```

### Assigning cross-links

Strategy: use shared tags to suggest related pages, then apply manual overrides
for known clusters. Cap at 5 links per page. Always make links bidirectional.

```python
# Tag-based clustering
clusters = {}
for slug, tags in slug_to_tags.items():
    for other_slug, other_tags in slug_to_tags.items():
        if slug == other_slug:
            continue
        if set(tags) & set(other_tags):
            clusters.setdefault(slug, set()).add(other_slug)
```

## Phase 5: Upgrade Misclassified Stubs

Threshold: `status: stub` + >500 chars of body content (after stripping `相关页面`
section and whitespace) → `status: growing`.

```python
body_clean = re.sub(r'\s+', ' ', body).strip()
body_clean = re.sub(r'## 相关页面.*$', '', body_clean, flags=re.DOTALL).strip()
if len(body_clean) > 500:
    text = text.replace('status: stub', 'status: growing', 1)
```

## Phase 6: Expand Hot Stubs

"Hot stubs" = pages with incoming links but thin content. These are disappointing —
people navigate to them and find nothing.

1. Sort stubs by incoming link count (descending)
2. For the top 5-10, expand with definitions, key facts tables, and relationships
3. Mark `confidence: medium` when synthesizing from general knowledge
4. Update `updated` date in frontmatter

## Phase 7: Update Log

After all repairs, append a single comprehensive log entry:

```markdown
## [YYYY-MM-DD] lint+update | 大规模 wiki 完善
- 发现: ... (initial state)
- 操作: ... (every fix applied, with counts)
- 结果: ... (final metrics)
```

## Common Pitfalls

- **Wikilink resolution on first pass**: the resolve() function must try dir-prefixed
  links BEFORE bare-name links, otherwise `[[concepts/cpu-architecture]]` gets
  misinterpreted as a bare name `concepts/cpu-architecture` and a second `concepts/`
  prefix is prepended, creating `concepts/concepts/cpu-architecture`.
- **"相关页面" header ≠ actual links**: don't skip pages just because the header
  exists — check that there are actual `[[wikilinks]]` inside.
- **Don't patch 70 files individually**: use execute_code for bulk operations.
  Reading/writing files in Python is much faster than individual tool calls.
- **Bidirectional links**: when adding A → B, also ensure B → A if B's related
  section has room (cap at 5).
