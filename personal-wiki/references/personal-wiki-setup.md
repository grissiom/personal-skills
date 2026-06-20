---
name: personal-wiki-setup
description: Initialize and maintain a personal knowledge management wiki from existing local document collections. Symlink-based, no copies.
category: productivity
tags: [wiki, knowledge-management, documentation, organization, symlinks]
triggers:
  - "user wants to set up / initialize a personal wiki"
  - "user has local documents they want to organize into a knowledge base"
  - "user asks to create a wiki from ~/Docs or similar directory"
  - "user mentions SCHEMA.md, raw/, entities/, concepts/ wiki structure"
  - "user wants to fill / populate / seed / restructure wiki content"
  - "user wants to create concept pages, entity pages, or comparison pages"
  - "user asks about '重构' (restructuring) a large document collection into wiki pages"
  - "user wants to read / summarize / take notes on a book in the collection"
---

# Personal Wiki Setup

Set up a personal knowledge management (PKM) wiki from an existing local document collection. Uses **symbolic links** — never copies — to avoid duplicating data.

## Directory Structure

```
~/hermes/wiki/
├── SCHEMA.md          ← schema & conventions
├── README.md          ← homepage / navigation index
├── raw/               ← symlinks to original documents
│   └── .rawlenses     ← ignore-pattern file for filtering guidance
├── entities/          ← people, organizations, products, devices
├── concepts/          ← theories, terms, methodologies
├── comparisons/       ← technology / solution comparisons
├── reading_notes/     ← external article archives (WeChat, blogs, papers)
└── queries/           ← open questions, TODOs, research leads
```

## Steps

### 1. Create SCHEMA.md

Define the wiki structure, naming conventions, and frontmatter spec:

**Naming**: `kebab-case` for English, zh/en variants in same directory via `zh.md`/`en.md`. Disambiguate with brackets: `spring[coil].md`, `spring[season].md`.

**Frontmatter**:
```yaml
---
title: Page Title
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: raw/path or external URL
status: draft | stub | growing | mature
---
```

### 2. Create Directory Tree

```bash
mkdir -p ~/hermes/wiki/{raw,entities,concepts,comparisons,reading_notes,queries}
```

### 3. Link All Source Documents (raw/)

Use **symlinks** (`ln -s`), never `cp`:

```bash
cd ~/hermes/wiki/raw
for item in /media/grissiom/Docs/*; do
  ln -sf "$item" "$(basename "$item")"
done
```

### 4. Evaluate What to Exclude

Walk through every directory and file with the user. Use these criteria:

| Criterion | Exclude? | Example |
|-----------|----------|---------|
| Personal/private files (resumes, medical, contracts, photos) | **Yes** | `Gri/`, `HJH/` |
| Build artifacts (.o, .swp, .tmp, Thumbs.db, .git) | **Yes** | Scattered in BSP source dirs |
| Superseded/outdated tech docs (EOL libraries, old framework versions) | **Yes** | Qt 4, PyQwt, PIL, Jenkins docs |
| Classic/timeless content (standards, design principles, algorithms) | **No** | RFCs, encoding tables, classic CS books |
| Current-tech documentation | **No** | Active libraries, current OS docs |
| Books and long-form content | **No** | Even old books if principles are stable |

#### Assessing Tech Version Status

When deciding if technical documentation is outdated, use this systematic checklist:

1. **Check date range**: `find dir -type f -printf '%TY\\n' 2>/dev/null | sort | head -1` gives oldest content year
2. **Check current version**: Search whether the project/library is still actively maintained
3. **Apply the "teach test"**: If someone followed these docs today, would they learn current best practices or deprecated patterns?
4. **Version gap heuristic**:
   - If the project is **2+ major versions ahead** of the docs, → **likely exclude** (Qt 4 → Qt 6, PyQt4 → PyQt6)
   - If the project was **superseded by a fork/rename**, → **exclude** (PIL → Pillow in 2010)
   - If the project is **dead** (no release in 5+ years), → **likely exclude** (PyQwt, last update 2010)
   - If the content is about **stable standards** (USB 2.0 spec, RFC, encoding table), → **keep regardless of age**
   - If the content is **~15+ year old beginner tutorials** for a fast-evolving platform (iOS, Android), → **exclude** |

