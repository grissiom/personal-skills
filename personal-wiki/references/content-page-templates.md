# Content Page Templates (from real session)

Templates for the four page types in a personal knowledge wiki, extracted from a session that created 29 pages across 5 domains.

## Concept Page (Navigation Index Pattern)

Use for domain-level indexes (programming, OS, automotive, protocols, etc.).

```markdown
---
title: Domain Title (中英文)
tags: [tag1, tag2]
created: YYYY-MM-DD
status: growing
source: raw/xxx/
---

## 概述

Brief description. Total: N files, N MB.

## Subdirectory Index

| 目录 | 说明 | 链接 |
|------|------|------|
| Topic A | 2-line description | [raw/A/](raw/A/) |
| Topic B | 2-line description | [raw/B/](raw/B/) |

## Related Concepts

- [Concept A](concepts/concept-a.md)
- [Concept B](entities/entity-b.md)
```

## Entity Page (Person/Technology)

```markdown
---
title: Name
tags: [人物/技术, category]
created: YYYY-MM-DD
status: stub
source: raw/xxx/
---

## 概况

1-2 sentence description.

## Related Resources

- Source documents: `raw/xxx/` — N files, N MB
```

## Comparison Page (Table Pattern)

```markdown
---
title: Title Comparison
tags: [对比, tag1, tag2]
created: YYYY-MM-DD
status: stub
source: raw/xxx/
---

| 维度 | Option A | Option B |
|------|----------|----------|
| Hardware target | MCU | SoC/MPU |
| OS | OSEK RTOS | POSIX (Linux) |
| Language | C | C++ |
| Update | Static flash | OTA |
| Communication | CAN/LIN | SOME/IP, Ethernet |

## Related Pages

- [Page A](concepts/page-a.md)
```

## Book List Page (Reading Collection Pattern)

```markdown
## History

| Title | Author | Format | Link |
|-------|--------|--------|------|
| Book Name | Author | PDF | [link](raw/life/file.pdf) |
```

Group by category (History, Economics, Philosophy, etc.) and include author + format columns.

## Technical Deep-Dive Page

For substantive domain pages with architecture breakdowns, standards, algorithms, and practical details. See `references/technical-deep-dive-template.md` for the full template with examples from a session that filled 20+ pages (AUTOSAR, functional safety, ISO 26262, MISRA, hypervisor, RTOS scheduling, etc.).
