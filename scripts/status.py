#!/usr/bin/env python3
from common import backup_count, read_config

try:
    path, _text, data = read_config()
    print("Codex Live Switch：")
    print("当前 Codex 配置：")
    print(f"model = {data.get('model', '<未设置>')}")
    print(f"model_provider = {data.get('model_provider', '<未设置>')}")
    print(f"config = {path}")
    print(f"backup_count = {backup_count()}")
    print("输入“查看可用模型”可查看切换选项。")
except Exception as exc:
    print("Codex Live Switch：读取当前模型状态失败，不影响 Codex 启动。")
    print(f"原因：{exc}")