### 5. Granular Exclusion (Key Technique)

When you need to exclude specific **subdirectories** inside a source directory:

**DON'T** symlink the parent directory as a whole. Instead:
1. Remove the parent symlink: `rm /path/to/wiki/raw/parent`
2. `mkdir /path/to/wiki/raw/parent`
3. Create individual symlinks for each child, skipping excluded ones:

```python
import os
src = '/media/$USER/Docs/parent'
dst = os.path.expanduser('~/hermes/wiki/raw/parent')
exclude = {'OutdatedDir1', 'OutdatedDir2'}
for item in os.listdir(src):
    if item not in exclude:
        os.symlink(os.path.join(src, item), os.path.join(dst, item))
```

### 6. Create .rawlenses

In `raw/`, create a `.rawlenses` file documenting:

```yaml
# raw/ 过滤配置
IGNORE_PATTERNS:
  - '*.o'
  - '*.swp'
  - '*.tmp'
  - 'Thumbs.db'
  - '.git'
  - '.DS_Store'

EXCLUDED_DIRS:
  - DirectoryA   # reason
  - DirectoryB   # reason
```

### 7. Create README.md Homepage

Include:
- Navigation table linking all wiki sections
- Quick-entry links organized by domain
- Exclusion table with reasons
- Usage instructions

## Pitfalls

- **Read-only filesystem**: If the source is on a read-only mount (`ro` in `mount` output), `rm` on symlinks inside the traversed path will fail. Always use the **absolute path** to the symlink itself (e.g., `/home/user/wiki/raw/dir`) not a path that follows the symlink into the ro mount.
- **Special characters in filenames**: Chinese characters, `()`, `'`, `~`, spaces in filenames cause `ln -s` via shell to fail. Use `os.symlink()` from Python or `shlex.quote()` to escape properly.
- **Symlink as directory traversal**: `cd raw/dir` follows the symlink into the source. Operations on the target (`rm`, `mkdir`) affect the read-only source. Work outside the symlink path.
- **Over-exclusion**: Distinguish "old but still useful" (stable standards, design principles) from "superseded and misleading" (EOL library tutorials). The former stays, the latter goes.
- **Memory vs. skill**: User preferences about wiki structure and exclusion criteria go into this skill, not just memory. Memory captures state; skills capture method.
- **Overlap**: This skill overlaps with `productivity/personal-knowledge-wiki`. Both cover wiki setup and content filling. This skill (`personal-wiki-setup`) is more detailed with scripts, templates, and specific code. The curator may consolidate at scale.
- **Sibling subagent conflicts**: When doing batch direct filling via parallel `write_file` calls in the main session, sibling subagents (Hermes may spawn them automatically for I/O-heavy tasks) can write to the same stub files concurrently. This produces `_warning: file was modified by sibling subagent` messages. Files usually still get written correctly, but verify content with a spot-check after each batch. To avoid conflicts entirely, prefer sequential `write_file` calls (3-4 per turn in order) rather than parallel ones when the stubs are empty placeholders — the write time is negligible since there's no prior content to read.

## Related Skills

- `productivity/personal-knowledge-wiki` — Overlapping skill covering similar territory with less process detail and more concise reference templates. The background curator handles consolidation.

## Batch Parallel Reading via delegate_task

For populating a wiki with book notes from the collection, use `delegate_task` to read multiple books in **parallel** — this is much faster than reading one at a time:

```python
# In the parent session:
delegate_task(tasks=[
    {"context": "PDF at /path/book1.pdf\nExtract TOC and core arguments",
     "goal": "Return chapter list and 3-5 core theses",
     "toolsets": ["terminal"]},
    {"context": "PDF at /path/book2.pdf\n...",
     "goal": "...", 
     "toolsets": ["terminal"]},
])
```

Each subagent independently calls `pdfinfo + pdftotext`, reads the key chapters, and returns a structured summary. The parent then:
1. Reviews the summaries
2. Creates wiki pages from them
3. Links them to the existing knowledge map

