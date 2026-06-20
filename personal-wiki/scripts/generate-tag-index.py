#!/usr/bin/env python3
"""Generate a tag-index.md for a personal knowledge wiki.

Scans all .md files (excluding raw/ and .git/), extracts YAML frontmatter
title and tags, and writes a cross-reference table to <wiki>/concepts/tag-index.md.

Usage:
    python generate-tag-index.py /path/to/wiki
"""

import os
import re
import sys


def extract_frontmatter(path: str) -> tuple[str | None, list[str]]:
    """Return (title, tags_list) from a markdown file's YAML frontmatter."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()

    title_m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else None

    tags_m = re.search(r"^tags:\s*\[(.+)\]$", content, re.MULTILINE)
    tags = []
    if tags_m:
        for t in tags_m.group(1).split(","):
            t = t.strip()
            if t and t not in ("标签1", "标签2"):  # skip template placeholders
                tags.append(t)
    return title, tags


def main():
    if len(sys.argv) < 2:
        print("Usage: generate-tag-index.py <wiki_path>")
        sys.exit(1)

    wiki = os.path.abspath(sys.argv[1])

    # Collect all pages and their tags
    tag_index: dict[str, list[tuple[str, str]]] = {}  # tag -> [(rel_path, title)]

    for root, dirs, files in os.walk(wiki):
        # Skip hidden dirs (.git, .obsidian) and raw/ (symlinks to source)
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "raw"]
        if ".git" in root or ".obsidian" in root:
            continue

        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, wiki)

            title, tags = extract_frontmatter(path)
            label = title or rel

            for tag in tags:
                tag_index.setdefault(tag, []).append((rel, label))

    # Build the tag-index page
    lines = [
        "---",
        "title: 标签索引",
        "tags: [导航, 标签, 索引]",
        f"created: {__import__('datetime').date.today().isoformat()}",
        "status: growing",
        "---",
        "",
        "## 按标签浏览",
        "",
        f"共 {len(tag_index)} 个标签，覆盖 {sum(len(v) for v in tag_index.values())} 个页面",
        "",
        "| 标签 | 页面数 | 页面 |",
        "|------|--------|------|",
    ]

    for tag in sorted(tag_index.keys()):
        entries = tag_index[tag]
        links = ", ".join(f"[{t}]({p})" for p, t in entries)
        lines.append(f"| `{tag}` | {len(entries)} | {links} |")

    output = "\n".join(lines) + "\n"

    out_path = os.path.join(wiki, "concepts", "tag-index.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(output)

    print(f"✓ Written {len(tag_index)} tags ({sum(len(v) for v in tag_index.values())} pages) → {out_path}")


if __name__ == "__main__":
    main()
