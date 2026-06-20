# Linux Sandbox Fixup — Code Trace & Error Transcript

## The fixup function

From `hermes_cli/main.py` line 5330:

```python
def _desktop_linux_sandbox_fixup(packaged_executable: Path) -> bool:
    """Configure Electron's Linux SUID sandbox helper when required."""
    if sys.platform != "linux":
        return True

    sandbox = packaged_executable.parent / "chrome-sandbox"
    if not sandbox.exists():
        print(f"✗ Hermes Desktop is missing Electron's Linux sandbox helper: {sandbox}")
        return False

    # Reject symlinks — chown/chmod must not follow an attacker-controlled link
    try:
        sandbox_lstat = sandbox.lstat()
    except OSError:
        print(f"✗ Cannot stat Electron's Linux sandbox helper: {sandbox}")
        return False
    if not stat.S_ISREG(sandbox_lstat.st_mode):
        print(f"✗ Electron's Linux sandbox helper is not a regular file: {sandbox}")
        return False

    if sandbox_lstat.st_uid == 0 and stat.S_IMODE(sandbox_lstat.st_mode) == 0o4755:
        return True  # already configured — skip

    sudo = shutil.which("sudo")
    if not sudo:
        print("✗ Hermes Desktop requires sudo to configure Electron's Linux sandbox helper.")
        return False

    print("→ Configuring Electron Linux sandbox helper (sudo required)...")
    for command in ([sudo, "chown", "root:root", str(sandbox)],
                    [sudo, "chmod", "4755", str(sandbox)]):
        if subprocess.run(command, check=False).returncode != 0:
            print(f"✗ Failed to configure Electron's Linux sandbox helper: {sandbox}")
            return False
    return True
```

Called at line 5545:
```python
if not _desktop_linux_sandbox_fixup(packaged_executable):
    sys.exit(1)
```

## Error transcript (real session)

```
✓ built in 2.51s
  • packaging  platform=linux arch=x64 electron=40.10.2
  • copying unpacked Electron ...
→ Installing desktop workspace dependencies...
→ Building desktop packaged app...
→ Configuring Electron Linux sandbox helper (sudo required)...
sudo: a terminal is required to read the password; either use the -S option
      to read from standard input or configure an askpass helper
sudo: a password is required
✗ Failed to configure Electron's Linux sandbox helper:
  ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
```

## Why subprocess.run() sudo fails

`subprocess.run([sudo, ...])` inherits the parent's stdio. When the parent is a Hermes agent process (no real TTY), sudo can't open `/dev/tty` for password input. The `terminal` tool's PTY mode (`pty=true`) does NOT help — sudo still probes for a real terminal.

## The correct fix (user side)

```bash
sudo chown root:root ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
sudo chmod 4755 ~/.hermes/hermes-agent/apps/desktop/release/linux-unpacked/chrome-sandbox
```

Then resume with `hermes desktop --skip-build`.
