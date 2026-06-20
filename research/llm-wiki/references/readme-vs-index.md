# README vs Index — Wiki Navigation Design

Two navigational files with different purposes:

## README.md — The Knowledge Map

**Purpose:** Curated entry point for humans. A reader should open `README.md` and
immediately understand *what knowledge areas exist* and *where to start reading*.

**Organization:** By **domain/topic**, not by page type. Group related concepts under
thematic headings (e.g., "汽车电子", "编程 & 软件工程", "读书笔记"). Each heading
lists representative pages with one-line descriptions.

**Content:**
- Updated page counts per section
- Representative pages (not all — point to index.md for completeness)
- A visual knowledge map (ASCII art or structured hierarchy)
- Link to index.md for the full catalog

**Maintenance:** Update when new major topic areas emerge or counts change.
Doesn't need a new line for every single page.

**Example structure:**
```
# Wiki Home

## 🚗 汽车电子 (12 页)
- [[concepts/autosar]] — 汽车开放系统架构
- [[concepts/functional-safety]] — ISO 26262 功能安全
...

## 💻 编程 & 软件工程 (11 页)
- [[concepts/programming]] — 编程总览
...
```

## index.md — The Complete Catalog

**Purpose:** Machine-friendly alphabetical catalog of every single wiki page.
Used for quick lookups ("where is page X?") and programmatic scanning.

**Organization:** By **page type** (entities, concepts, comparisons, queries),
alphabetical within each section. Every page gets exactly one line with a
thesis-level summary.

**Content:**
- Total page count in header
- Every page listed, alphabetically by filename
- Each entry has a thesis-level summary (see `writing-good-summaries.md`)
- Updated `Last updated` date

**Maintenance:** Update whenever pages are added, removed, or materially changed.
This is the canonical source of truth for page existence.

## Key Differences

| | README.md | index.md |
|---|---|---|
| **Audience** | Humans discovering knowledge | Humans/programs looking up specific pages |
| **Organization** | By topic/domain | By page type, alphabetical |
| **Completeness** | Representative | Exhaustive |
| **Purpose** | "What should I read?" | "Where is page X?" |
| **Update trigger** | New topic areas, count changes | Every page add/remove/rename |

## How They Work Together

1. New reader opens `README.md` → sees knowledge map → clicks into a domain
2. Researcher looking for a specific comparison → opens `index.md` → finds it under "Comparisons"
3. Agent ingesting new content → updates `index.md` with new pages → checks if README needs a new domain section
4. Both files must stay in sync on counts and existence

## Common Mistake

Duplicating the same content in both files. `README.md` should NOT list all 60+
concept pages — that's what `index.md` is for. `README.md` lists the *domains*
and representative pages; `index.md` lists every page.
