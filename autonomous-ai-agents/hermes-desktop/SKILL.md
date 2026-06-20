---
name: hermes-desktop
description: "Build, launch, and troubleshoot the Hermes Electron desktop app — Node.js requirements, sandbox configuration, PATH handling, and common build failures."
category: autonomous-ai-agents
---

# Hermes Desktop

Build, launch, and troubleshoot the Hermes Electron desktop app (`hermes desktop` / `hermes gui`). The desktop app is a native Electron wrapper around the Hermes agent core, built from `apps/desktop/` in the hermes-agent repo.

## Triggers

- User runs `hermes desktop` or `hermes gui` and it fails
- User asks to install, build, or set up Hermes Desktop
- `npm WARN EBADENGINE` or `npm ERR!` during `hermes desktop`
- "chrome-sandbox" or "sudo" errors during launch
- Node.js version complaints

## Quick Start

```bash
# Ensure Node.js >= 20 is on PATH (v23+ recommended)
export PATH="$HOME/.local/nodejs/bin:$PATH"
node --version  # must be >= 20

# Full build + launch
hermes desktop

# Skip build if already built (e.g. after manual sandbox fix)
hermes desktop --skip-build
```

## Node.js Version Requirement

`hermes desktop` and its dependencies require **Node.js >= 20** (v23+ recommended). Several npm packages in the dependency tree demand `^20.19.0 || >=22.12.0`.

**Diagnostic signal:** `npm WARN EBADENGINE Unsupported engine` messages during build, listing packages like `@shikijs/core@4.2.0`, `@electron/rebuild@4.0.4`, `hermes@0.15.1` all requiring `node >= 20`.

If the system Node.js is too old but a newer one is installed at a custom path (e.g. `~/.local/nodejs/bin/`), make sure that path comes **first** in `$PATH` before running any hermes desktop commands:

```bash
export PATH="$HOME/.local/nodejs/bin:$PATH"
```

The `~/.bashrc` export is NOT automatically available in Hermes tool sessions — you must re-export in the current session or prefix every `hermes desktop` invocation.

## Build Pipeline

`hermes desktop` (implemented in `hermes_cli/main.py::cmd_gui`) runs these steps:

1. **`npm ci`** — install workspace dependencies from the repo root
2. **`npm run build`** (source) or **`npm run pack`** (packaged) — esbuild the frontend, then electron-builder
3. **`_desktop_linux_sandbox_fixup()`** — setuid-root the `chrome-sandbox` binary (Linux only)
4. **Launch** — spawn the packaged executable

Use `--skip-build` to jump to step 3–4 when the build is already current.

## chrome-sandbox (Linux Only)

Electron's Linux sandbox requires `chrome-sandbox` to be owned by root with setuid (`chmod 4755`). The build places it at:

```
apps/desktop/release/linux-unpacked/chrome-sandbox
```

The fixup function (`_desktop_linux_sandbox_fixup` at line 5330 of `hermes_cli/main.py`) checks:
- File exists and is a regular file (not a symlink — security check)
- Already `root:root` with mode `0o4755` → skips
- Otherwise runs: `sudo chown root:root <path>` then `sudo chmod 4755 <path>`

**Pitfall: sudo needs a TTY.** When `hermes desktop` is run from within a Hermes agent session (via the `terminal` tool), `sudo` fails with "a terminal is required to read the password". The build succeeds but launch is blocked.

**Workflow when this happens:**

```bash
# 1. The user runs these manually in a real terminal:
sudo chown root:root ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
sudo chmod 4755 ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox

# 2. Then launch with --skip-build (no rebuild needed):
export PATH="$HOME/.local/nodejs/bin:$PATH"
hermes desktop --skip-build
```

Once the sandbox is configured, it persists across rebuilds (same path). Future `hermes desktop` invocations will detect the correct permissions and skip sudo.

## Common Flags

| Flag | Purpose |
|------|---------|
| `--skip-build` | Launch existing build; skip npm install + electron-builder |
| `--force-build` | Rebuild even if content stamp matches |
| `--build-only` | Build artifact, don't launch (used by auto-updater) |
| `--source` | Launch via `electron .` against dist/ instead of packaged app |

## Making Node.js PATH Permanent

The `export PATH="$HOME/.local/nodejs/bin:$PATH"` in `~/.bashrc` only applies to interactive bash shells. For it to work across **all** shell types (login shells, cron, new terminal tabs, Hermes agent sessions), add it to `~/.profile` as well:

```bash
# Add near other PATH exports in ~/.profile
echo 'export PATH="$HOME/.local/nodejs/bin:$PATH"' >> ~/.profile
```

`~/.profile` is sourced by login shells, and its environment is inherited by all child processes — including the terminal emulator, every shell inside it, and the Hermes CLI.

## Linux Desktop Registration

After building, register Hermes Desktop in the application menu by creating a `.desktop` file and installing icons:

### Icon Installation (non-AppImage approach)

Electron apps ship a single large icon. Resize to hicolor sizes with PIL:

```bash
python3 -c "
import os
from PIL import Image
HOME = os.environ['HOME']
img = Image.open(f'{HOME}/.hermes/hermes-agent/apps/desktop/assets/icon.png')
for size in [16, 24, 32, 48, 64, 128, 256, 512]:
    d = f'{HOME}/.local/share/icons/hicolor/{size}x{size}/apps'
    os.makedirs(d, exist_ok=True)
    img.resize((size, size), Image.LANCZOS).save(f'{d}/hermes-desktop.png')
"
```

### Desktop Entry

```ini
[Desktop Entry]
Type=Application
Name=Hermes Desktop
GenericName=AI Agent
Comment=Hermes AI Agent — autonomous coding and task-execution assistant
Exec=/home/$USER/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/Hermes
Icon=hermes-desktop
Terminal=false
Categories=Development;
Keywords=hermes;ai;agent;assistant;coding;
StartupWMClass=Hermes
```

Validate and refresh:
```bash
desktop-file-validate ~/.local/share/applications/hermes-desktop.desktop
update-desktop-database ~/.local/share/applications/
```

For full details, load the `linux-desktop` skill.

## Pitfalls

- **System Node.js too old.** Check `node --version` before troubleshooting anything else. The `EBADENGINE` warnings are the canary.
- **Custom Node.js PATH not active in Hermes session.** `~/.bashrc` exports are not sourced by the Hermes agent process. Add the PATH to `~/.profile` for permanent coverage (see above). For immediate fix: `export PATH="$HOME/.local/nodejs/bin:$PATH"`.
- **chrome-sandbox sudo fails silently** when run from within Hermes. Tell the user to run the two sudo commands manually in their own terminal.
- **Build succeeds but launch fails at the sandbox step** — the error message is "Failed to configure Electron's Linux sandbox helper". The fix is manual sudo, not a rebuild.
- **`--skip-build` still checks sandbox.** Even with `--skip-build`, the `_desktop_linux_sandbox_fixup()` runs and blocks launch on sudo failure. The flow is: build → sandbox check → launch. `--skip-build` only skips step 1–2 (npm + electron-builder), not step 3 (sandbox).
