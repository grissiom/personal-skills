---
name: linux-ime-wayland
description: Diagnose and fix fcitx5/ibus input method issues on Wayland — preedit auto-commit, candidate window position, compositor-specific flags for Chrome/Electron/Qt/GTK.
category: devops
---

# Linux IME on Wayland — Diagnosis & Fixes

Diagnose and fix fcitx5 (and ibus) input method issues on Wayland: preedit characters committing too early, candidate window misplacement, and compositor-specific quirks for Chrome/Electron/Qt/GTK apps.

## Triggers
- "fcitx/fcitx5 input method broken / auto-committing / candidates wrong"
- "Chinese/Japanese/Korean typing problems in browser/app on Wayland"
- "IME not working in Chrome/Electron/VS Code under Wayland"

## Diagnosis Steps

### 1. Identify the IME version and session type
```bash
fcitx5 --version
echo $XDG_SESSION_TYPE   # wayland or x11
echo $WAYLAND_DISPLAY
```

### 2. Run the built-in diagnostic (`fcitx5-diagnose`)
This is the single most valuable command. It shows:
- Which frontend each app is using (wayland vs xim vs ibus)
- The capabilities (cap) of each frontend — wayland frontend with cap:52 vs xim with cap:4000000000
- Environment variable state (GTK_IM_MODULE, QT_IM_MODULE, XMODIFIERS)

```bash
fcitx5-diagnose 2>/dev/null | grep -E 'program:|frontend:|cap:' | head -30
```

Key signal: if Chrome/Electron shows `frontend:wayland cap:52` but you're having issues, it's using text-input-v3 (which has known problems with KWin).

### 3. Identify the compositor
KDE Plasma → KWin; GNOME → Mutter; Sway; Hyprland; etc. Each has different text-input protocol support.

## Known Issues & Fixes

### Chrome/Chromium on KDE Plasma (KWin)
**Symptom:** Preedit characters auto-commit in dialogs/popups, or IME doesn't trigger at all.

**Root cause:** KWin and Chromium have a known disagreement in text-input-v3 protocol implementation (fcitx wiki).

**Fix A (recommended):** Force text-input-v1 instead of v3.
Add to Chrome launch flags:
```
--enable-wayland-ime --wayland-text-input-version=1
```
Apply by creating `~/.local/share/applications/google-chrome.desktop` that overrides the system one. Must fully quit and restart Chrome.

**Fix B:** Fall back to XWayland (most stable, uses XIM):
```
--ozone-platform=x11
```
+ set `GTK_IM_MODULE=fcitx` in environment.

**Fix C:** Use GTK4 IM module (candidate popup position may be wrong on non-GNOME):
```
--gtk-version=4
```
+ set `GTK_IM_MODULE=fcitx`.

### Chrome/Chromium on GNOME (Mutter)
GNOME's text-input-v3 support includes ibus dbus protocol. fcitx5 can replace ibus-daemon on startup. Use the same Wayland flags as above, or fall back to XWayland.

### Chrome/Chromium on Sway
Sway 1.10+ supports text-input-v3. Environment: `QT_IM_MODULE=fcitx` for Qt5, `QT_IM_MODULES="wayland;fcitx"` for Qt 6.8.2+. Chrome should work with `--enable-wayland-ime`.

### Electron apps (VS Code, Discord, Slack, etc.)
Electron does NOT support `--gtk-version=4`. Only text-input-v1/v3 flags work:
```
code --enable-features=UseOzonePlatform --ozone-platform=wayland --enable-wayland-ime
```
Or fall back to XWayland + `GTK_IM_MODULE=fcitx`.

### Persisting Chrome flags
Instead of desktop file overrides, you can set flags persistently at `chrome://flags` → "Preferred Ozone Platform". Options: Default / X11 / Wayland / Auto. Combined with `--enable-wayland-ime` for text-input protocol choice.

## Environment Variable Quick Reference

| Variable | Purpose | When to set |
|---|---|---|
| `GTK_IM_MODULE=fcitx` | Force GTK apps to use fcitx IM module | GTK apps under X11/XWayland; or when Wayland text-input isn't working |
| `QT_IM_MODULE=fcitx` | Force Qt apps to use fcitx IM module | Qt5 under Wayland on non-KDE compositors |
| `QT_IM_MODULES="wayland;fcitx"` | Qt 6.8.2+ fallback chain | Qt6 on compositors without text-input-v2 |
| `XMODIFIERS=@im=fcitx` | XIM protocol | XWayland apps |
| `SDL_IM_MODULE=fcitx` | SDL-based apps | Games/apps using SDL |

Unset `GTK_IM_MODULE` and `QT_IM_MODULE` on KDE Plasma (KWin handles text-input natively).

## Authoritative Source
- [fcitx-im.org: Using Fcitx 5 on Wayland](https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland) — compositor-specific setup, Chrome/Electron flags, known issues.

## Pitfalls
- **Don't set GTK_IM_MODULE when unset is correct.** On modern KDE/GNOME the compositor handles text-input-v3 natively; setting `GTK_IM_MODULE=fcitx` can cause double-input or break Wayland-native features.
- **Chrome must be fully quit (not just closed).** The ozone platform and IME flags are read at process start. Minimizing to tray doesn't count.
- **text-input-v1 is officially "unsupported" by Chromium devs** (per bug [crbug.com/1431532](https://bugs.chromium.org/p/chromium/issues/detail?id=1431532)), but it's the most reliable option on KWin with fcitx5.

## References
- `references/chrome-kwin-desktop-template.md` — ready-to-use `google-chrome.desktop` override with `--enable-wayland-ime --wayland-text-input-version=1` flags.
