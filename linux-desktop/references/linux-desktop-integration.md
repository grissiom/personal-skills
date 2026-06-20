---
name: linux-desktop-integration
description: Create .desktop files and register applications in Linux desktop menus — AppImage icon extraction, desktop-file-validate, icon cache updates.
---

# Linux Desktop Integration

Register applications in the Linux desktop environment by creating `.desktop` files under `~/.local/share/applications/` and installing icons under `~/.local/share/icons/hicolor/`.

## When to use
- User asks to add an application to the desktop menu / application launcher
- User wants to register an AppImage as a desktop application
- User needs a `.desktop` file with custom launch arguments (e.g., `--no-sandbox`)

## Steps

### 1. Extract icons from AppImages (if applicable)
If the application is an AppImage, extract its icon resources:

```bash
cd /tmp && /path/to/AppImage --appimage-extract
```

**Pitfall:** `--appimage-extract <single-file>` only extracts symlinks — the actual icon files are relative symlinks that resolve only inside the full extraction tree. Always use bare `--appimage-extract` (no file argument) to get the complete tree, then find icons under `squashfs-root/usr/share/icons/hicolor/`.

### 2. Install icons into the hicolor theme
Copy all available sizes from the extraction:

```bash
for size in 16 32 48 64 128 256 512; do
  mkdir -p ~/.local/share/icons/hicolor/${size}x${size}/apps/
  cp /tmp/squashfs-root/usr/share/icons/hicolor/${size}x${size}/apps/<app>.png \
     ~/.local/share/icons/hicolor/${size}x${size}/apps/<app>.png
done
```

### 3. Create the .desktop file
Write to `~/.local/share/applications/<app>.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=<App Name>
Comment=<Description>
Exec=/absolute/path/to/binary [--flags]
Icon=<app>
Terminal=false
Categories=<MainCategory>;<AdditionalCategory>;
MimeType=x-scheme-handler/<app>;
StartupWMClass=<app>
```

Key field rules:
- **Exec**: MUST be an absolute path. Append launch flags here (e.g., `--no-sandbox`). Do NOT use shell constructs (`&&`, `|`, `~`).
- **Icon**: basename without extension. The desktop spec resolves it via the hicolor icon theme.
- **Categories**: Use exactly one main category (`Office`, `Utility`, `Development`, `Graphics`, `Network`, `AudioVideo`, `Education`, `Game`, `Science`, `Settings`, `System`). Additional categories are secondary. Unregistered category names (like `Note`) cause validation errors.
- **Terminal**: `false` for GUI apps, `true` for CLI/TUI apps.
- **StartupWMClass**: Set to the application's WM_CLASS string so the window manager groups windows correctly.

### 4. Validate
```bash
desktop-file-validate ~/.local/share/applications/<app>.desktop
```
- **Errors** (e.g., unregistered category name) must be fixed.
- **Hints** (e.g., "contains more than one main category") are informational — many real desktop files use multiple main categories and work fine.

### 5. Refresh caches (best-effort)
```bash
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
```
These tools may not be installed — that's fine. The desktop environment usually picks up changes on next login regardless.

### 6. Cleanup
Remove the temporary extraction directory:
```bash
rm -rf /tmp/squashfs-root
```
