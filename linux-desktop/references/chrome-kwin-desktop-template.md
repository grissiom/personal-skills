# Chrome Desktop File Template for KWin + fcitx5

This is a user-level override for `~/.local/share/applications/google-chrome.desktop` that forces Chrome to use Wayland text-input-v1 (compatible with KWin) instead of the default text-input-v3 (which has a known protocol disagreement with KWin that causes fcitx5 preedit characters to auto-commit in dialogs).

## File: `~/.local/share/applications/google-chrome.desktop`

```ini
[Desktop Entry]
Version=1.0
Name=Google Chrome
GenericName=Web Browser
Comment=Access the Internet
Exec=/usr/bin/google-chrome-stable --enable-wayland-ime --wayland-text-input-version=1 %U
StartupNotify=true
Terminal=false
Icon=google-chrome
Type=Application
Categories=Network;WebBrowser;
MimeType=application/pdf;application/rdf+xml;application/rss+xml;application/xhtml+xml;application/xhtml_xml;application/xml;image/gif;image/jpeg;image/png;image/webp;text/html;text/xml;x-scheme-handler/http;x-scheme-handler/https;
Actions=new-window;new-private-window;

[Desktop Action new-window]
Name=New Window
Exec=/usr/bin/google-chrome-stable --enable-wayland-ime --wayland-text-input-version=1

[Desktop Action new-private-window]
Name=New Incognito Window
Exec=/usr/bin/google-chrome-stable --enable-wayland-ime --wayland-text-input-version=1 --incognito
```

## Verification

After applying, fully quit Chrome and restart. Then verify:

```bash
fcitx5-diagnose 2>/dev/null | grep -A1 'Google-chrome'
```

The frontend should still show `wayland` but the behavior should be fixed (text-input-v1 doesn't have the preedit auto-commit issue).

## Alternative: XWayland fallback

If text-input-v1 also has issues, replace the flags with `--ozone-platform=x11` and ensure `GTK_IM_MODULE=fcitx` is set in the environment.
