# Reading Note Creation (Real Session Example)

Based on a session that created a 4,800-word structured reading note for Hazlitt's *Economics in One Lesson* (432 pages, Chinese PDF).

## Workflow

```bash
# 1. Check book metadata
pdfinfo "/media/grissiom/Docs/一课经济学.pdf" | grep -iE 'title|author|pages|subject'
# Output: Author: AZ, Pages: 432

# 2. Extract full text (handles Chinese PDFs too)
pdftotext "/media/grissiom/Docs/一课经济学.pdf" /tmp/book.txt

# 3. Read the table of contents (first 30 lines)
grep -n "^第\|^前\|^附\|目录\|CONTENTS" /tmp/book.txt | head -30

# 4. Read key chapters via line ranges
sed -n 'LINES_START,LINES_ENDp' /tmp/book.txt   # preface
# For a 432-page Chinese book, expect ~6,000-7,000 lines of extracted text
# Page 1 ≈ line 14-16

# 5. Core thesis extraction - read chapter 1 and the conclusion
# These are the most important sections for the reading note
```

## Page Structure

```markdown
---
title: 读书笔记：中文名 (English Title)
tags: [读书笔记, domain, author]
created: YYYY-MM-DD
status: growing
source: raw/xxx.pdf
---

## 基本信息

- **原书名**：English Title
- **作者**：Author
- **首版**：Year
- **修订版**：Year (if applicable)
- **页数**：N
- **核心影响**：Other thinkers that influenced/inspired this work
- **源文件**：[raw/xxx.pdf](raw/xxx.pdf)

## 核心论点

2–3 paragraph summary of the central thesis. Include a direct quote of the book's core insight if the text is clear.
Explain the key analytical framework/method the author uses throughout the book.

## 章节结构与各章要点

| 章 | 主题 | 核心谬误/论点 |
|----|------|--------------|
| 1 | Chapter title | Core argument of this chapter |

Group into thematic sections if the book has natural groupings (e.g., "Basic Fallacies", "Government Intervention", "Macro").

## 经典论点摘录

Thematic subheadings with:
- The scenario/fallacy the author addresses
- The "seen" (obvious) vs "unseen" (hidden) consequences
- The author's conclusion

## 历史地位与评价

- Field context
- Influence on later work
- Common criticisms (if known)

## 延伸阅读

- Related wiki pages
- Other books in the collection on the same topic
```

## Pitfalls

- **Garbled OCR**: Chinese PDFs (especially pre-2010 scans) may produce garbled characters from poor OCR. Read the table of contents structure (chapter numbers are usually readable) and infer chapter themes from context.
- **Line count estimation**: 432 Chinese text pages ≈ 6,000-7,000 lines of pdftotext output. To estimate: pages × 15-18 lines/page.
- **Missing chapter titles**: In garbled text, the chapter numbering (第N章) is usually intact even when the title is garbled. Cross-reference with the book's known chapter structure.
- **Don't over-quote**: Extract key arguments in your own words with short supporting quotes. A reading note should be self-contained.
- **State what's excluded**: If the PDF is too garbled to read fully, note this and summarize from what is readable.
- **EPUB vs PDF**: For `.epub` books, extract TOC via Python `zipfile` (see SKILL.md for code). The TOC is always correct (not OCR-dependent). Content extraction is harder — you may need to parse `.xhtml` files inside the archive.
- **Multiple formats**: Some books exist in both PDF and EPUB. Prefer EPUB for TOC accuracy, PDF for page-level quoting.