This pattern works for up to 3 simultaneous reads (per Hermes delegation limits). For more, batch in groups of 3.

### epub Book Extraction

For `.epub` files (not PDFs), extract the TOC directly via Python's `zipfile`:

```python
import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile('book.epub') as z:
    ncx = z.read('toc.ncx')
    root = ET.fromstring(ncx)
    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    for nav in root.findall('.//ncx:navPoint', ns):
        label = nav.find('.//ncx:navLabel/ncx:text', ns)
        if label is not None and label.text:
            print(label.text.strip())
```

This gives you the full TOC without needing any external tool. For content extraction from epub, you may need to find and read the `.xhtml` files inside the archive directly.

## Tag Index Auto-Generation

Run this from `execute_code` after creating/updating pages to generate a cross-reference tag index at `concepts/tag-index.md`:

```python
import os, re

tag_index = {}
for root, dirs, files in os.walk('/path/to/wiki'):
    if '.git' in root: continue
    for f in files:
        if not f.endswith('.md') or 'raw/' in root: continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, '/path/to/wiki')
        with open(path) as fh:
            content = fh.read()
        title_m = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else rel
        tags_m = re.search(r'^tags:\s*\[(.+)\]$', content, re.MULTILINE)
        if tags_m:
            for t in [x.strip() for x in tags_m.group(1).split(',')]:
                tag_index.setdefault(t, []).append((rel, title))

# Write tag-index.md with a markdown table of tag → pages
```

Load `scripts/generate-tag-index.py` (via `skill_view(name="personal-wiki-setup", file_path="scripts/generate-tag-index.py")`) and run it with the wiki path when the tag index needs refreshing (e.g., after adding 5+ pages).

## Glossary Pages

The wiki supports **glossary pages** (`concepts/glossary.md`) as an additional page type alongside the four standard ones. A glossary is useful when the document collection covers a domain with extensive abbreviations (automotive, aerospace, software).

Glossary structure:
```markdown
---
title: 术语表 (Glossary)
tags: [导航, 术语, 索引]
created: YYYY-MM-DD
status: growing
---

## Domain Name

| 缩写 | 全称 | 说明 |
|------|------|------|
| ABC | Alpha Beta Charlie | Explanation of the term |
```

Group by domain with subheadings. Link to relevant wiki pages for detailed coverage.

## Content Filling (Post-Setup)

After the exclusion phase, seed the wiki with index pages. Use a **layered approach** — largest directories first, then medium, then cross-cutting comparisons.

### Auto-Iteration / "请继续" Pattern

When the user says "请继续", "please continue", "自动迭代 X 轮", or keeps asking for more, use a **batch-rounds** strategy:

1. **Plan a batch of ~10 rounds** with the `todo` tool. Each round is one meaningful deliverable (a reading note, a concept page, a set of comparisons). Be specific about what each round produces.
2. **Prioritize by impact** — book reading notes > technical deep-dives > entity pages > comparisons > navigation refactors.
3. **Use delegate_task for parallel reading** — batch 3 book summaries at once (delegation limit), then create the wiki pages from the summaries.
4. **Alternate content types** across rounds to keep variety: reading note → tech concept → entity → comparison → reading note → ...
5. **Commit periodically** — after every ~10 rounds or when a natural boundary is hit, do a `git add -A && git commit -m "X rounds: summary"`.
6. **Update queries/todo.md** at the end of each batch to reflect progress.

**Round template** (what a single round looks like):

```
Round N/X: [Type] [Specific Topic]
- Create/source content via terminal, delegate_task, or direct write
- Write the wiki page with frontmatter, structured tables, and raw/ links
- Cross-link to existing pages
- Progress: mark in todo
```

For auto-iteration requests like "40 轮", create an explicit batch plan with the todo tool, then work through it round by round. Use delegate_task for I/O-heavy tasks (reading PDFs, extracting data) so the main session focuses on writing.

### Batch Direct Filling of Empty Stubs (No delegate_task Needed)

When you have many empty stub pages whose topics are well-defined in `index.md`, you do NOT need delegate_task to read documents first — the agent's domain knowledge is sufficient. Fill them directly with `write_file` in batches of 3-4 per round:

