# Concepts Tree Restructuring — Case Study (2026-06-20)

Session: ~/hermes/wiki restructured from 69 flat `.md` → 11 subdirectories.

## Mapping Used

```
concepts/
├── ai-agent/          agi, agentic-ai-cpu-bottleneck, claude-code-expertise,
│                      how-llms-actually-work, ai-agent-tech-report-2026-06   (5)
├── ai-hardware/       ai-hardware-automotive-soc-2025-2026,
│                      top3-ad-chips-comparison, m100-orchestrated-dataflow   (3)
├── automotive/        autosar*, aspice, iso-26262, functional-safety,
│                      asam-mcd, misra, automotive-*                         (10)
├── embedded/          embedded-systems, linux-kernel, rtos-*, ebpf,
│                      hypervisor, operating-systems, ros, sel4              (8)
├── programming/       programming, computer-science, character-encoding,
│                      rest-fielding, protocols, misc-tech                    (6)
├── software-engineering/ software-engineering, clean-coder, code-complete,
│                      mythical-man-month, philosophy-software-design,
│                      patterns-of-software, unix-programming-art,
│                      open-source, systems-engineering, google-monorepo     (10)
├── hardware/          cpu-architecture, hardware-design                     (2)
├── coolshell/         coolshell + 5 提炼                                    (6)
├── books/             reading-list + 12 读书笔记                            (13)
├── meta/              glossary, tag-index, tool-manuals                     (3)
└── misc/              science, aerospace, english-learning, godel,
                       misc-management-quality                                (5)
```

## Pitfalls Encountered

### 1. `sed` with wikilinks needs `\|` for literal pipes
When using `sed` to add `concepts/subdir/` prefixes to bare wikilinks like
`[[software-engineering|软件工程]]`, the `|` must be escaped — otherwise it becomes
regex alternation (in ERE) or conflicts with the `|` delimiter.
```bash
# WORKS — non-pipe delimiter (@) + escaped pipe (\|) in BRE mode:
sed 's@\[\[software-engineering\|软件工程\]\]@[[concepts/.../software-engineering|软件工程]]@g'
# BROKEN — pipe delimiter + unescaped pipe in pattern:
sed 's|\[\[software-engineering|软件工程\]\]|[[...]]|g'
```
**Fix:** Use `execute_code` with Python regex for complex bulk rewrites (handles edge
cases more reliably), or escape `|` as `\|` with a non-pipe delimiter in `sed`.
Without escaping, the `|` separator gets dropped, turning
`[[software-engineering|软件工程]]` into `[[concepts/software-engineering/software-engineering软件工程]]`.

### 2. Renamed file breaks old references
`management-quality.md` → `misc/misc-management-quality.md` caused 5 broken wikilinks
across README.md, index.md, queries/todo.md, and two concept pages. Always grep for
the old filename after renaming, across ALL `.md` files.

### 3. Wiki pages can have bare wikilinks (no `concepts/` prefix)
Files inside `concepts/` sometimes use bare `[[software-engineering]]` instead of
`[[concepts/software-engineering]]`. These become broken when the file moves to a
subdirectory. Need a second-pass regex to catch and prefix these.

### 4. `sed` over multiple files needs exact match
`sed -i 's|old|new|g' file1 file2` is safer than piping through `while read`,
but always verify with `grep` after. Orders of magnitude faster than individual
`patch` calls for bulk replacements.

## Successful Pattern

The whole operation (67 files moved, 70 files updated, 500+ wikilinks fixed)
completed in 2 `execute_code` calls:
1. Move files + global wikilink rewrite (Python `shutil.move` + `re.sub`)
2. Fix remaining 4 root-level files + second-pass regex

This is the recommended approach — `execute_code` with Python handles pipes,
subdirectories, and edge cases far more reliably than shell `sed` pipelines.
