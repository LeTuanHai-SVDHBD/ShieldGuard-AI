from __future__ import annotations

import os
import sys
from pathlib import Path


try:
    import winreg
except Exception:  # pragma: no cover - non-Windows fallback
    winreg = None


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _app_command(entry_point: Path) -> str:
    if getattr(sys, "frozen", False):
        return f"\"{sys.executable}\""

    pythonw = Path(sys.executable).with_name("pythonw.exe")
    executable = pythonw if pythonw.exists() else Path(sys.executable)
    return f"\"{executable}\" \"{entry_point}\""


def _startup_script_path(app_name: str) -> Path:
    appdata = os.getenv("APPDATA")
    if not appdata:
        return Path()
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / f"{app_name}.cmd"


def set_startup(enabled: bool, app_name: str, entry_point: Path) -> bool:
    success = False
    command = _app_command(entry_point)

    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
            success = True
        except Exception:
            success = False

    script_path = _startup_script_path(app_name)
    if enabled:
        if script_path:
            try:
                script_path.write_text(f"@echo off\n{command}\n", encoding="utf-8")
                success = True
            except Exception:
                pass
    else:
        if script_path and script_path.exists():
            try:
                script_path.unlink()
            except Exception:
                pass

    return success
