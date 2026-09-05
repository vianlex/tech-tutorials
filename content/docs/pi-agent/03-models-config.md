---
title: 第三章 模型与配置
linkTitle: 模型与配置
description: Pi Agent 多模型支持、settings.json 与自定义供应商
weight: 63
---

# 模型与配置

## 多模型支持 {#multi-model}

Pi Agent 支持多家供应商，且可在**一次会话中随时切换模型**。可用模型取决于环境中已配置的 API Key（或 OAuth）。

```bash
# 列出当前可用模型（支持搜索）
pi --list-models
pi --list-models sonnet
```

启动即指定模型：

```bash
# --provider 指定供应商
pi --provider anthropic

# --model 用模式或 id（支持 provider/id）
pi --model sonnet
pi --model anthropic/claude-sonnet-4
```

## 切换与循环模型 {#switch-model}

会话内进行模型操作：

```text
/model      打开模型选择器（模糊搜索，方向键 + Enter）
Ctrl+P      在 --models 限定的模型间循环
/thinking   调整思考级别：off / minimal / low / medium / high
Shift+Tab   循环思考级别
```

通过 CLI 约束循环范围与思考级别：

```bash
# --models：Ctrl+P 时可循环的模型（逗号分隔）
pi --models "sonnet,opus,gpt"

# --thinking：off/minimal/low/medium/high/xhigh/max
pi --model sonnet --thinking high

# --api-key：命令行覆盖环境变量
pi --api-key sk-ant-...
```

## 配置文件 settings.json {#settings}

Pi Agent 有两级配置：

```text
~/.pi/agent/settings.json   全局配置（所有项目生效）
.pi/settings.json           项目配置（覆盖全局，需信任后加载）
```

常见配置项：

```json
{
  "steeringMode": "one-at-a-time",
  "followUpMode": "one-at-a-time",
  "transport": "auto",
  "defaultProjectTrust": "ask",
  "enableInstallTelemetry": false,
  "npmCommand": ["mise", "exec", "node@20", "--", "npm"],
  "externalEditor": "/usr/bin/nvim"
}
```

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| `steeringMode` | 队列中 steering 消息投递方式 | `one-at-a-time`（默认）/ `all` |
| `followUpMode` | 队列中 follow-up 消息投递方式 | `one-at-a-time`（默认）/ `all` |
| `transport` | 多传输供应商的传输偏好 | `sse` / `websocket` / `auto` |
| `defaultProjectTrust` | 无保存决策时的信任回退 | `ask`（默认）/ `always` / `never` |
| `enableInstallTelemetry` | 安装/更新遥测开关 | `false` 退出 |
| `npmCommand` | 指定 npm 执行上下文（配合版本管理器） | 命令数组 |
| `externalEditor` | 外部编辑器（Ctrl+G 调用） | 路径，缺省回退 `$VISUAL`/`$EDITOR` |

> 键盘绑定在 `~/.pi/agent/keybindings.json`，信任决策在 `~/.pi/agent/trust.json`，均为独立文件。

## 自定义模型与供应商 {#custom-models}

可将本地或自建端点（Ollama、vLLM、LM Studio 等）加入 `~/.pi/agent/models.json`：

```json
{
  "providers": {
    "ollama": {
      "type": "openai-completions",
      "baseUrl": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "models": [
        { "id": "llama3.1", "name": "Llama 3.1 (Ollama)" }
      ]
    }
  }
}
```

支持的 API 类型：

```text
openai-completions      OpenAI 兼容补全接口
openai-responses        OpenAI Responses API
anthropic-messages      Anthropic Messages API
google-generative-ai    Google Generative AI API
```

## 上下文与项目文件 {#context-files}

Pi Agent 会自动加载项目上下文，让 Agent 了解项目约定：

```text
# 上下文文件（AGENTS.md 或 CLAUDE.md）
加载顺序：
1. ~/.pi/agent/AGENTS.md        全局
2. 从 cwd 向上遍历的父目录
3. 当前目录

# 系统提示覆盖
.pi/SYSTEM.md            替换默认系统提示
APPEND_SYSTEM.md         追加到系统提示
```

关闭上下文发现：

```bash
pi --no-context-files     # 简写 -nc
```

## 小结 {#summary}

模型通过环境变量 + `/model` 或 CLI 标志选择，行为由 `~/.pi/agent/settings.json` 与 `models.json` 控制，项目约定可写入 `AGENTS.md`。下一章学习扩展系统与自定义开发。
