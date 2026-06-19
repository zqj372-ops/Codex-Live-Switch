#!/usr/bin/env python3
"""Shared helpers for Codex Live Switch scripts."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRESETS_PATH = ROOT / "presets" / "models.json"


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def config_path() -> Path:
    return codex_home() / "config.toml"


def backups_dir() -> Path:
    return codex_home() / "backups"


def load_presets() -> dict[str, dict[str, Any]]:
    with PRESETS_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require_preset(key: str) -> dict[str, Any]:
    presets = load_presets()
    if key not in presets:
        print(f"未知模型 preset：{key}")
        print("可用 preset：" + "、".join(presets.keys()))
        sys.exit(2)
    return presets[key]


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup_config(config: Path | None = None) -> Path | None:
    config = config or config_path()
    if not config.exists():
        return None
    backups_dir().mkdir(parents=True, exist_ok=True)
    dest = backups_dir() / f"config-{timestamp()}.toml"
    counter = 1
    while dest.exists():
        dest = backups_dir() / f"config-{timestamp()}-{counter}.toml"
        counter += 1
    shutil.copy2(config, dest)
    return dest


def parse_toml_safely(text: str, source: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{source} 无法安全解析：{exc}") from exc


def quote_toml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def redact(value: str) -> str:
    if not value:
        return value
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"


def upsert_top_level(text: str, key: str, value: str) -> str:
    line = f"{key} = {quote_toml(value)}"
    pattern = re.compile(rf"(?m)^{re.escape(key)}\s*=.*$")
    if pattern.search(text):
        return pattern.sub(line, text, count=1)
    insert_at = 0
    match = re.search(r"(?m)^\[", text)
    if match:
        insert_at = match.start()
        prefix = text[:insert_at].rstrip()
        suffix = text[insert_at:].lstrip("\n")
        return (prefix + "\n" if prefix else "") + line + "\n" + suffix
    text = text.rstrip()
    return (text + "\n" if text else "") + line + "\n"


def provider_block(provider: dict[str, Any]) -> str:
    lines = [f"[model_providers.{provider['provider_id']}]"]
    lines.append(f"name = {quote_toml(provider['provider_name'])}")
    lines.append(f"base_url = {quote_toml(provider['base_url'])}")
    lines.append(f"wire_api = {quote_toml(provider['wire_api'])}")
    if provider.get("env_key"):
        lines.append(f"env_key = {quote_toml(provider['env_key'])}")
    return "\n".join(lines) + "\n"


def upsert_provider(text: str, provider: dict[str, Any]) -> str:
    block = provider_block(provider)
    pid = re.escape(provider["provider_id"])
    pattern = re.compile(rf"(?ms)^\[model_providers\.{pid}\]\n.*?(?=^\[|\Z)")
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    text = text.rstrip()
    return (text + "\n\n" if text else "") + block


def backup_count() -> int:
    return len(list(backups_dir().glob("config-*.toml"))) if backups_dir().exists() else 0


def read_config() -> tuple[Path, str, dict[str, Any]]:
    path = config_path()
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return path, text, parse_toml_safely(text, path)
