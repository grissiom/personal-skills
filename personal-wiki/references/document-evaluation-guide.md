# Document Evaluation Guide (Real Session Example)

This reference captures the evaluation workflow from a real wiki initialization session, as a concrete template to follow or adapt.

## Initial Assessment Commands

```bash
# File type distribution (root level)
find . -maxdepth 1 -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# File type distribution (all subdirs)
find . -type f | sed 's/.*\.//' | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn | head -30

# Each directory: size + file count
for d in */; do
  count=$(find "$d" -type f | wc -l)
  size=$(du -sh "$d" | cut -f1)
  echo "$size  $count  $d"
done | sort -k2 -rn

# Empty directories
find . -type d -empty

# Year range per directory (identifies stale content)
for d in */; do
  oldest=$(find "$d" -type f -printf '%TY\n' 2>/dev/null | sort | head -1)
  newest=$(find "$d" -type f -printf '%TY\n' 2>/dev/null | sort -rn | head -1)
  echo "$oldest - $newest  $d"
done | sort -k1

# Check for personal/private files
find . -iname '*简历*' -o -iname '*体检*' -o -iname '*公积金*' \
       -o -iname '*合同*' -o -iname '*协议*' -o -iname '*身份证*' \
       -o -iname '*护照*' 2>/dev/null | head -10

# Check for build artifacts
find . -name '*.o' -type f | wc -l
find . -name '*.swp' -type f | wc -l
find . -name 'Thumbs.db' -type f | wc -l
find . -name '.git' -type d | wc -l
```

## Exclusion Categories (from real session)

### Category 1: Personal / Private
- Resumes, medical reports, contracts, property deeds
- Financial records (housing fund, invoices)
- Personal photos and videos
- Family/personal correspondence

**Real examples**: `Gri/` (产权协议, 体检报告, 简历, 公积金), `HJH/` (七夕纪念.mp4, personal travel)

### Category 2: Build Artifacts & System Junk
- `.o` (object files, 124 in this session)
- `.swp` (Vim swap, 8)
- `.tmp` (temp, 2)
- `Thumbs.db` (Windows thumbnail cache, 10)
- `.git` directories (1)

### Category 3: Superseded / EOL Technology Docs
| Technology | Era | Modern Replacement | Verdict |
|-----------|-----|-------------------|---------|
| Qt 4 books | 2006-2008 | Qt 6.x | Exclude |
| PyQt4 documentation | ~2010-2015 | PyQt5/PyQt6 | Exclude |
| PyQwt (plotting lib) | 2010 (last update) | PyQtGraph, Matplotlib | Exclude |
| PIL (Python Imaging Lib) | pre-2011 | Pillow | Exclude |
| Jenkins website dump | stale archive | — | Exclude |
| iOS beginner guide | 2015 | SwiftUI era | Exclude |

### Category 4: Keep (Timeless / Stable)
- **Standards**: RFCs, encoding tables (GB2312, Unicode), Intel HEX format
- **Classic books**: The Mythical Man-Month, Code Complete, Introduction to Algorithms, Structure and Interpretation of Programs
- **Design principles**: Designing Interactions, Don't Make Me Think
- **Open source philosophy**: Cathedral & Bazaar, Free Culture
- **Language learning**: English, GRE — these don't age
- **Domain references**: Embedded RTOS principles (μC/OS-II), character encoding tables, UML

## Key Decision Framework

When evaluating a directory, ask:

1. **Is it personal?** → Exclude (medical, financial, resume, private photos/videos)
2. **Is it a build artifact?** → Exclude (`.o`, `.swp`, `.tmp`, `Thumbs.db`)
3. **Is the technology actively maintained?** → No → **Is the content still relevant as reference?** → No → Exclude
4. **Does it teach deprecated patterns?** → Yes → Exclude (someone following these docs will go down the wrong path)
5. **Is it a stable standard / timeless work?** → Keep

## Handling Read-Only Source Filesystem

When the source media is mounted read-only (`mount | grep ro`):

- Symlinks are on the writable filesystem, targets are on the ro mount
- `rm symlink_at_writable_path` works (removing the link, not the target)
- `cd` into the symlink path **follows** into the ro filesystem — operations then fail
- Always use **absolute path** to the symlink when removing it
- To exclude sub-items: remove the parent symlink, recreate the parent as a real writable directory, and symlink each child individually
