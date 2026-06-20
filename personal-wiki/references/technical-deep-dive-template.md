# Technical Deep-Dive Concept Page Template

Use this when filling an empty stub with substantive domain knowledge — architecture breakdowns, standards, algorithms, protocols, frameworks, or methodologies. This pattern was used across 20+ pages (AUTOSAR, functional safety, ISO 26262, MISRA, embedded systems, systems engineering, hypervisor, RTOS scheduling, etc.) in a wiki-filling session.

## Template

```markdown
---
title: Topic Name (中英文)
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: raw/xxx/
status: growing
---

## 概述

What this is, why it matters, key context (2-4 sentences).

## Architecture / Structure

A diagram (ASCII art or table) showing the layered/component structure:

```
┌──────────────────┐
│ Top Layer        │ ← purpose
├──────────────────┤
│ Middle Layer     │ ← purpose
├──┬──┬──┬────────┤
│A │B │C │D       │ ← sub-components
└──┴──┴──┴────────┘
```

## Core Concepts / Key Sections

### Sub-topic A

Explain this component/concept. Use tables for structured data:

| Item | Description | Detail |
|------|-------------|--------|
| Key term | What it means | Specifics |

### Sub-topic B

Continue breaking down the topic. Include decision trees, comparison tables, or flow charts as appropriate.

## Practical Details

Code examples, command snippets, formulas, or configuration patterns:

```c
// Example showing practical usage
void example() { ... }
```

## Version History / Evolution (if applicable)

| Version | Year | Key Changes |
|---------|------|-------------|
| v1.0 | YYYY | What changed |

## Knowledge Base Files

- [Source documents](raw/xxx/) — N files, N MB

## 相关页面 (Related Pages)

- [[concepts/related-a]]
- [[concepts/related-b]]
- [[comparisons/related-c]]
```

## Key Principles

1. **Self-contained** — reader should understand the concept without consulting raw/ docs
2. **Structured** — use ASCII diagrams, tables, and bullet lists over long prose
3. **Cross-linked** — every page links to related concepts, entities, and comparisons
4. **Practical** — include code snippets, command examples, formulas where they add value
5. **Level-appropriate** — don't recapitulate a textbook; provide a structured reference an experienced engineer can quickly scan and map to their own knowledge
6. **Chinese titles with English key terms** — natural bilingual presentation
7. **Status: growing** — mark as `growing` (not `mature`) so future sessions know more can be added

## When to Use

Use this template when:
- The page topic is a well-known technical concept (agent can synthesize from training data)
- The index.md already lists the page with a clear topic description
- You're filling an empty stub, not a raw/ directory index

Do NOT use this when:
- The page is a raw-navigation index (use Concept Page / Navigation Index template instead)
- The content requires reading specific PDFs from the collection (use delegate_task book reading + reading note template)

## Anti-Patterns to Avoid

- **Writing stubs that just say "TODO"** — always include substantive content even if incomplete
- **Linking only to raw/ without synthesis** — agent knowledge is the primary source, raw/ links are supplementary
- **Over-compartmentalizing** — if two concepts are tightly coupled, prefer one deeper page over two shallow ones
- **Skipping the architecture diagram** — ASCII art or tables with structural breakdowns are the single most valuable element of a technical reference page
