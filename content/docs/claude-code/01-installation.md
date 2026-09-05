---
title: 第一章 安装与快速上手
linkTitle: 快速上手
description: Claude Code 安装、登录与首次使用
weight: 71
---

# 安装与快速上手

Claude Code 是 Anthropic 官方的终端 AI 编程助手。本章介绍如何在 macOS / Linux / Windows 上安装，完成登录订阅，并跑通第一次对话。

## 安装方式 {#install}

推荐用官方原生安装脚本（无需 Node.js，且支持后台自动更新）。

```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows（PowerShell，普通用户身份，不要加管理员）
irm https://claude.ai/install.ps1 | iex
```

也可通过 Homebrew（macOS / Linux）或 npm 安装：

```bash
# Homebrew（不会自动更新，需手动 brew upgrade claude-code）
brew install --cask claude-code

# npm（需 Node.js 18+，不要使用 sudo）
npm install -g @anthropic-ai/claude-code
```

> 注意：npm 上的仿冒包名为 `claude-code`，运行会提示 "Wrong package!"。正确包名是 `@anthropic-ai/claude-code`，命令是 `claude`，不是 `claude-code`。

## 验证安装 {#verify}

安装完成后关闭并重新打开终端，执行：

```bash
claude --version
# 例如：2.1.89 (Claude Code)
```

## 登录与订阅 {#login}

Claude Code 需要有效账户（Claude Pro / Max / Teams / Enterprise 或 Anthropic Console API 额度），免费版 Claude.ai 不支持。

```bash
# 方式一：浏览器 OAuth 登录（最常见）
claude
# 首次运行会打印登录链接与验证码，浏览器中授权即可

# 方式二：使用 /login 重新登录
# 在交互界面中输入：
/login
```

无浏览器环境（服务器 / CI）可用 API Key：

```bash
# Anthropic 官方 API Key
export ANTHROPIC_API_KEY=sk-ant-...
claude

# Amazon Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
# 再配置好 AWS 凭证后运行 claude

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=your-project-id
claude
```

## 首次对话 {#first-chat}

在**项目根目录**启动 Claude Code，它会按需读取文件，无需手动上传：

```bash
cd path/to/your/project
claude
```

交互界面以 `claude >` 提示符等待输入，直接描述任务即可：

```text
claude > 帮我给 src/utils.ts 里的 formatDate 函数补一个单元测试
```

Claude 执行写文件、跑命令等操作时，会先征求你的许可（输入 `Y` 允许一次、`n` 拒绝、`Y` 加回车可一次允许本次会话全部编辑）。这就是唯一的"安全规则"：**破坏性操作前永远会确认**。

## 基本交互 {#interaction}

| 操作 | 说明 |
| --- | --- |
| 直接输入文字 | 向 Claude 下达任务或提问 |
| `!命令` | 以 Shell 命令执行，如 `!git status` |
| `Esc` | 中断当前 Claude 的生成 |
| `Ctrl+D` 或 `/exit` | 退出会话 |
| `Shift+Tab` | 切换权限模式（默认 / 计划 / 自动编辑） |

## 小结 {#summary}

安装推荐用官方脚本，登录后进入项目目录运行 `claude` 即可开始。下一章学习斜杠命令、`@` 文件引用、图片输入与 Git 集成等核心用法。
