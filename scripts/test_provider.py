#!/usr/bin/env python3
"""Send a minimal OpenAI-compatible chat_completions request for a preset."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request

from common import redact, require_preset


def main() -> int:
    parser = argparse.ArgumentParser(description="测试模型 provider 连接")
    parser.add_argument("preset_key")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    preset = require_preset(args.preset_key)
    env_key = preset.get("env_key")
    api_key = os.environ.get(env_key) if env_key else None
    if env_key and not api_key:
        print("失败：缺少环境变量。")
        print(f"env_key = {env_key}")
        return 2

    url = preset["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": preset["model"],
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 8,
        "temperature": 0,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"测试 Provider：{preset['provider_name']}")
    print(f"模型：{preset['model']}")
    print(f"URL：{url}")
    if env_key:
        print(f"API Key：{env_key}={redact(api_key or '')}")

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            elapsed = (time.perf_counter() - started) * 1000
            body = resp.read(4096).decode("utf-8", errors="replace")
            print("成功")
            print(f"HTTP 状态码：{resp.status}")
            print(f"首字响应时间：{elapsed:.0f} ms")
            print("响应预览：" + body[:300])
            return 0
    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - started) * 1000
        body = exc.read(2048).decode("utf-8", errors="replace")
        print("失败")
        print(f"HTTP 状态码：{exc.code}")
        print(f"首字响应时间：{elapsed:.0f} ms")
        safe_body = body[:500].replace(api_key, "****") if api_key else body[:500]
        print("错误信息：" + safe_body)
        return 1
    except Exception as exc:
        elapsed = (time.perf_counter() - started) * 1000
        print("失败")
        print("HTTP 状态码：<无>")
        print(f"首字响应时间：{elapsed:.0f} ms")
        message = str(exc).replace(api_key, "****") if api_key else str(exc)
        print(f"错误信息：{message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
