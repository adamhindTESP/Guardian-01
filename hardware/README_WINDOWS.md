# ⚠ Windows Filesystem Compatibility Notice

The `/hardware` directory contains design and interface files intended for
Linux/macOS filesystems.

## Important for Windows Users

Some files in this directory **cannot be checked out on Windows (NTFS)** due to
filesystem constraints (case sensitivity, reserved names, or path semantics).

### This is expected behavior.

If you see messages like:

invalid path ‘hardware/interfaces/hardware_interface.py’

You did **nothing wrong**.

### Supported workflows on Windows
- Read hardware files directly on GitHub
- Work on non-hardware portions of the repo
- Use sparse checkout or local exclusion (documented)

### Full hardware development
Requires:
- Linux
- macOS
- or a case-sensitive filesystem

⚠ **Do not commit deletions of hardware files caused by NTFS limitations.**