1. **Identify the stub pages** from the `index.md` listing (pages with 0 lines or just frontmatter)
2. **Prioritize by domain centrality** — core technical concepts > reading notes > entity pages > navigation refactors
3. **Use the Technical Deep-Dive template** (see `references/technical-deep-dive-template.md`) for technical concept pages
4. **Write 3-4 pages per turn** using parallel `write_file` calls — each to a different empty stub
5. **Verify with a read_file spot-check** of one page per batch
6. **Cross-link** pages as you go — the last page of each batch should link to others in that batch

This approach was proven in a session that filled 50+ stub pages to substantial content (100-150 lines each) in a single session, covering AUTOSAR, functional safety, ISO 26262, MISRA, embedded systems, systems engineering, software engineering, RTOS scheduling, hypervisors, character encoding, and 10+ more domains.

Key advantage: skips the I/O overhead of reading PDFs from raw/ when the agent already knows the domain. Reserve delegate_task reads for books and documents the agent cannot synthesize from training data (specific book arguments, proprietary standards, personal documents).

### Layered Content Quality

Pages in the wiki naturally exist at different depths. Use status markers progressively:

| Status | When to use | Content depth |
|--------|-------------|---------------|
| `stub` | Entity page, simple raw/ reference | Frontmatter + 1-2 paragraphs + link |
| `growing` | Technical concept, domain page | Architecture diagrams, tables, sub-sections, cross-links |
| `mature` | After multiple revisions with user feedback | Comprehensive with real examples and deep cross-referencing |

Don't force `mature` on first write — `growing` is the right target for a first-pass technical deep-dive. It signals "substantive but room for refinement."

### Post-Fill Quality Audit and Targeted Expansion

After batch-filling stubs (50+ pages in one session), run a **quality audit** to find pages that need expansion:

**Step 1: Bulk size audit via execute_code**

```python
import os
wiki = os.path.expanduser("~/hermes/wiki")
for d in ["concepts", "entities", "comparisons", "reading_notes", "queries"]:
    dp = os.path.join(wiki, d)
    for f in os.listdir(dp):
        if f.endswith('.md') or f.endswith('.html'):
            size = os.path.getsize(os.path.join(dp, f))
            # categorize: <1KB (thin), 1-3KB (medium), ≥3KB (rich)
```

This is much faster than calling `read_file` 77 times individually. Execute the audit script, then report the quality distribution to the user: "X thin (<1KB) + Y medium (1-3KB) + Z rich (≥3KB)".

**Step 2: Targeted expansion of thin pages**

For pages <1KB (usually entities with only frontmatter + 2-3 lines):
1. Read the current content to understand what's there
2. Expand with domain knowledge — the agent already knows the topic (ARM, CPU, Python, C++)
3. Target 4-7 KB per page: architecture diagrams, version tables, cross-links, raw/ file references
4. Write 3-4 pages per round, sequential to avoid sibling-subagent conflicts

**Step 3: Targeted expansion of medium pages**

For pages 1-3KB that are core technical concepts (not reading notes):
- `godel.md` → expand with proof sketch, implications for CS
- `cpu-architecture.md` → expand with pipeline, cache coherency, branch prediction
- Entity pages (`arm.md`, `cpp.md`, `ti-radar.md`) → expand with product lines, specs, domain-specific context
- Glossary → add domain-segmented abbreviation tables

**Step 4: Report the shift**

After expansion rounds, re-run the audit script. Typical outcome: thin goes from 7 → 1 (only source-material-constrained pages), rich goes from 44 → 54.

### Round 1: Top 5–6 Directories

For each large directory, create a concept page as a **navigation index** linking to raw/ subdirectories:

```yaml
---
title: 编程与软件开发
tags: [编程, 软件工程]
created: YYYY-MM-DD
status: growing
source: raw/programming/
---
```

Pattern: Overview (size + file count) → Subdirectory table (name, description, raw/ link) → Related concepts.

### Round 2: Medium Directories

Cover remaining important directories:
- **Tool collections** (`software_menual/`): group by category (compilers, debuggers, docs, databases)
- **Book collections** (`life/`): full categorized book list with title, author, format, raw/ link
- **Domain refs** (`protocols/`, `electrical design/`): index with tables

