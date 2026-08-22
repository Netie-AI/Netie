"""OS executor. Linux uses xdotool + ffmpeg. Windows uses ctypes user32."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class ExecutorError(RuntimeError):
    pass


class Executor:
    def __init__(self, *, display: str | None, screenshot_dir: Path) -> None:
        self.display = display or os.environ.get("DISPLAY") or ":1"
        self.screenshot_dir = screenshot_dir
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["DISPLAY"] = self.display
        return env

    def mouse_location(self) -> dict[str, int]:
        if sys.platform == "win32":
            import ctypes

            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return {"x": int(pt.x), "y": int(pt.y)}
        try:
            out = subprocess.run(
                ["xdotool", "getmouselocation", "--shell"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5.0,
                env=self._env(),
            ).stdout
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ExecutorError(f"xdotool getmouselocation failed: {exc}") from exc
        parsed = dict(re.findall(r"([A-Z]+)=(\d+)", out))
        return {
            "x": int(parsed.get("X", "0")),
            "y": int(parsed.get("Y", "0")),
            "screen": int(parsed.get("SCREEN", "0")),
        }

    def move(self, x: int, y: int) -> dict[str, Any]:
        if sys.platform == "win32":
            import ctypes

            if ctypes.windll.user32.SetCursorPos(int(x), int(y)) == 0:
                raise ExecutorError("SetCursorPos failed")
        else:
            try:
                subprocess.run(
                    ["xdotool", "mousemove", "--sync", str(int(x)), str(int(y))],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                    env=self._env(),
                )
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise ExecutorError(f"xdotool mousemove failed: {exc}") from exc
        loc = self.mouse_location()
        return {"requested": {"x": int(x), "y": int(y)}, "actual": loc}

    def click(self, x: int, y: int, button: str = "left") -> dict[str, Any]:
        moved = self.move(x, y)
        mapping = {"left": "1", "middle": "2", "right": "3"}
        if button not in mapping:
            raise ExecutorError(f"unknown button {button}")
        if sys.platform == "win32":
            import ctypes

            down = {"left": 0x0002, "right": 0x0008, "middle": 0x0020}[button]
            up = {"left": 0x0004, "right": 0x0010, "middle": 0x0040}[button]
            ctypes.windll.user32.mouse_event(down, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(up, 0, 0, 0, 0)
        else:
            try:
                subprocess.run(
                    ["xdotool", "click", mapping[button]],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                    env=self._env(),
                )
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise ExecutorError(f"xdotool click failed: {exc}") from exc
        return {"moved": moved, "button": button}

    def type_text(self, text: str) -> dict[str, Any]:
        if not text:
            raise ExecutorError("empty type")
        if sys.platform == "win32":
            raise ExecutorError("windows type is not wired yet")
        try:
            subprocess.run(
                ["xdotool", "type", "--clearmodifiers", "--", text],
                check=True,
                capture_output=True,
                text=True,
                timeout=30.0,
                env=self._env(),
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ExecutorError(f"xdotool type failed: {exc}") from exc
        return {"chars": len(text)}

    def hotkey(self, keys: list[str]) -> dict[str, Any]:
        if not keys:
            raise ExecutorError("empty hotkey")
        if sys.platform == "win32":
            raise ExecutorError("windows hotkey is not wired yet")
        combo = "+".join(keys)
        try:
            subprocess.run(
                ["xdotool", "key", "--clearmodifiers", combo],
                check=True,
                capture_output=True,
                text=True,
                timeout=5.0,
                env=self._env(),
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ExecutorError(f"xdotool key failed: {exc}") from exc
        return {"keys": keys}

    def wait(self, ms: int) -> dict[str, Any]:
        time.sleep(max(0, ms) / 1000.0)
        return {"ms": ms}

    def display_size(self) -> tuple[int, int]:
        env = os.environ.copy()
        env["DISPLAY"] = self.display
        try:
            out = subprocess.run(
                ["xdpyinfo", "-display", self.display],
                check=True,
                capture_output=True,
                text=True,
                timeout=5.0,
                env=env,
            ).stdout
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return (1920, 1080)
        m = re.search(r"dimensions:\s+(\d+)x(\d+)", out)
        if not m:
            return (1920, 1080)
        return (int(m.group(1)), int(m.group(2)))

    def screenshot(self, name: str) -> Path:
        dest = self.screenshot_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            raise ExecutorError("windows screenshot is not wired yet")
        if not shutil.which("ffmpeg"):
            raise ExecutorError("ffmpeg missing")
        w, h = self.display_size()
        display = self.display if self.display.startswith(":") else f":{self.display}"
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "x11grab",
            "-draw_mouse",
            "1",
            "-video_size",
            f"{w}x{h}",
            "-i",
            display,
            "-frames:v",
            "1",
            "-update",
            "1",
            str(dest),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=20.0)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise ExecutorError(f"ffmpeg screenshot failed: {exc}") from exc
        if not dest.exists() or dest.stat().st_size < 100:
            raise ExecutorError("screenshot was empty")
        return dest
