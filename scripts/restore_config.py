#!/usr/bin/env python3
"""Restore the most recent Codex config backup."""

from __future__ import annotations

import shutil

from common import backup_config, backups_dir, config_path, parse_toml_safely


def main() -> int:
    bdir = backups_dir()
    backups = sorted(bdir.glob("config-*.toml")) if bdir.exists() else []
    if not backups:
        print("未找到可恢复的备份配置。")
        return 1
    source = backups[-1]
    target = config_path()
    try:
        parse_toml_safely(source.read_text(encoding="utf-8"), source)
    except ValueError as exc:
        print("最近一次备份无法安全解析，未恢复。")
        print(f"原因：{exc}")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    current_backup = backup_config(target)
    shutil.copy2(source, target)
    print("已恢复上一次配置。")
    print("恢复来源：")
    print(source)
    if current_backup:
        print("当前配置已再次备份，方便回滚：")
        print(current_backup)
    print("当前会话如需立即切回，请使用：")
    print("/model <原模型名>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
