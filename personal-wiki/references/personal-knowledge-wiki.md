---
name: personal-knowledge-wiki
description: Set up, restructure, and fill a personal knowledge wiki backed by symlinks to an existing document collection
category: productivity
triggers:
  - "user asks to init/initialize/set up a wiki or knowledge base"
  - "user wants to organize personal documents into structured notes"
  - "task involves creating concept/entity/comparison pages from a local doc collection"
  - "user asks to 'fill the wiki' or 'restructure' a knowledge base"
---

# Personal Knowledge Wiki

Workflow for creating and maintaining a personal knowledge wiki (`~/hermes/wiki/`) backed by symlinks to an existing local document collection.

## 1. Initial Setup

**NEVER copy files.** If docs are local, create symlinks (`ln -sf`) from `raw/` to the source.

```
~/hermes/wiki/
├── SCHEMA.md           # structure definition
├── README.md           # homepage with knowledge map navigation
├── raw/                # symlinks to original documents (gitignored)
├── entities/           # people, organizations, products
├── concepts/           # theories, methods, terminology
├── comparisons/        # cross-cutting technology comparisons
├── reading_notes/      # external article archives (WeChat, blogs, papers)
└── queries/            # todo items, open questions
```

### SCHEMA.md boilerplate
Frontmatter per-page:
```yaml
---
title: Example Page
tags: [tag1, tag2]
created: YYYY-MM-DD
status: stub | growing | mature
source: raw/path/
---
```

Directories:
- `raw/` — symlinks only, never tracked in git
- `entities/` — named after the entity (`arm.md`, `cpp.md`)
- `concepts/` — domain-level knowledge maps
- `comparisons/` — side-by-side technology comparisons

### Exclusion filter (`.rawlenses`)
Create `raw/.rawlenses` to document excluded directories and file patterns:
- Personal/private files (resumes, medical reports, contracts, family photos)
- Outdated tech docs (EOL'd libraries, superseded API docs)
- Build artifacts (`*.o`, `*.swp`, `*.tmp`, `Thumbs.db`, `.git/`)
- Large archives with no knowledge value

## 2. Evaluating What to Include

When asked to assess the collection:

1. **Scan directory sizes and file counts** — identify the top 5-10 largest, they get priority
2. **Check file type distribution** — HTML archives of saved pages are common; source code dirs may contain build artifacts
3. **Identify exclusion candidates**:
   - **Personal** — resumes, medical reports, contracts, family photos/videos (ask user)
   - **Outdated** — EOL'd frameworks (Qt4, PIL, old iOS SDKs), stale CI docs (Jenkins)
   - **Build artifacts** — `.o`, `.swp`, `.tmp`, `Thumbs.db`
4. **Present a table** of what to exclude with reasoning, let the user decide

**Key judgment**: being a symlink costs zero disk space. The cost of exclusion is navigational noise, not space. Exclude things that are conceptually wrong (personal/private) or actively misleading (outdated docs that teach wrong APIs).

## 3. Creating Wiki Pages

### Concept pages (concepts/)
- One page per major domain (programming, operating-systems, automotive-electronics)
- Include a table linking to corresponding `raw/` subdirectories
- List key references with brief descriptions
- Cross-link to related entity and comparison pages

### Entity pages (entities/)
- Named after the entity (person, technology, organization)
- Brief overview + list of key resources
- Link to raw source directory

### Comparison pages (comparisons/)
- Side-by-side tables comparing technologies
- Include: feature comparison, use cases, links to raw docs
- Cross-link to relevant concept pages

### External Article Saving (reading_notes/)

Save web articles (WeChat official accounts, blogs, technical papers) to `reading_notes/`:

- **WeChat articles**: Use the `weixin-article-to-wiki` skill — it produces a standalone HTML file with locally-downloaded images, zero external dependencies.
- **Other sites**: Save as standalone HTML using the same pattern (no external JS/CSS/fonts, local images).
- **Format**: HTML-only (no `.md`). The HTML is the canonical copy. Each article gets `<slug>.html` + `<slug>_files/` for images.
- **Index entries**: Must include a one-sentence summary of the core argument, not just a title. Link format: `[<slug>](./<slug>.html)` (plain markdown link, not wikilink).

### Reading notes (books from local collection)

When a user's collection contains books (PDF/epub):
2. Read key chapters (preface, core argument, conclusion)
3. Create a concept page with structured notes:
   - Basic info (title, author, edition, source link)
   - Core thesis / one-paragraph summary
   - Chapter-by-chapter breakdown
   - Key quotes
   - Related pages

### Style conventions
- **Chinese + English mixed content** is normal — keep it natural
- Use **tables** for structured data (file lists, comparisons, specs)
- Every page should have at least one `raw/` link so the reader can find source docs
- Status in frontmatter: `stub` (placeholder), `growing` (some content), `mature` (comprehensive)
- `queries/todo.md` tracks pending work — mark completed items `[x]`

## 4. Restructuring ("重构")

When the user says "重构":

1. Analyze the largest directories first (by file count)
2. Create comprehensive index pages for each major area
3. Seed key entity and concept pages for the most important technologies/people
4. Update README.md knowledge map to link everything
5. Update `queries/todo.md` with remaining work

For **selective exclusion within a symlinked directory** (e.g. exclude `Qt/` from `programming/`):
- Remove the parent directory symlink
- Recreate it as individual symlinks for each item, skipping excluded ones
- Use Python `os.listdir()` + `os.symlink()` to handle special characters in filenames
- Document excluded items in `.rawlenses`

## 5. Git Initialization

After the wiki has content:
```bash
cd ~/hermes/wiki
git init
cat > .gitignore << 'EOF'
raw/                    # symlinks to source, not tracked
*.swp *.swo *~
.DS_Store
.obsidian/              # editor config
EOF
git add .
git commit -m "init"
```

## Pitfalls

- **Read-only source filesystem**: `rm` on symlinks pointing into a read-only mount will fail. Remove the symlink itself (its path is on the writable home FS), not the target. Use `unlink` or absolute paths.
- **Special characters in filenames**: Chinese chars, `~`, `'`, parens in filenames break shell quoting. Use `os.symlink()` in Python, not shell `ln`.
- **Deeply nested build artifacts**: `.o` / `.swp` files inside otherwise valuable source trees. Don't try to filter per-directory; document patterns in `.rawlenses` and rely on find filters.
- **Large HTML archives**: saved web pages from saved-for-later reading can dominate file counts (34K HTML files in a 58K collection). This is normal — the wiki indexes them, it doesn't need to open them all.
- **Symlink traversal**: `cd ~/hermes/wiki/raw/programming/` follows symlink into source FS. Always use absolute paths or work from the wiki root.