### Round 3: Comparisons + Entities

Create comparison pages for related technologies:
```markdown
| 维度 | Option A | Option B |
|------|----------|----------|
| Aspect | value    | value    |
```

Entity pages for key people/technologies with a brief overview + raw/ source link.

### Round 4: Knowledge Map README

Evolve README from simple index to **knowledge map**:
- Organize concept links by domain (Programming, OS, Hardware, Automotive, etc.)
- Quick-entry table: directory | size | file count | wiki page
- Comparisons section
- Exclusion table
- Every page reachable in ≤ 2 clicks from README

### Round 5: Track Progress

Update `queries/todo.md` with completed checkboxes and remaining items.

### Round 6: Deep Reading Notes (PDF Books)

Create structured reading notes from books in the collection. This turns a raw `.pdf` file into searchable, actionable knowledge.

Workflow:

```bash
# 1. Check book metadata
pdfinfo "/path/to/book.pdf" | grep -iE 'title|author|pages|subject'

# 2. Extract full text
pdftotext "/path/to/book.pdf" /tmp/book.txt

# 3. Read key sections
sed -n 'LINES_START,LINES_ENDp' /tmp/book.txt   # preface
sed -n 'LINES_START,LINES_ENDp' /tmp/book.txt   # chapter 1 (core thesis)
sed -n 'LINES_START,LINES_ENDp' /tmp/book.txt   # conclusion/summary
```

Page structure for a reading note:

```markdown
---
title: 读书笔记：书名 (English Title)
tags: [读书笔记, topic, author]
created: YYYY-MM-DD
status: growing
source: raw/xxx.pdf
---

## 基本信息

- **原书名**：English Title
- **作者**：Author
- **首版**／**版本**：Year / pages
- **核心影响**：Related thinkers/influences
- **源文件**：[raw/xxx.pdf](raw/xxx.pdf)

## 核心论点

2–3 paragraph summary of the book's central thesis. Quote key sentences.

## 章节结构与各章要点

Table: chapter number → theme → core argument / fallacy debunked.

## 经典论点摘录

Thematic groupings with the author's key arguments. Use subheadings per theme.

## 历史地位与评价

Context within the field, influence, and (where appropriate) criticism.

## 延伸阅读

Links to related wiki pages and other books in the collection.
```

Pitfalls:
- **Garbled OCR**: Chinese PDFs with outdated OCR produce garbled chapter titles. Use context from the table of contents to infer real titles.
- **Sed line numbers**: `pdfinfo` tells you page count. Multiply by ~15 lines/page for English, ~25 for Chinese to estimate sed ranges.
- **Don't over-summarize**: The reading note should be self-contained — someone reading the note should understand the book's argument without needing the original. Include key quotes.

See `references/reading-note-creation.md` for a real session example, and `templates/reading-note.md` for a starting template.

## Verification

### Symlink health

```bash
# Count symlinks
find raw/ -type l | wc -l

# Verify excluded items are gone
ls raw/programming/Qt 2>&1 && echo "SHOULD BE EXCLUDED" || echo "correctly excluded"

# Check for broken symlinks
find raw/ -type l -xtype l 2>/dev/null
```

### Page quality audit (post-fill)

After batch content filling, verify page sizes with `execute_code` — a single script reads `os.path.getsize()` for all 77 pages in under a second, vs. 77 individual `read_file` calls:

```python
import os
wiki = os.path.expanduser("~/hermes/wiki")
thin, medium, rich = 0, 0, 0
for d in ["concepts", "entities", "comparisons", "reading_notes", "queries"]:
    for f in os.listdir(os.path.join(wiki, d)):
        if f.endswith('.md') or f.endswith('.html'):
            size = os.path.getsize(os.path.join(wiki, d, f))
            if size < 1000: thin += 1
            elif size < 3000: medium += 1
            else: rich += 1
print(f"{thin} thin + {medium} medium + {rich} rich")
```

Then spot-check one representative page per quality tier with `read_file` to verify content is correct (not just non-zero bytes).
