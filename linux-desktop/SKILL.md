---
name: linux-desktop
description: "Linux desktop integration: .desktop files, AppImage registration, IME/Wayland troubleshooting."
category: devops
---

# Linux Desktop Integration & Troubleshooting

Register applications in the Linux desktop and fix input method issues on Wayland.

## 1. Desktop Entry Registration

Create `.desktop` files under `~/.local/share/applications/` with icons under `~/.local/share/icons/hicolor/`.

### Quick Recipe (AppImage)

```bash
# Extract AppImage icons (full extraction — not partial)
cd /tmp && /path/to/AppImage --appimage-extract

# Install icons at all sizes
for f in $(find squashfs-root -name '*.png' -path '*/icons/hicolor/*/apps/*'); do
  size=$(echo "$f" | grep -oP '/\d+x\d+/')
  mkdir -p ~/.local/share/icons/hicolor/$size/apps/
  cp "$f" ~/.local/share/icons/hicolor/$size/apps/
done
```

### Quick Recipe (Single PNG — Electron / non-AppImage apps)

When the app provides only one large icon (e.g. `assets/icon.png` at 1024x1024), resize with PIL and install to all hicolor sizes:

```bash
python3 -c "
import os
from PIL import Image
HOME = os.environ['HOME']
img = Image.open('/absolute/path/to/icon.png')
for size in [16, 24, 32, 48, 64, 128, 256, 512]:
    d = f'{HOME}/.local/share/icons/hicolor/{size}x{size}/apps'
    os.makedirs(d, exist_ok=True)
    img.resize((size, size), Image.LANCZOS).save(f'{d}/<icon-name>.png')
    print(f'  {size}x{size} done')
"
```

Replace `/absolute/path/to/icon.png` and `<icon-name>` with actual values. No need to run `gtk-update-icon-cache` — KDE and GNOME pick up new icons from hicolor within a few seconds.

### Create Desktop Entry & Validate

```bash
# Create .desktop file
cat > ~/.local/share/applications/<app>.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=<App Name>
Exec=/absolute/path/to/binary
Icon=<icon-basename-no-ext>
Terminal=false
Categories=Utility;
EOF

# Validate and refresh
desktop-file-validate ~/.local/share/applications/<app>.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
```

### Key Rules
- **Exec** MUST be absolute path. Add flags like `--no-sandbox` for Electron apps.
- **Icon** is bare filename without extension.
- **Categories** — exactly ONE main category. Non-standard ones must start with `X-`.
- **Terminal** — `false` for GUI, `true` for CLI/TUI.
- **StartupWMClass** — set for proper window grouping (often the app name lowercased).

→ **Full details + AppImage:** `references/linux-desktop-integration.md`
→ **AppImage-specific:** `references/appimage-desktop-integration.md`
→ **Obsidian worked example:** `references/obsidian-desktop-template.md`

## 2. IME on Wayland (fcitx5/ibus)

Diagnose and fix Chinese/Japanese/Korean input method issues on Wayland.

### Diagnosis
```bash
fcitx5 --version
echo $XDG_SESSION_TYPE
fcitx5-diagnose 2>/dev/null | grep -E 'program:|frontend:|cap:' | head -30
```

### Chrome/Chromium on KDE Plasma (KWin)
**Symptom:** Preedit auto-commits in dialogs, or IME doesn't trigger.

**Fix A:** Force text-input-v1:
```
--enable-wayland-ime --wayland-text-input-version=1
```
Apply via `~/.local/share/applications/google-chrome.desktop` override. Must fully quit Chrome.

**Fix B:** Fall back to XWayland: `--ozone-platform=x11` + `GTK_IM_MODULE=fcitx`

**Fix C:** GTK4 IM module: `--gtk-version=4` + `GTK_IM_MODULE=fcitx`

### Electron Apps (VS Code, Discord)
```
code --enable-features=UseOzonePlatform --ozone-platform=wayland --enable-wayland-ime
```

### Environment Variables Quick Reference
| Variable | When to set |
|----------|------------|
| `GTK_IM_MODULE=fcitx` | GTK apps under X11/XWayland; wayland text-input broken |
| `QT_IM_MODULE=fcitx` | Qt5 under Wayland on non-KDE compositors |
| `QT_IM_MODULES="wayland;fcitx"` | Qt 6.8.2+ fallback chain |
| `XMODIFIERS=@im=fcitx` | XWayland apps |
| (unset) | KDE Plasma — KWin handles text-input natively |

→ **Full IME diagnosis:** `references/linux-ime-wayland.md`
→ **Chrome KWin template:** `references/chrome-kwin-desktop-template.md`

## Pitfalls

- **AppImage partial extraction fails** — `--appimage-extract <single-file>` only extracts symlinks. Always do full extraction first.
- **Icon not appearing** — icon cache may need session restart. Best-effort refresh with `gtk-update-icon-cache`.
- **desktop-file-validate warns about multiple main categories** — e.g. `Categories=Development;Utility;` triggers "contains more than one main category". Pick exactly ONE main category (the first listed determines menu placement).
- **Don't set GTK_IM_MODULE on modern KDE/GNOME** — compositor handles text-input-v3 natively. Setting it can cause double-input.
- **Chrome must be fully quit** (not just closed) for ozone flags to take effect.
- **text-input-v1 is officially "unsupported" by Chromium** but is the most reliable option on KWin with fcitx5.
