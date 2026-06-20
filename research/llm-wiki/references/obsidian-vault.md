# Obsidian Vault Integration

The wiki directory works as a fully-featured Obsidian vault. This reference
covers file-tool workflows for reading, searching, and editing the wiki
through Obsidian's lens.

## Vault Path

Set via `OBSIDIAN_VAULT_PATH` env var, or default to `~/Documents/Obsidian Vault`.
For llm-wiki integration, `OBSIDIAN_VAULT_PATH` should point to the same
directory as `$WIKI_PATH`.

## Reading Notes

```python
read_file(path="$WIKI/entities/my-page.md")
```

Prefer `read_file` over `cat` — it provides line numbers and pagination.

## Listing Notes

```python
search_files(pattern="*.md", target="files", path="$WIKI/entities")
```

Prefer `search_files` over `find` or `ls`.

## Searching Note Contents

```python
search_files(pattern="transformer", path="$WIKI", file_glob="*.md")
```

## Creating a Note

```python
write_file(path="$WIKI/entities/new-topic.md", content="""---
title: New Topic
created: 2026-01-01
updated: 2026-01-01
type: entity
tags: [tag1]
sources: []
---

# New Topic

First paragraph here.
""")
```

## Appending to a Note

1. Read the target with `read_file`
2. Use `patch` with stable context (e.g., add after a known heading)
3. For simple end-of-file appends, `terminal` is acceptable if file-tool
   approaches are awkward

## Targeted Edits

Use `patch` for focused changes when you have stable context.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating wiki pages,
always use wikilinks to connect related content (minimum 2 outbound links
per page per SCHEMA.md conventions).

## Linked Images

Obsidian embeds images with `![[image.png]]`. Store images in `raw/assets/`
and reference them with this syntax.
