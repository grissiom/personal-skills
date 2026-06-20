# Wiki Page Templates

## Concept Index Page (concepts/)

```markdown
---
title: Domain Name (中英双语)
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
status: growing
source: raw/path/
---

## 概述

Brief overview of the domain. Include file count and size if relevant.

## Subdirectory Index

| Subdir | Description | Link |
|--------|-------------|------|
| Topic A | What it is | [raw/path/A/](raw/path/A/) |
| Topic B | What it is | [raw/path/B/](raw/path/B/) |

## Key References

| Title | Author/Version | Format | Link |
|-------|---------------|--------|------|
| Book X | Author Y | PDF | [raw/.../file.pdf](raw/.../file.pdf) |

## Related Pages

- [Related Concept](concepts/related.md)
- [Related Entity](entities/related.md)
```

## Reading Notes Page (concepts/)

```markdown
---
title: 读书笔记：Book Title
tags: [读书笔记, topic1, topic2]
created: YYYY-MM-DD
status: growing
source: raw/path/to/book.pdf
---

## Basic Info

- Title, Author, Edition, Format
- Pages, Source link

## Core Thesis

One-paragraph summary of the central argument.

## Structure / Chapter Breakdown

| Chapter | Theme | Key Point |
|---------|-------|-----------|
| 1 | Topic | Fallacy analysis |
| 2 | Topic | Alternative view |

## Key Quotes and Arguments

### Quote/Argument Name
Analysis of the argument in context.

## Related Pages
```

## Entity Page (entities/)

```markdown
---
title: Person/Technology Name
tags: [tag1, tag2]
created: YYYY-MM-DD
status: stub
source: raw/path/
---

## Overview

Brief description.

## Key Resources

| Resource | Link |
|----------|------|
| Description | [raw/path/](raw/path/) |

## Related Pages
```

## Comparison Page (comparisons/)

```markdown
---
title: Technology A vs Technology B
tags: [对比, tag1, tag2]
created: YYYY-MM-DD
status: stub
---

## Comparison Table

| Dimension | Option A | Option B |
|-----------|----------|----------|
| Feature 1 | Value | Value |
| Feature 2 | Value | Value |

## Related Pages
```
