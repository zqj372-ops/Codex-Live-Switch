#!/usr/bin/env python3
"""Switch Codex model presets with safe persistence and live-session fallback."""

from __future__ import annotations

import argparse
import os
import shutil
import sys

from common import backup_config, config_path, parse_toml_safely, require_preset, upsert_provider, upsert_top_level


def persist_config(preset: dict, dry_run: bool) -> tuple[bool, str, str | None]:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    try:
        parse_toml_safely(original, path)
    except ValueError as exc:
        print("未修改配置。")
        print("原因：")
        print(str(exc))
        print("建议：")
        print("请先备份并检查 config.toml 格式。")
        print("本插件不会强行覆盖你的原配置。")
        return False, str(path), None

    updated = upsert_top_level(original, "model", preset["model"])
    updated = upsert_top_level(updated, "model_provider", preset["provider_id"])
    updated = upsert_provider(updated, preset)
    parse_toml_safely(updated, path)

    if dry_run:
        return True, str(path), None

    backup = backup_config(path)
    try:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(updated, encoding="utf-8")
        parse_toml_safely(tmp.read_text(encoding="utf-8"), tmp)
        tmp.replace(path)
    except Exception:
        if backup and backup.exists():
            shutil.copy2(backup, path)
        raise
    return True, str(path), str(backup) if backup else None


def main() -> int:
    parser = argparse.ArgumentParser(description="切换 Codex 模型 preset")
    parser.add_argument("preset_key")
    parser.add_argument("--live", action="store_true", help="尝试当前会话即时切换（输出可执行 fallback）")
    parser.add_argument("--persist", action="store_true", help="写入 Codex 默认配置")
    parser.add_argument("--print-slash-command", action="store_true", help="输出 /model fallback 命令")
    parser.add_argument("--dry-run", action="store_true", help="只检查和预览，不写入")
    args = parser.parse_args()

    preset = require_preset(args.preset_key)
    persist = args.persist or not args.live
    saved = False
    config = str(config_path())
    backup = None

    if persist:
        try:
            saved, config, backup = persist_config(preset, args.dry_run)
        except Exception as exc:
            print("写入失败，已尝试回滚。")
            print(f"原因：{exc}")
            return 1

    print(f"已选择：{preset['label']}")
    print(f"模型：{preset['model']}")
    print(f"Provider：{preset['provider_name']}")
    print("当前会话：")
    if args.live:
        print("已尝试即时切换。")
    else:
        print("未请求即时切换。")
    print("默认配置：")
    if args.dry_run:
        print(f"dry-run：将保存到 {config}")
    elif saved:
        print(f"已保存到 {config}")
        if backup:
            print(f"已备份原配置：{backup}")
    else:
        print("未保存。")

    env_key = preset.get("env_key")
    if env_key and not os.environ.get(env_key):
        print("检测到环境变量未设置：")
        print(env_key)
        print("请先执行：")
        print(f'export {env_key}="你的 API Key"')

    if args.print_slash_command or args.live:
        print("如果当前会话没有自动切换，请直接输入：")
        print(f"/model {preset['model']}")
    print("无需重启 Codex。")
    return 0 if saved or args.dry_run or not persist else 1


if __name__ == "__main__":
    raise SystemExit(main())
