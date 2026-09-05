---
title: 第四章 配置与自定义
linkTitle: 配置与自定义
description: opencode.json、模型选择、自定义 agent、规则文件与主题
weight: 124
---

# 配置与自定义

## 配置文件位置 {#locations}

OpenCode 的配置支持 JSON / JSONC（可带注释），多个来源会**合并**而非互相覆盖：

```text
项目根           opencode.json       随仓库提交，团队共享（推荐）
用户全局         ~/.config/opencode/opencode.json
TUI 专属         tui.json（项目或 ~/.config/opencode/ 下）
环境变量         OPENCODE_CONFIG   指定配置文件路径
```

> 项目级 `opencode.json` 启动时会从当前目录向上查找到 Git 根，可安全提交。全局用户配置位于 `~/.config/opencode/`。

## 选择模型 {#models}

在 `opencode.json` 中指定主模型与轻量模型：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

`small_model` 用于生成标题等轻量任务，默认会尝试更便宜的模型。查看可用模型：

```bash
opencode models            # 列出全部已配置提供方的模型（provider/model 格式）
opencode models anthropic  # 只看某个提供方
opencode models --refresh  # 刷新 models.dev 缓存，获取新模型
```

## 配置提供方与密钥 {#providers}

通过 `provider` 传入选项，密钥推荐用环境变量：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

启用 / 禁用提供方（白名单优先于黑名单）：

```json
{
  "enabled_providers": ["anthropic", "openai"],
  "disabled_providers": ["gemini"]
}
```

配置还支持 `{env:VAR}` 与 `{file:path}` 变量替换。

## 自定义 Agent {#agents}

在 `opencode.json` 中用 `agent` 定义专属 Agent：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": { "write": false, "edit": false }
    }
  },
  "default_agent": "build",
  "subagent_depth": 1
}
```

也可在 `~/.config/opencode/agents/` 或 `.opencode/agents/` 用 Markdown 文件定义；`default_agent` 指定默认主 Agent，`subagent_depth` 控制子 Agent 嵌套深度（0 禁用子 Agent）。

命令行创建 Agent（交互向导，或带全参数非交互运行）：

```bash
opencode agent create \
  --description "Review code" \
  --mode primary \
  --permissions bash,read,edit \
  --model anthropic/claude-sonnet-4-5

opencode agent list     # 列出所有可用 Agent
```

## 规则文件：AGENTS.md 与 instructions {#rules}

`/init` 生成的 `AGENTS.md` 可通过 `instructions` 数组纳入更多规则文件：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md", "CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]
}
```

`instructions` 接受文件路径或 glob 模式，OpenCode 会自动加载作为系统上下文。

## 自定义命令 {#commands}

在 `opencode.json` 的 `command` 字段或 `.opencode/commands/*.md` 中定义斜杠命令：

```json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage and show failures.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

Markdown 写法（`.opencode/commands/test.md`）：

```markdown
---
description: Run tests with coverage
agent: build
---

Run the full test suite with coverage report and show any failures.
```

模板支持占位符与语法：

```text
$ARGUMENTS   传入的全部参数（如 /component Button → Button）
$1 $2 $3     位置参数
!`npm test`  注入 shell 命令输出
@src/foo.tsx 引用文件内容
```

自定义命令可覆盖同名内置命令（如 `/init`）。

## 主题与快捷键 {#theme-keys}

TUI 外观与键位在 `tui.json` 中配置（仅覆盖想改的项，其余继承默认）：

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "keybinds": {
    "command_list": "ctrl+p"
  }
}
```

常用内置斜杠命令（可在 TUI 输入 `/` 触发）：

```text
/help /editor /export /new /sessions /share /unshare
/compact /models /themes /init /undo /redo /exit /connect /thinking
```

多数命令有 `ctrl+x` 引导键快捷键（如 `ctrl+x c` 压缩、`ctrl+x u` 撤销、`ctrl+x l` 会话列表）。

## 权限与 MCP {#permissions-mcp}

默认允许所有操作，可改为需确认，并接入 MCP 服务器：

```json
{
  "permission": { "edit": "ask", "bash": "ask" },
  "mcp": {
    "jira": { "type": "remote", "url": "https://jira.example.com/mcp", "enabled": true }
  }
}
```

## 小结 {#summary}

本章讲解了 `opencode.json` 配置位置、模型与提供方设置、自定义 Agent、规则文件引入、自定义命令以及主题/快捷键/权限/MCP。下一章进入进阶用法：CLI 非交互执行、serve 无头 API、GitHub agent 与效率技巧。
