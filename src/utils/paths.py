import os
import sys
from pathlib import Path

APP_NAME = "HeThongNhanDienAnh18+"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_assets_dir() -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / "assets"
    return _project_root() / "assets"


def get_model_path(model_name: str = "320n.onnx") -> Path:
    return get_assets_dir() / "models" / model_name


def get_app_data_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / "AppData" / "Roaming" / APP_NAME


def get_data_dir() -> Path:
    data_dir = get_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_logs_dir() -> Path:
    logs_dir = get_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_log_path(filename: str = "bao_cao_vi_pham.txt") -> Path:
    return get_logs_dir() / filename


def get_config_path() -> Path:
    config_path = _project_root() / "data" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path


def get_default_config_path() -> Path:
    data_config = _project_root() / "data" / "config.json"
    if data_config.exists():
        return data_config
    return _project_root() / "config.json"


def get_privacy_path() -> Path:
    privacy_path = _project_root() / "data" / "privacy.md"
    privacy_path.parent.mkdir(parents=True, exist_ok=True)
    return privacy_path


def get_default_privacy_path() -> Path:
    return get_assets_dir() / "privacy.md"
