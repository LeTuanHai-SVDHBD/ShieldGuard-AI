from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def _add_data_arg(path: Path, target: str) -> list[str]:
    if not path.exists():
        return []
    return ["--add-data", f"{path}{os.pathsep}{target}"]


def build() -> int:
    entry_point = PROJECT_ROOT / "main.py"
    assets_dir = PROJECT_ROOT / "assets"
    data_dir = PROJECT_ROOT / "data"
    icon_path = assets_dir / "icons" / "app_icon.ico"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "HeThongNhanDienAnh18+",
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        str(entry_point),
    ]

    cmd.extend(_add_data_arg(assets_dir, "assets"))
    cmd.extend(_add_data_arg(data_dir, "data"))

    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])

    print(" ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(build())
