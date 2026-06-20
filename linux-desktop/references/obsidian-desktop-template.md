# AppImage Desktop File Template

This is the desktop file created for Obsidian 1.12.7 AppImage. Use as a template for any Electron-based AppImage.

## File: `~/.local/share/applications/<app>.desktop`

```ini
[Desktop Entry]
Type=Application
Name=Obsidian
Comment=Obsidian Markdown Knowledge Base
Exec=~/Obsidian-1.12.7.AppImage --no-sandbox
Icon=obsidian
Terminal=false
Categories=Office;Utility;
MimeType=x-scheme-handler/obsidian;
StartupWMClass=obsidian
```

## Key Adaptations Per App

- **`Name`**: Human-readable app name
- **`Exec`**: Absolute path to the AppImage + any required flags. Common flags:
  - `--no-sandbox` — Required for many Electron AppImages when running as non-root
  - `--enable-wayland-ime --wayland-text-input-version=1` — Chrome/Electron flags for Wayland IME (see `linux-ime-wayland` skill)
- **`Icon`**: Bare icon name without `.png` — must match the filename installed to `~/.local/share/icons/hicolor/*/apps/`
- **`Categories`**: One main category + optional additionals. See [Desktop Menu Specification](https://specifications.freedesktop.org/menu-spec/latest/apa.html) for valid categories.
- **`StartupWMClass`**: The X11 WM_CLASS of the app window. For Electron apps this is usually the app name lowercased. Run `xprop WM_CLASS` and click the window to find the exact value.

## Validation

```bash
desktop-file-validate ~/.local/share/applications/<app>.desktop
```
