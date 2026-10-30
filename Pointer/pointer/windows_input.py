"""Windows SendInput + PowerShell screenshot. Importable on Linux for tests."""

from __future__ import annotations

import sys
from typing import Iterable

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

VK = {
    "ctrl": 0x11,
    "control": 0x11,
    "alt": 0x12,
    "shift": 0x10,
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "escape": 0x1B,
    "win": 0x5B,
    "super": 0x5B,
    "meta": 0x5B,
    "backspace": 0x08,
    "space": 0x20,
    "delete": 0x2E,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
}


def ensure_dpi_aware() -> str:
    """Best-effort per-monitor DPI so SetCursorPos matches GetCursorPos."""
    if sys.platform != "win32":
        return "skipped"
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return "per_monitor"
    except (AttributeError, OSError, ValueError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return "system"
    except (AttributeError, OSError, ValueError):
        return "failed"


def vk_code(name: str) -> int:
    key = name.strip().lower()
    if key in VK:
        return VK[key]
    if len(key) == 1 and "a" <= key <= "z":
        return ord(key.upper())
    if len(key) == 1 and "0" <= key <= "9":
        return ord(key)
    raise ValueError(f"unknown key {name}")


def unicode_keydown_up(ch: str) -> list[tuple[int, int]]:
    """Return (wVk, dwFlags) pairs for one character. Empty/control chars rejected."""
    if len(ch) != 1:
        raise ValueError("unicode event needs one character")
    code = ord(ch)
    if code < 32 and ch not in {"\t", "\n"}:
        raise ValueError("refusing control character")
    if ch == "\n":
        return [(0x0D, 0), (0x0D, KEYEVENTF_KEYUP)]
    if ch == "\t":
        return [(0x09, 0), (0x09, KEYEVENTF_KEYUP)]
    return [(code, KEYEVENTF_UNICODE), (code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP)]


def hotkey_press_release(keys: Iterable[str]) -> list[tuple[int, int]]:
    codes = [vk_code(k) for k in keys]
    down = [(c, 0) for c in codes]
    up = [(c, KEYEVENTF_KEYUP) for c in reversed(codes)]
    return down + up


def screenshot_powershell(dest: str) -> str:
    # Laptop-ASCII. Path is inserted quoted. Caller must pass an absolute path.
    escaped = dest.replace("'", "''")
    return (
        "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
        "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height; "
        "$g = [System.Drawing.Graphics]::FromImage($bmp); "
        "$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size); "
        f"$bmp.Save('{escaped}'); "
        "$g.Dispose(); $bmp.Dispose();"
    )


def send_events(events: list[tuple[int, int]]) -> int:
    """Send (vk_or_unicode, flags) via SendInput. Windows only."""
    import ctypes
    from ctypes import wintypes

    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]

        _anonymous_ = ("i",)
        _fields_ = [("type", wintypes.DWORD), ("i", _I)]

    arr = (INPUT * len(events))()
    for i, (code, flags) in enumerate(events):
        arr[i].type = 1  # INPUT_KEYBOARD
        if flags & KEYEVENTF_UNICODE:
            arr[i].ki.wVk = 0
            arr[i].ki.wScan = code
        else:
            arr[i].ki.wVk = code
            arr[i].ki.wScan = 0
        arr[i].ki.dwFlags = flags
    sent = ctypes.windll.user32.SendInput(len(events), ctypes.byref(arr), ctypes.sizeof(INPUT))
    return int(sent)
