# Evaluating a Document Collection for Wiki Ingestion

Example from the 2026-06-11 session: 58K files, 24GB collection at `/media/grissiom/Docs/`.

## Scan Commands

```bash
# Top directories by file count
for d in */; do
  name=$(basename "$d")
  count=$(find "$d" -type f | wc -l)
  size=$(du -sh "$d" | cut -f1)
  echo "$size  $count  $name"
done | sort -k2 -rn

# File type distribution (all depths)
find . -type f | sed 's/.*\.//' | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn

# Year distribution of content
for d in */; do
  oldest=$(find "$d" -type f -printf '%TY\n' | sort | head -1)
  newest=$(find "$d" -type f -printf '%TY\n' | sort -rn | head -1)
  echo "$oldest - $newest  $d"
done | sort -k1
```

## Exclusion Categories Identified

| Category | Examples | Reason |
|----------|----------|--------|
| Personal files | Resumes, medical reports, contracts, family photos/videos | Privacy, not knowledge |
| Outdated tech | Jenkins CI docs (2017-2020), Qt4 (2006-2008), PIL (→Pillow 2011), iOS guides (2015) | Teach wrong/obsolete APIs |
| Build artifacts | `*.o`, `*.swp`, `*.tmp`, `Thumbs.db`, `.git/` | Noise, zero knowledge value |

## Symlink Splitting Pattern

When you need to exclude sub-items inside a symlinked directory:

```python
import os
src = '/source/path'
dst = '/wiki/raw/dir'
exclude = {'ItemA', 'ItemB'}
for item in os.listdir(src):
    if item not in exclude:
        os.symlink(os.path.join(src, item), os.path.join(dst, item))
```

This avoids the "all-or-nothing" problem of directory-level symlinks.
