#!/usr/bin/env python3
from common import load_presets

print("可用模型模式：")
for key, preset in load_presets().items():
    print(f"{key}：{preset['label']} - {preset['model']}")
