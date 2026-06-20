---
name: llm-wiki
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB."
version: 3.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv, ocr-and-documents, scrape-website-mirror]
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base, OR to initialize a wiki
  from an existing document library on disk (symlink mode — see "Symlink Mode" section)
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

**Location:** Set via `WIKI_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent. May also include `.html` files in `reading_notes/`
that are original web page archives — these are **immutable first-class pages**
referenced via standard Markdown links `[title](path.html)`, NOT `[[wikilinks]]`
(Obsidian can't resolve wikilinks to HTML).
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki (from scratch)

When the user asks to create or start an empty wiki:

1. Determine the wiki path (from `$WIKI_PATH` env var, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### Symlink Mode: Initializing from an Existing Local Document Library

When the user already has a large document library on disk (external drive, work archive,
backup of saved web pages) and wants to create a wiki that references it rather than
copying/ingesting everything:

**Principle: symlinks, not copies.** The existing documents stay in place. The wiki's
`raw/` directory is a mirror of symlinks. This gives you zero extra disk usage and
keeps the original as the source of truth.

#### Workflow

**① Scope the library.** Load `references/library-audit-methodology.md` for the
full audit methodology (classification, garbage patterns, edge case detection).
Don't symlink blindly — scan first:

```bash
# Total file count & size
find "$SRC_DIR" -type f | wc -l
du -sh "$SRC_DIR"

# File type distribution
find "$SRC_DIR" -type f | awk -F. '{print tolower($NF)}' | sort | uniq -c | sort -rn | head -20

