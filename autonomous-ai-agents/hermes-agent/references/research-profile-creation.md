# Creating a Research Profile

Proven workflow for creating a dedicated Hermes profile for research/monitoring tasks.

## Step 1: Create the profile

```bash
hermes profile create <name> --clone  # clones default profile's config + .env
```

## Step 2: Write SOUL.md

`~/.hermes/profiles/<name>/SOUL.md` defines the persona. Structure:

```markdown
## 身份定位
One-paragraph identity statement.

## 核心研究领域
Numbered sections with specific companies, tools, trends to track.

## 信息源分级
Table: 🥇 primary (official blogs, papers) → 🥈 secondary → 🥉 reference

## 核心监控源（必查）
List of URLs the agent MUST check during each analysis.

## 分析与输出规范
- Report structure (TL;DR → findings → details → recommendations)
- Output format (tables, confidence markers, language)
- Weekly/monthly report templates

## 快捷指令
Table mapping user commands to agent actions.

## 交互风格
Tone, language, output preferences.
```

## Step 3: Tailor config.yaml

Key settings for research profiles:

```yaml
agent:
  max_turns: 120          # Give more turns for deep research
  reasoning_effort: "high" # Better analysis quality
  environment_hint: "..."  # Remind the agent of its role
display:
  compact: true
  personality: "researcher"
  language: "zh"
memory:
  memory_char_limit: 4000  # More space for research notes
delegation:
  max_iterations: 100      # Allow deeper subagent research
```

## Step 4: Copy .env

```bash
cp ~/.hermes/.env ~/.hermes/profiles/<name>/.env
```

## Step 5: Set up cron jobs

At minimum, two recurring jobs:

1. **Weekly roundup** — scan key sources, generate a structured report
2. **Monthly deep-dive** — trend analysis, competitive matrix, ecosystem map

Optional: a one-shot **initial analysis** job to populate memory with baseline data.

Cron job config recommendations:
- `profile: <name>` to run under the research profile
- `enabled_toolsets: ["web", "file", "terminal"]` (web_search for scanning blogs)
- `deliver: "local"` (save to workspace, don't send to chat platforms)

## Step 6: Create workspace directories

```bash
mkdir -p ~/.hermes/profiles/<name>/workspace/{weekly-reports,monthly-reports,notes}
```

## Step 7: Create alias and test

```bash
hermes profile alias <name>          # creates ~/.local/bin/<name>
<name> -q "本周动态"                  # test with a single query
```
