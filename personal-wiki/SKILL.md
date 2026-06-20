---
name: personal-wiki
description: "Set up, restructure, and fill a personal knowledge wiki backed by symlinks to an existing document collection."
category: productivity
---

# Personal Knowledge Wiki

Set up and maintain a personal knowledge management (PKM) wiki from an existing local document collection. Uses symbolic links — never copies — to avoid duplicating data.

## Directory Structure

```
~/hermes/wiki/
├── SCHEMA.md          ← schema & conventions
├── README.md          ← homepage / navigation index
├── raw/               ← symlinks to original documents
│   └── .rawlenses     ← ignore-pattern file
├── entities/          ← people, organizations, products
├── concepts/          ← theories, terms, methodologies
├── comparisons/       ← technology / solution comparisons
├── reading_notes/     ← external article archives
└── queries/           ← open questions, TODOs
```

## Phases

### Phase 1: Initial Setup
1. Create directory tree: `mkdir -p ~/hermes/wiki/{raw,entities,concepts,comparisons,reading_notes,queries}`
2. Create SCHEMA.md with frontmatter spec and naming conventions
3. Symlink source documents into `raw/`: `ln -sf "$item" "$(basename "$item")"`
4. **NEVER copy files.** If docs are local, create symlinks from `raw/` to the source.

→ **Full setup details:** `references/personal-wiki-setup.md`
→ **Setup scripts:** `scripts/generate-tag-index.py`

### Phase 2: Evaluate What to Exclude
Walk through every directory and file. Exclusion criteria:

| Criterion | Decision | Example |
|-----------|----------|---------|
| Personal/private files | **Exclude** | Resumes, medical, contracts |
| Build artifacts | **Exclude** | .o, .swp, .tmp, .git |
| Superseded tech docs | **Exclude** | EOL libraries, old frameworks |
| Classic/timeless content | **Keep** | RFCs, encoding tables, CS classics |
| Current-tech docs | **Keep** | Active libraries, current OS docs |

**Version assessment checklist:** Check date range, current version, apply the "teach test" (would someone following these docs today learn current best practices?). 2+ major versions behind → likely exclude. Dead project (no release in 5+ years) → likely exclude.

→ **Full evaluation guide:** `references/collection-evaluation.md`

### Phase 3: Create Wiki Pages
- **Concept pages** (`concepts/`) — one per major domain, with tables linking to raw/ subdirectories
- **Entity pages** (`entities/`) — named after entity, brief overview + raw/ link
- **Comparison pages** (`comparisons/`) — side-by-side tables with feature comparison and use cases
- **Reading notes** (`reading_notes/`) — structured book/article notes (Chinese + English mixed)
- **Glossary pages** — domain-segmented abbreviation tables

→ **Page templates:** `references/page-templates.md`, `templates/reading-note.md`
→ **External article ingestion:** `references/external-article-ingestion.md` — full workflow for saving a web article to both local mirror and wiki synthesis page

### Phase 4: Auto-Iteration Filling
Use batch-rounds strategy: plan ~10 rounds with `todo` tool, prioritize by impact (book notes > technical deep-dives > entity pages > comparisons), use `delegate_task` for parallel PDF reading (3 at once).

**Batch direct filling:** For empty stubs where domain knowledge suffices, fill 3-4 pages per turn with `write_file`. Target `growing` status (substantive but room for refinement), not `mature` on first pass.

### Phase 5: Quality Audit
Run `execute_code` with `os.path.getsize()` to categorize pages: thin (<1KB), medium (1-3KB), rich (≥3KB). Expand thin pages with domain knowledge (target 4-7KB). Spot-check one per batch.

### Phase 6: Git Init
```bash
cd ~/hermes/wiki && git init
echo -e "raw/\n*.swp\n.DS_Store\n.obsidian/" > .gitignore
git add . && git commit -m "init"
```

## Granular Exclusion (Key Technique)

When excluding specific subdirectories inside a source directory:
1. Remove the parent symlink: `unlink /path/to/wiki/raw/parent`
2. `mkdir /path/to/wiki/raw/parent`
3. Create individual symlinks for each child, skipping excluded ones (use Python `os.symlink()` for special chars)

## Pitfalls

- **Read-only source filesystem:** `rm` on symlinks pointing into read-only mount will fail. Use `unlink` on the symlink path itself, not the target.
- **Special characters in filenames:** Chinese chars, `()`, `'`, `~`, spaces break shell quoting. Use `os.symlink()` in Python, not shell `ln`.
- **Symlink traversal:** `cd raw/dir` follows symlink into source. Always use absolute paths or work from wiki root.
- **Sibling subagent conflicts:** When batch-filling empty stubs via parallel `write_file`, sibling subagents can write concurrently. Prefer sequential writes (3-4 per turn) for empty stubs.
- **Over-exclusion:** Distinguish "old but still useful" from "superseded and misleading."
- **Don't copy files:** Symlinks only. The wiki indexes; the source remains authoritative.
