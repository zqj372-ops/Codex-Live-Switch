# switch-model

Use this skill when the user wants to switch, list, test, inspect, or restore Codex model configuration from inside Codex.

## Intent triggers

Chinese or English phrases like:

- 切换模型、换模型、换到 M3、切换到 MiniMax M3
- 切换到极速模式、切换到省钱模式、切换到本地模型、切换到 OpenRouter
- 查看可用模型、列出模型、list models
- 测试模型连接、测试 MiniMax M3、test provider
- 恢复模型配置、回滚配置、restore config

## Intent mapping

- 极速、快速、快改代码、fast -> `fast`
- M3、MiniMax M3、复杂项目、长上下文 -> `m3`
- 省钱、便宜、cheap -> `cheap`
- OpenRouter、备用 -> `openrouter`
- 本地、local、Ollama -> `local`
- 恢复、回滚、restore -> run `scripts/restore_config.py`
- 查看、列出、list -> run `scripts/list_models.py`
- 测试、连接、test -> run `scripts/test_provider.py <preset>`

## Required behavior

For model switching, run from the plugin root:

```bash
python3 scripts/switch_model.py <preset> --live --persist --print-slash-command
```

Rules:

1. Prefer current-session live switching, but do not claim Codex definitely accepted the internal `/model` command.
2. Always persist the selected default model to the Codex config unless the user explicitly asks for dry-run only.
3. If live switching cannot be confirmed, print the fallback command `/model <model>`.
4. Never tell the user to restart Codex.
5. Never write API keys to disk; only write the `env_key` variable name.
6. Do not print raw API keys. If an API key appears in errors, redact it.
7. If config parsing fails, do not overwrite the config.
8. Preserve existing user config and unrelated providers.

## Examples

User: `切换到 MiniMax M3`

Run:

```bash
python3 scripts/switch_model.py m3 --live --persist --print-slash-command
```

User: `查看可用模型`

Run:

```bash
python3 scripts/list_models.py
```

User: `恢复上一次模型配置`

Run:

```bash
python3 scripts/restore_config.py
```
