# Codex Live Switch / Codex 即时换模

Codex Live Switch 是一个 Codex 专用轻量插件，用于在 Codex 当前会话中通过自然语言快速切换 MiniMax、DeepSeek、OpenRouter、Ollama 等第三方模型，并同步保存为默认配置。

它不是桌面应用、不是 Electron 软件、不是账号池、不是 API 转发平台，也不是通用 AI CLI 管理器。它只做一件事：在 Codex 里尽量不重启地切换模型。

## 核心能力

- Codex 插件结构：`.codex-plugin/plugin.json`、`skills`、`hooks`、`presets`、`scripts`。
- 双通道切换：当前会话 Live Switch + `~/.codex/config.toml` 持久化。
- 无法确认当前会话已切换时，输出可复制的 `/model <model>` fallback 命令。
- 写配置前自动备份到 `~/.codex/backups/config-YYYYMMDD-HHMMSS.toml`。
- TOML 解析失败时拒绝覆盖用户配置。
- 不保存 API Key 明文，只保存环境变量名，例如 `MINIMAX_API_KEY`。
- 支持恢复最近一次备份。
- SessionStart hook 只显示当前模型状态，不修改配置、不读取 API Key。

## 内置模型 preset

| preset | 模式 | Provider | Model | 说明 |
| --- | --- | --- | --- | --- |
| `fast` | 极速改代码 | MiniMax | `MiniMax-M2.7-highspeed` | 快速修 bug、改 UI、小范围代码修改 |
| `m3` | 复杂项目 / 长上下文 | MiniMax | `MiniMax-M3` | 长上下文、多文件分析、复杂项目重构 |
| `cheap` | 省钱模式 | DeepSeek | `deepseek-chat` | 解释报错、生成普通代码、低成本任务 |
| `openrouter` | OpenRouter 备用 | OpenRouter | `openrouter/auto` | 备用路由和多供应商 fallback |
| `local` | 本地 Ollama | Ollama | `qwen2.5-coder:32b` | 本地离线代码任务 |

## 安装

```bash
mkdir -p ~/.codex/plugins
cp -r codex-live-switch ~/.codex/plugins/codex-live-switch
```

如需 marketplace 入口，可创建或合并：

```json
{
  "plugins": [
    {
      "name": "codex-live-switch",
      "path": "~/.codex/plugins/codex-live-switch",
      "description": "Switch Codex models without restarting."
    }
  ]
}
```

然后在 Codex 中通过 `/plugins` 启用。

## 环境变量

远程 provider 使用 API Key 环境变量，本插件不会保存明文 Key：

```bash
export MINIMAX_API_KEY="你的 API Key"
export DEEPSEEK_API_KEY="你的 API Key"
export OPENROUTER_API_KEY="你的 API Key"
```

本地 Ollama preset 不需要 API Key。

## 在 Codex 里使用

可以直接输入：

```text
查看可用模型
切换到极速模式
切换到 MiniMax M3
切换到省钱模式
切换到本地模型
测试 MiniMax M3
恢复上一次模型配置
```

Skill 会把意图映射到脚本。例如 `切换到 MiniMax M3` 会运行：

```bash
python3 scripts/switch_model.py m3 --live --persist --print-slash-command
```

典型输出：

```text
已选择：复杂项目 / 长上下文
模型：MiniMax-M3
Provider：MiniMax
当前会话：
已尝试即时切换。
默认配置：
已保存到 ~/.codex/config.toml
如果当前会话没有自动切换，请直接输入：
/model MiniMax-M3
无需重启 Codex。
```

## 脚本命令

```bash
python3 scripts/list_models.py
python3 scripts/switch_model.py m3 --live --persist --print-slash-command
python3 scripts/switch_model.py fast --dry-run
python3 scripts/test_provider.py m3
python3 scripts/restore_config.py
python3 scripts/status.py
```

## 配置写入格式

插件会保留已有配置和其他 provider，只更新顶层模型和目标 provider：

```toml
model = "MiniMax-M3"
model_provider = "minimax"

[model_providers.minimax]
name = "MiniMax"
base_url = "https://api.minimax.io/v1"
wire_api = "chat_completions"
env_key = "MINIMAX_API_KEY"
```

如果设置了 `CODEX_HOME`，配置路径为 `$CODEX_HOME/config.toml`；否则为 `~/.codex/config.toml`。

## 安全边界

- 不做桌面应用。
- 不做账号池或多 Key 轮询。
- 不做云同步或团队共享。
- 不绕过官方限制。
- 不承诺插件一定能直接执行 Codex 内部 `/model`；无法确认时始终输出 fallback 命令。
- 不提示重启 Codex；只有 Codex 版本完全不支持 `/model` 时，建议升级 Codex。
