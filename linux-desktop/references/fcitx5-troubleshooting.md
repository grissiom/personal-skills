---
name: fcitx5-troubleshooting
description: Diagnose and fix fcitx5 input method issues on Linux — auto-commit, candidate window position, etc. Covers Chrome/Electron/GTK/Qt on Wayland and X11.
---

# fcitx5 Troubleshooting

## Trigger conditions
- fcitx5 input method issues: characters auto-committing, candidate window position wrong, IME not triggering
- Specifically for Chrome/Chromium/Electron apps on Wayland or X11
- User mentions fcitx, fcitx5, input method, 输入法, 打字问题

## Diagnostic steps

### 1. Gather system info
```bash
fcitx5 --version
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"
ps aux | grep fcitx5
```

### 2. Run fcitx5-diagnose
```bash
fcitx5-diagnose 2>/dev/null | grep -E "frontend:|program:" | head -20
```
Key fields:
- `frontend:wayland cap:52` — uses text-input-v3 (limited, known issues with KWin)
- `frontend:xim cap:4000000000` — uses XIM over XWayland (fragile preedit)
- `frontend:dbus` — uses fcitx5 DBus frontend (best)

### 3. Check Chrome/Chromium ozone platform
```bash
xwininfo -root -tree 2>/dev/null | grep -i chrome
```
If Chrome windows appear in xwininfo → X11/XWayland mode.
If not → native Wayland mode.

### 4. Check environment variables
```bash
echo "GTK_IM_MODULE=$GTK_IM_MODULE"
echo "QT_IM_MODULE=$QT_IM_MODULE"
echo "XMODIFIERS=$XMODIFIERS"
```

## Fix: Chrome/Chromium auto-commit on Wayland

### Root cause
On KDE Plasma (KWin) + Wayland, Chrome's text-input-v3 implementation has protocol-level disagreements with KWin, causing preedit text to commit prematurely in dialogs/popups.

### Recommended fix: XWayland + GTK IM module
Add to Chrome's desktop file (`~/.local/share/applications/google-chrome.desktop`):
```
Exec=env GTK_IM_MODULE=fcitx /usr/bin/google-chrome-stable --ozone-platform=x11 %U
```

This does two things:
1. `GTK_IM_MODULE=fcitx` — Chrome uses fcitx5's GTK IM module (DBus), NOT raw XIM
2. `--ozone-platform=x11` — forces XWayland, avoiding buggy text-input-v3

### Alternative: text-input-v1 (less reliable)
```
--enable-wayland-ime --wayland-text-input-version=1
```

### Verification
After restarting Chrome:
```bash
# Confirm X11 mode
xeyes &  # mouse over Chrome window, eyes should follow

# Check fcitx5 frontend
fcitx5-diagnose 2>/dev/null | grep chrome
```

## Prerequisites
- `fcitx5-frontend-gtk3` package installed (for GTK_IM_MODULE=fcitx to work)
- `XMODIFIERS=@im=fcitx` set in environment

## Pitfalls
- Environment variables set in desktop file only take effect on restart — hot-reloading impossible
- `--ozone-platform=x11` is redundant if Chrome already defaults to XWayland, but harmless as a safeguard
- Without `GTK_IM_MODULE=fcitx`, Chrome uses raw XIM protocol over XWayland — preedit is fragile, especially in dialogs
- fcitx5's official wiki is at https://fcitx-im.org/wiki/Using_Fcitx_5_on_Wayland — authoritative for Wayland-specific issues
