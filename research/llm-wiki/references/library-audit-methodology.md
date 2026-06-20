# Library Audit Methodology

When a user asks to initialize a wiki from an existing document library on disk,
this reference defines the audit process to classify content and identify what
to include, exclude, or flag for user decision.

## Audit Phases

### Phase 1: Size the Library

```bash
SRC_DIR="/path/to/docs"

# Total file count
find "$SRC_DIR" -type f | wc -l

# Total size
du -sh "$SRC_DIR"

# Directory sizes (sorted by size)
du -sh "$SRC_DIR"/*/ 2>/dev/null | sort -rh | head -40
```

### Phase 2: Profile File Types

```bash
# All file extensions (across entire tree)
find "$SRC_DIR" -type f | awk -F. '{print tolower($NF)}' | sort | uniq -c | sort -rn | head -30

# Per-directory file types (for big dirs)
for d in programming linux OS CPU; do
  find "$SRC_DIR/$d" -type f | awk -F. '{print tolower($NF)}' | sort | uniq -c | sort -rn | head -10
done
```

### Phase 3: Locate Garbage Patterns

| Pattern | How to count | How to confirm |
|---------|-------------|----------------|
| `Thumbs.db` | `find "$SRC_DIR" -name 'Thumbs.db' -type f \| wc -l` | Windows thumbnail cache |
| `*.o` | `find "$SRC_DIR" -name '*.o' -type f \| wc -l` | Compiled object files |
| `*.swp` | `find "$SRC_DIR" -name '*.swp' -type f \| wc -l` | Vim swap files |
| `*.tmp` | `find "$SRC_DIR" -name '*.tmp' -type f \| wc -l` | Temp files |
| `.git/` | `find "$SRC_DIR" -name '.git' -type d \| wc -l` | Git repos embedded in SDKs |
| `.DS_Store` | `find "$SRC_DIR" -name '.DS_Store' -type f \| wc -l` | macOS folder metadata |

Also check for build-system artifacts specific to the user's domain:
- `.uvproj` / `.uvopt` — Keil uVision IDE
- `.ewp` / `.ewd` / `.eww` / `.icf` — IAR Embedded Workbench
- `.dcd` / `.dii` — ASAM GDI companion files (automotive standard)
- `.a` / `.lib` / `.so` — compiled libraries

### Phase 4: Classify Directories

For each directory, assess:

```
<dir-name> | <file-count> | <size> | <category> | <wiki-value>
```

**Categories:**
- **tech-doc** — programming, CS, protocols, OS, CPU, linux → keep
- **domain-eng** — CAR, radar, GMSL, PCIe, electrical design → keep
- **reference** — NASA_standards, Quality Management, RFC → keep
- **education** — english, GRE, TOEFL, 从心理解孩子 → keep
- **humanities** — 王陶陶, 唯为, 美君, history, 晚清沧海事 → keep
- **personal-archive** — HJH (with personal videos/resume) → FLAG FOR USER
- **tools** — Jenkins (website dump), software_menual → keep
- **sdk-bsp** — CPU/MIPS/Loongson (source code + build artifacts) → keep but note noise
- **empty** — no files → harmless symlink

### Phase 4.5: Scan for Personal/Private Content

Before presenting the summary, proactively search for personal documents hidden
inside otherwise innocuous directory names. A directory named after a person's
handle (e.g., `Gri/`, a contraction of the username) may contain private files.

```bash
# Chinese document patterns — common in bilingual document libraries
find "$SRC_DIR" -iname '*简历*' -o \
                -iname '*体检*' -o \
                -iname '*公积金*' -o \
                -iname '*合同*' -o \
                -iname '*协议*' -o \
                -iname '*身份证*' -o \
                -iname '*护照*' 2>/dev/null | head -10

# English patterns
find "$SRC_DIR" -iname '*resume*' -o \
                -iname '*cv*' -o \
                -iname '*medical*' -o \
                -iname '*salary*' -o \
                -iname '*contract*' -o \
                -iname '*passport*' -o \
                -iname '*nd[a]*' 2>/dev/null | head -10

# Personal photo/media — QQ photos, family pics
find "$SRC_DIR" -iname '*qq*photo*' -o \
                -iname '*selfie*' -o \
                -iname '*全家福*' 2>/dev/null | head -10
```

When hits are found, examine the containing directory — it may be an entire
personal folder. Flag these for user decision: "是知识还是回忆？" (Is this
knowledge or personal memory?)

**Important:** These scans can produce false positives. A "协议" (protocol/
agreement) match in a technical directory like `protocols/CAN/UDS/` is a
technical document about diagnostic protocols, not a personal contract. Always
check the full path and context before flagging.

### Phase 5: Identify Edge Cases for User Decision

Things that aren't obviously in or out:

1. **Personal media** — family videos, resumes, personal photos mixed into a
   shared Docs drive. Ask: "是知识还是回忆？"

2. **Large archives** — zip/tar.gz files whose contents are unknown. A 114MB
   `选择突破口 (1).zip` in a history folder could be books or could be junk.

3. **Website mirrors** — full HTML dumps of old documentation sites (e.g.,
   Jenkins CI docs at 84MB). Usually stale, but the user may want to keep them
   for offline reference.

4. **SDK/BSP source trees** — full embedded project directories with source code,
   build artifacts, IDE configs. The prose documentation within is valuable,
   but the compiled objects and swap files are noise.

### Phase 6: Present Summary

Format:

```
Source: <path> (<size>, <N> files in <N> directories)

In scope (auto-include):
  <category> — <N dirs> — <description>
  ...

Garbage found:
  Thumbs.db: <N>
  *.o: <N>
  ...

Needs decision:
  <dir> — <reason> — <N files> — <size>

Recommendation: include all, skip garbage, ask about <N> edge cases.
```

## Committing Decisions

After user confirms scope:

- In memory, record: source path, included/excluded dirs, garbage count, date
- In log.md: `## [YYYY-MM-DD] init | Symlink wiki from <src>`
- Include the exclusion rationale so a future user (or agent) understands why
  something was skipped and can reverse the decision