# Directory sizes
du -sh "$SRC_DIR"/*/ 2>/dev/null | sort -rh

# Root-level file listing
ls -la "$SRC_DIR"
```

**② Classify content categories** to decide what to include:

| Category | File types | Wiki value |
|----------|-----------|------------|
| **Knowledge docs** | pdf, txt, md, doc, rtf, html, htm | Primary — keep |
| **Source code / SDKs** | c, h, cpp, py, js, rs, makefile | Keep as reference, note BSP nature |
| **Media (educational)** | aac, m4a, mp3, mp4, jpg, png | Keep if lecture/tutorial |
| **Media (personal)** | mp4 of personal events | Questionable — ask user |
| **Build artifacts** | .o, .exe, .bin, .tmp, .swp | Exclude — no wiki value |
| **IDE/Project files** | .uvproj, .uvopt, .ewp, .ewd | Exclude unless user asks |
| **OS junk** | Thumbs.db, .DS_Store | Always exclude |
| **Embedded repos** | .git/ directories | Exclude — source control metadata |
| **Website dumps** | html+css+js bundles | Keep if documentation, skip if generic site mirror |

**③ Identify garbage patterns to exclude.** Common noise in document libraries:

| Pattern | Why | Count in reference session |
|---------|-----|---------------------------|
| `Thumbs.db` | Windows thumbnail cache | 10 |
| `*.o` | Compiled object files | 124 |
| `*.swp` | Vim swap files | 8 |
| `*.tmp` | Temp files | 2 |
| `.git/` directories | Git metadata | 1 |
| `.DS_Store` | macOS folder metadata | 0 (Linux host) |

These are scattered inside legitimate directories (e.g., a BSP source tree under
`CPU/`). The symlink approach preserves them transparently — they don't cost
space.

**After linking, create a `.rawlenses` file** inside `raw/` to document what
was excluded and why. This gives anyone browsing the wiki's source layer an
at-a-glance reference for filtered patterns:

```yaml
# raw/.rawlenses — filtering config

IGNORE_PATTERNS:
  - '*.o'          # 编译目标文件
  - '*.swp'        # Vim 交换文件
  - '*.tmp'        # 临时文件
  - 'Thumbs.db'    # Windows 缩略图缓存
  - '.git'         # Git 仓库内部数据
  - '.DS_Store'    # macOS 元数据

EXCLUDED_DIRS:
  - HJH            # 个人档案，非知识内容
  - Gri            # 个人隐私文件
  - Jenkins        # 过时的 CI 文档存档
```

**④ Ask for scoping confirmation.** Present a summary like:

```
Source: /media/grissiom/Docs/ (24 GB, 58,146 files)
In scope: 60+ directories (programming, linux, OS, CPU, CAR, 王陶陶, ...)
Garbage found: Thumbs.db(10), .o(124), .swp(8), .tmp(2), .git(1)
Questionable: HJH/ (2.3G, personal videos + resume — archive or knowledge?)
```

Let the user OK the scope before linking.

**⑤ Create symlinks:**

```bash
mkdir -p "$WIKI/raw"
cd "$WIKI/raw"
for item in "$SRC_DIR"/*; do
  ln -sf "$item" "$(basename "$item")"
done
```

This creates one symlink per root-level file/directory in the library.
It's fast (<1s for 80+ items) and costs zero disk.

**⑥ Seed the wiki structure.** After linking, create introductory pages
so the wiki is immediately navigable:
- `README.md` — homepage with categorized navigation to all raw/ directories
- Seed pages in `entities/`, `concepts/`, `comparisons/`, `queries/`
  for the biggest/most important topics
- `SCHEMA.md` customized to the library's bilingual zh/en nature

Each seed page should have `status: stub` so the user sees the growth track.

**⑦ Update memory/log** that the wiki was initialized in symlink mode, with
the source path and any files excluded.

#### Iterative Scoping Refinement

Scoping is rarely one-shot. After the first summary and exclusion decisions,
the user may come back with more questions or spot additional content to remove.
Treat these follow-ups as a **refinement loop**, not a failure of the initial
audit:

- The user may ask "还有什么可以排除的？" — re-examine the remaining
  directories, especially small or ambiguous ones, and look deeper at their
  actual content (not just names and sizes)
- The user may flag a specific directory for deeper evaluation (e.g., "PyQt
  API 文档是否已经过时？"). When this happens:
  - Check the **version and release date** of the content
  - For tool-specific documentation, cross-reference the tool's current
    major version — if the docs cover a version that's been EOL for years
    (e.g., PyQt4 → EOL 2015, Jenkins CI → superseded), flag as outdated
  - **Version-obsolescence rule**: if a tool has been superseded by 1+ major
    versions and the docs in the library cover the old version, the docs are
    stale. Book documentation older than ~10 years with no topical reason
    (classic reference, historical analysis) should also be questioned.
- After each refinement, update `.rawlenses`, README, and memory to reflect
  the new state
- There is no "done" signal — stop when the user is satisfied with the scope

This refinement loop applies primarily to **Symlink Mode** (where the library
is a fixed snapshot and exclusions are about navigation hygiene). For the
standard ingestion path, the Pre-Ingest Scoping section's upfront decisions
should suffice.

#### When Symlink Mode is the Right Choice

- User says "不要拷贝，要做链接" (don't copy, link)
- Library is on an external drive or network share
- Library is very large (10GB+) and only a subset is actively referenced
- User wants to keep the original folder structure intact
- User may add/remove files from the original library independently

#### When to Prefer Ingestion (the standard llm-wiki path)

- Sources are URLs (must be fetched)
- Sources are individual files the user drags in
- The wiki needs full-text search across source content
- The user wants to extract knowledge, not just catalog files
- Library file types are consistently prose (pdf, md, txt)

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Bilingual wikis (zh/en): Chinese characters in filenames are acceptable.
  For the same entity, create `entity-name-zh.md` and `entity-name-en.md` variants,
  or keep a single page with bilingual content and tag accordingly.
  For disambiguation, use brackets: `spring[coil].md` vs `spring[season].md`.
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source. This lets a reader trace each
  claim back without re-reading the whole raw file. Optional on single-source pages where the
  `sources:` frontmatter is enough.

## Frontmatter

### Wiki Pages

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
status: stub | draft | growing | mature    # optional growth track
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
# Optional quality signals:
confidence: high | medium | low        # how well-supported the claims are
contested: true                        # set when the page has unresolved contradictions
contradictions: [other-page-slug]      # pages this one conflicts with
---
```

`status` is optional but recommended for personal wikis where content matures
over time:
- **stub** — barely started, just a title and maybe a sentence
- **draft** — rough content, needs cleanup and cross-references
- **growing** — substantial but incomplete, actively expanding
- **mature** — reviewed, cross-referenced, reasonably complete

Combined with `confidence`, this gives at-a-glance signals about how reliable
a page is. Lint reports should flag pages that are `confidence: high` but
`status: stub` (impossible — can't be confident about a stub).

### raw/ Frontmatter

Raw sources ALSO get a small frontmatter block so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article   # original URL, if applicable
ingested: YYYY-MM-DD
sha256: <hex digest of the raw content below the frontmatter>
---
```

The `sha256:` lets a future re-ingest of the same URL skip processing when content is unchanged,
and flag drift when it has changed. Compute over the body only (everything after the closing
`---`), not the frontmatter itself.

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is a link + thesis-level summary — not a one-liner rephrasing the title, but a statement of the page's central argument, contribution, or conclusion.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a thesis-level summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**Summary quality rule:** A good index summary tells the reader *what this page argues or concludes*, not just *what it is about*.

- ❌ "LLM 中语言的数学本质" — restates the title, no information
- ❌ "关于 LLM 语言的范畴论视角分析" — slightly more detail but still a topic label
- ✅ "用范畴论（Yoneda 引理、Nerve 构造、Kan 扩张）重新审视 LLM 中语言的意义结构，指出分布式语义假设在数学上等价于 Yoneda 引理" — captures the thesis and method

A summary must answer: after reading this page, what should the reader know or believe that they didn't before? If it's just a topic label, rewrite it.

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - **Single URL (article, post):** → use `web_extract` to get markdown, save to `raw/articles/`
   - **Entire static site / blog (bulk scraping):** → load
     `skill_view(name="llm-wiki", file_path="references/bulk-web-scraping.md")`
     for the proven 5-phase workflow (recon → parallel HTML download → image
     extraction → metadata → wiki integration). Do NOT use `web_extract` for
     bulk — it's one-page-at-a-time and will take forever.
   - **Local PDF file** (file is on disk, not a URL):
     1. First verify the file is readable: `file -L "$PDF_PATH"` (check for broken symlinks)
     2. Load the `ocr-and-documents` skill for tool selection guidance
     3. Use **openDataLoader-pdf** (standard mode) for English PDFs — fastest, JSON+bbox output
     4. Use **pymupdf4llm** for CJK/Chinese PDFs or when Java is unavailable
     5. Save the resulting Markdown to `raw/papers/` and link the source in frontmatter
     6. Do NOT overwrite the original PDF — raw/ sources are immutable. The PDF stays as-is,
        the Markdown extraction is the working copy for wiki authoring.
   - **Web PDF** → use `web_extract` (handles PDFs via Firecrawl), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`
   - **Add raw frontmatter** (`source_url`, `ingested`, `sha256` of the body).
     On re-ingest of the same URL: recompute the sha256, compare to the stored value —
     skip if identical, flag drift and update if different. This is cheap enough to
     do on every re-ingest and catches silent source changes.

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

④ **Write or update wiki pages:**
   - **SYNTHESIS RULE (critical):** Wiki pages MUST synthesize and extract knowledge.
     A wiki page should *teach something* — structure concepts, reveal patterns,
     draw conclusions, cross-reference related ideas. NEVER create list-only pages
     (tables of article titles/URLs, chronological inventories, raw metadata dumps).
     Those belong as raw/ files or a simple JSON index, not as wiki concept pages.
     If you're tempted to create N sub-index pages per category, stop — instead,
     identify 3-6 thematic clusters and write one synthesis page per cluster that
     extracts principles, contrasts ideas, and teaches the reader something new.
   - **Local links over external URLs:** All references to raw sources must point
     to local `raw/articles/source-file` paths, never to external URLs. The reader
     should be able to navigate entirely within the wiki without hitting the web.
   - **Link text must be descriptive, never generic.** Raw-source links (`raw/articles/...`)
     must use the article title or a meaningful description as link text. NEVER use
     bare `[raw](raw/articles/...)` — the reader must know what they're clicking on
     without following the link. When bulk-ingesting, use `execute_code` with the
     article metadata JSON to programmatically replace all `[raw](raw/articles/ID.html)`
     with `[Article Title](raw/articles/ID.html)` in a single pass. Example:\n     ```python\n     pattern = re.compile(r'\\[raw\\]\\(raw/articles/.../(\\d+)\\.html\\)')\n     for m in pattern.finditer(content):\n         title = title_by_id[m.group(1)]\n         content = content.replace(m.group(0), f'[{title}](raw/.../{m.group(1)}.html)')\n     ```
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md
   - **Provenance:** On pages synthesizing 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Lint

When the user asks to lint, health-check, or audit the wiki:

> **For batch repair workflows** (bulk cross-linking, stub upgrades, index rebuild),
> load `references/batch-repair.md` via `skill_view(name="llm-wiki", file_path="references/batch-repair.md")`.
> It has the proven lint script with correct wikilink resolution and step-by-step
> repair procedures.

① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
```python
# Use execute_code for this — programmatic scan across all wiki pages
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# Scan all .md AND .html files in entities/, concepts/, comparisons/, queries/,
# reading_notes/ using os.walk (recursive, handles subdirectories like ai-agent/).
# Extract all [[wikilinks]] — build inbound link map
# Pages with zero inbound links are orphans
# HTML pages: no frontmatter required. Use filesystem mtime as created/updated.
```

② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.

③ **Index completeness:** Every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.

④ **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, sources). Tags must be in the taxonomy.

⑤ **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.

⑥ **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts. Surface all pages
   with `contested: true` or `contradictions:` frontmatter for user review.

⑦ **Quality signals:** List pages with `confidence: low` and any page that cites
   only a single source but has no confidence field set — these are candidates
   for either finding corroboration or demoting to `confidence: medium`.

⑧ **Source drift:** For each file in `raw/` with a `sha256:` frontmatter, recompute
   the hash and flag mismatches. Mismatches indicate the raw file was edited
   (shouldn't happen — raw/ is immutable) or ingested from a URL that has since
   changed. Not a hard error, but worth reporting.

⑨ **Page size:** Flag pages over 200 lines — candidates for splitting.

⑩ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.

⑪ **Log rotation:** If log.md exceeds 500 entries, rotate it.

⑫ **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested pages > stale content > style issues).

⑬ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Writing Good Summaries

Wiki summaries serve two roles: they help the reader decide whether to click,
and they act as memory anchors when scanning the index. A summary must capture
the **central thesis** — the core argument, insight, or conclusion the page makes.

### What makes a good summary

1. **States the argument, not the topic.** "Transformer architecture overview"
   is a topic. "Attention mechanisms eliminate the sequential bottleneck of RNNs
   by computing pairwise token interactions in parallel" is an argument.
2. **Includes method when relevant.** If the page uses a specific analytical
   lens (category theory, distributed systems theory, formal verification),
   name it in the summary.
3. **Names the entities involved.** If the page analyzes a specific model,
   paper, or tool, name it.
4. **Answers "so what?"** The reader should understand what they'll learn,
   not just what subject area the page falls in.

### Examples

| Topic | Bad summary | Good summary |
|-------|-------------|--------------|
| LLM 语言本质 | LLM 中语言的数学本质 | 用范畴论（Yoneda 引理、Kan 扩张）和代数拓扑证明：LLM 的分布式语义假设在数学上等价于 Yoneda 引理，语言的"意义"可建模为单纯集上的同伦类型 |
| Harness Engineering | Harness Engineering 方法论介绍 | 提出用三个 Markdown 文件虚拟化大厂角色分工，实现 AI Agent 的规划→实现→验收三权分立，程序员从写 Prompt 升级为定义系统权责边界 |
| Multi-Agent 协作 | 多 Agent 协作分析 | 形式化验证证明多 Agent 瓶颈是分布式系统问题（一致性、故障隔离、任务路由）而非模型能力——"等下一代模型就好了"是幻觉 |

### When to skip or shorten

- **Entity pages** for people, companies, or products whose significance is
  self-evident can have shorter summaries (e.g., "NVIDIA：GPU 与 AI 加速计算领导者")
- **Comparison pages** naturally need descriptive summaries naming the items
- **Stub pages** can have minimal summaries until they grow — flag with
  `status: stub` and a note about planned expansion

**Use these principles whenever you write or update index.md entries.**

### Searching

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### Pre-Ingest Scoping

When the user says "ingest everything from <directory>", **do NOT start ingesting
blindly** — the directory may contain 58k+ files across many topics, file types,
and eras. Scope first:

① **Explore the source directory:**
   ```bash
   # File count & type distribution
   find "$SRC_DIR" -type f | wc -l
   find "$SRC_DIR" -type f | awk -F. '{print tolower($NF)}' | sort | uniq -c | sort -rn

   # Directory structure
   du -sh "$SRC_DIR"/*/ 2>/dev/null | sort -rh

   # Top-level listing
   ls -la "$SRC_DIR"
   ```

② **Classify the content** into categories:
   - **Knowledge docs** (pdf, txt, md, doc, rtf) — primary wiki material
   - **Source code** (c, cpp, h, py, js, rs) — not wiki content unless user says otherwise
   - **Web archives** (html, htm, css) — too noisy for direct ingestion
   - **Media** (jpg, png, gif, mp3, aac, m4a) — reference material, not editable
   - **Binaries/archives** (zip, tar.gz, exe, bin) — uningestible

③ **Present a scoping summary** to the user:
   - Total file count and size
   - Breakdown by category and file type
   - Notable subdirectories and their topics
   - Recommendation of which categories to prioritize and which to skip

④ **Ask for prioritization.** Don't assume — the user may want:
   - Only certain subdirectories ingested first
   - Only knowledge-doc file types (pdf, txt, md) and skip the rest
   - Everything from a specific topic area (e.g., "start with AGI/ and CS/")
   - A specific sequence (oldest first, newest first, by topic)

⑤ **Filter by ingestibility** — skip by default (user can override):
   - Source code files (.c, .h, .cpp, .py, .js, .rs, etc.)
   - Web page archives (.html, .htm, .css, .js bundles)
   - Media files (.jpg, .png, .gif, .mp3, .aac, .m4a, .mp4)
   - Binary formats (.zip, .tar.gz, .exe, .bin, .dcd, .dii)
   - System files (.reg, .gif, .jpg as standalone — unless embedded in a doc)

   Reason: these files don't contain digestible prose. Source code and HTML
   dumps are either too noisy or too specialized to produce useful wiki pages.
   Media and binaries can't be read as text.

⑥ **Document the filtering** in the log entry so the user knows what was
   intentionally skipped and can request it later.

⑦ **Only after scoping + user agreement** should you proceed with actual
   ingestion. Never ingest a bulk source directory without going through
   scoping first — 58k files of html/css/code noise will trash the wiki.

### Bulk Ingest

When ingesting multiple sources at once (after Pre-Ingest Scoping), batch the updates:
1. Read all sources first — but only the subset agreed with the user
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch
   - Include what was filtered and why, so the user can override later

### Bulk Web Scraping (URL-based ingest of entire sites)

> **For scraping entire blogs/static sites from URLs** (740+ articles, images, metadata),
> load `references/bulk-web-scraping.md` via
> `skill_view(name="llm-wiki", file_path="references/bulk-web-scraping.md")`.
> It covers the proven 5-phase workflow: recon → parallel HTML download →
> image extraction → metadata → wiki integration. Key pitfall: do NOT use
> `wget -p` for bulk — it re-downloads shared CSS/JS per page and kills throughput.
> Split into HTML-first (xargs+curl, P=20) then images.

### 4. Tree Organization (reorganizing flat concepts/)

When a wiki's `concepts/` directory grows beyond ~30 pages or spans 5+ distinct
domains, reorganize flat pages into a tree of subdirectories by domain.

**When to reorganize:**
- User explicitly asks to "归类" or "整理成树状结构"
- Lint reveals too many root-level pages making navigation unwieldy
- Index sections become hard to scan (50+ entries per section)

**Procedure (do all in one `execute_code` pass):**

① **Define a mapping** of `old_filename → new_subdir/filename`. Group by domain:
   `automotive-electronics.md → automotive/automotive-electronics.md`
   `linux-kernel.md → embedded/linux-kernel.md`
   etc. Present the mapping to the user first for approval.

② **Create subdirs and move files** — `os.makedirs` + `shutil.move`.

③ **Global wikilink update** — scan ALL `.md` files with a regex that rewrites
   `[[concepts/old-name]]` → `[[concepts/new-subdir/old-name]]`. Handle piped text:
   `[[concepts/old-name|text]]` → `[[concepts/new-subdir/old-name|text]]`.
   Also handle bare names (without `concepts/` prefix) in files that live inside
   concepts/ itself.

④ **Fix cross-file references** — some pages link with bare `[[software-engineering]]`
   instead of `[[concepts/software-engineering]]`. After moving, these bare links
   lose their `concepts/` context and break. Catch them with a second regex pass
   and add the full `concepts/subdir/` prefix.

⑤ **Verify** — run the lint script. Target: 0 broken wikilinks. Common failure mode:
   a file was renamed (e.g., `management-quality.md` → `misc-management-quality.md`)
   and old references still use the old name.

⑥ **Update index.md and README.md** with the new paths.

**Pitfall:** The `sed` command with pipe characters (`|`) in wikilinks is fragile —
prefer `execute_code` with Python regex for bulk replacements. The patch tool is
safer for individual fixes.

### 5. Cross-referencing Reading Notes

`reading_notes/*.html` are raw web page archives (immutable). They should be linked
FROM concept pages, not left as orphan files. After ingesting a reading_note:

1. Determine which concept page best covers the topic
2. Add a `## 相关阅读笔记` section at the bottom (before `## 相关页面` if present)
3. Use standard Markdown links: `[文章标题](reading_notes/foo.html) — 一句话摘要`

Example:
```markdown
## 相关阅读笔记

- [理想 M100 芯片 NPU 数据流架构解析](reading_notes/li-auto-m100-npu-architecture.html) — ISCA 2026：编排式数据流架构，TSMC N5A，UniAD 端到端 30FPS，4.4× Thor-U
```

This gives the concept page "further reading" depth while keeping HTML sources untouched.

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration (references/obsidian-vault.md)

The wiki directory works as an Obsidian vault out of the box. For file-tool
workflows (read_file, search_files, write_file, patch) for editing notes,
load `references/obsidian-vault.md` via `skill_view(name="llm-wiki", file_path="references/obsidian-vault.md")`.
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Batch Repair (when wiki has degraded)

When the user says "完善 wiki", "improve wiki", or a lint reveals widespread issues,
follow this prioritized repair workflow. For the full procedure including programmatic
lint scripts, load `references/batch-repair.md`.

### Priority order

1. **Rebuild missing index.md / log.md** — if either is gone, rebuild from filesystem:
   scan all .md files in entities/concepts/comparisons/queries, extract titles from
   frontmatter, and generate the index from scratch. Start a fresh log documenting the
   rebuild.
2. **Fix broken wikilinks** — broken links erode trust. Fix them first.
3. **Add cross-links to dead-end pages** — pages with `## 相关页面` but no actual links
   (empty section) are common. Fill them. Pages with no outgoing links at all: add
   `## 相关页面` with 2-5 links based on shared tags or topic clusters.
4. **Batch-upgrade misclassified stubs** — pages marked `status: stub` with >500 chars
   of substantive content (excluding the `相关页面` section) should be `growing`.
   Upgrade them in one pass.
5. **Expand hot stubs** — pages with incoming links but thin content (<500 chars) are
   "disappointing" — people navigate there and find nothing. Expand them with definitions,
   tables, and key facts.

### Wikilink formats to handle

Wikilinks in a mature wiki come in two forms; lint code must resolve both:

- **Dir-prefixed**: `[[concepts/linux-kernel]]` — already scoped to a page directory
- **Bare-name**: `[[linux-kernel]]` — needs directory resolution across entities/,
  concepts/, comparisons/, queries/

Resolution order: try dir-prefixed match first, then bare-name across all page dirs.
The first lint pass often gets this wrong and reports false broken links — always
verify before acting on broken-link reports.

### Empty "相关页面" sections

Pages from older sessions may have a `## 相关页面` header with no wikilinks below it.
These are NOT real cross-references — they're placeholder stubs. When found:
replace the empty section with actual links. Use `re.sub(r'## 相关页面\n\n.*?(?=\n## |\Z)', ...)`
to match and replace the section, not the header alone.

### Bulk status upgrade threshold

Pages with `status: stub` and >500 chars of body content (after stripping whitespace
and the `## 相关页面` section) have enough substance to be `growing`. Upgrade them
programmatically with a single `execute_code` pass — don't patch each file individually.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **HTML files in page dirs are immutable original source archives.** `reading_notes/`
  `.html` files must never be modified (no frontmatter, no MD conversion). Reference
  them with standard Markdown links `[title](path.html)`, NOT `[[wikilinks]]` — Obsidian
  wikilinks only resolve `.md` files. Lint: flag `[[link]]` that resolves to `.html` as
  "use standard link format". `find_pages()` must use `os.walk` (recursive) to find
  `.html` files in subdirectories.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **index.md or log.md may be missing** — if the orientation reads fail with "File not found",
  do NOT skip the step. Rebuild them from the filesystem (scan all .md files, extract
  frontmatter titles). A wiki without index and log is unmaintainable — fix this before
  doing anything else.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create list-only pages** — a wiki page that is just a table of article titles,
  dates, and URLs is not a wiki page, it's a raw index. Wiki pages must synthesize:
  extract principles, find patterns, draw conclusions, and teach the reader something.
  When ingesting a blog or site with hundreds of articles, group them into 3-6 thematic
  clusters and write synthesis pages — not one list page per category. The raw HTML
  files are already in `raw/`; the wiki's job is to extract what they *mean*, not what
  they *are*. If the user says "做总结提炼和归纳，而不是简单的罗列", immediately
  restructure from lists to synthesis.
- **All wiki links must point to local `raw/` paths, never external URLs.** When referencing
  ingested articles, link to `raw/articles/source-file.html` NOT `https://example.com/...`.
  The reader should navigate entirely within the wiki without hitting the net.
- **Link text must be descriptive, never generic.** Raw-source links must use the article
  title or a meaningful phrase as link text. NEVER use bare `[raw](raw/articles/...)` —
  replace with `[Article Title](raw/articles/ID.html)`. For bulk ingest, use
  `execute_code` to programmatically replace all generic links from metadata JSON in one pass.
- **Index summaries must be thesis-driven, not title-rewrites.** Every entry in index.md
  should tell the reader what the page argues or concludes, not just what topic it covers.
  See `references/writing-good-summaries.md` for examples. A summary like "关于 X 的分析"
  or "X 的概述" is a topic label, not a summary — rewrite it to capture the central thesis.
- **README ≠ index.** `README.md` is a curated knowledge map organized by domain/topic —
  for humans discovering what to read. `index.md` is a complete alphabetical catalog
  organized by page type — for machines and quick lookups. Keep both in sync. When adding
  pages, update both files. See `references/readme-vs-index.md` for the full distinction.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rotate it to `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
- **Symlink wikis: verify the drive is mounted.** When using symlink mode (raw/ pointing to an
  external drive), the source drive may not always be plugged in. Before any raw/ operation:
  ```bash
  file -L "$WIKI/raw/"* | grep broken
  ```
  If broken symlinks are found, report "The source drive is not mounted; raw/ symlinks are broken."
  to the user. Do not try to guess the mount path or create fake error files — just report it. 
  The same check belongs in the orientation step if the wiki uses symlink mode.
- **Bulk web scraping: never use `wget -p`.** The `-p` (page-requisites) flag causes wget
  to re-download shared CSS/JS/plugin files for every single page, killing throughput on
  shared-asset sites (WordPress, etc.). For bulk HTML downloads, use xargs+curl at P=20
  concurrency without `-p`, then extract and download unique images in a separate pass.
  Full workflow in `references/bulk-web-scraping.md`.
- **`[[../index]]` and `[[../README]]` never resolve.** Wikilinks with `../` parent references
  (e.g., `[[../index|Wiki 索引]]`) are broken in every renderer. Replace with standard
  Markdown links: `[Wiki 索引](index.md)`. This most often appears in `queries/todo.md`.
- **Patch tool corrupts markdown line breaks.** When using `patch` to edit index.md or
  other files containing markdown line breaks (two trailing spaces + newline: `  \n`),
  the `old_string`/`new_string` mechanism may turn `\n` into literal backslash-n (`\\n`)
  in the output. After patching, always grep-check for literal `\\n` and fix with
  `execute_code`: `content.replace('  \\n  *', '  \n  *')`. This is most common when
  adding entries to the Reading Notes section of index.md.

## Related Tools

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) is a Node.js CLI that
compiles sources into a concept wiki with the same Karpathy inspiration. It's Obsidian-compatible,
so users who want a scheduled/CLI-driven compile pipeline can point it at the same vault this
skill maintains. Trade-offs: it owns page generation (replaces the agent's judgment on page
creation) and is tuned for small corpora. Use this skill when you want agent-in-the-loop curation;
use llmwiki when you want batch compile of a source directory.
