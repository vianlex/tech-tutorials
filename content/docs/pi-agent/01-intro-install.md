---
title: 第一章 简介与安装
linkTitle: 简介与安装
description: Pi Agent 简介、安装与首次运行
weight: 61
---

# 简介与安装

## 什么是 Pi Agent {#what}

Pi Agent 是一个**极简、开源**的终端 AI 编程 Agent，核心特点：

- **多模型支持**：Anthropic、OpenAI、Google、Groq、xAI 等，且可在会话中切换模型
- **TUI 交互**：基于终端的对话式界面，支持快捷键、分支、会话树
- **会话管理**：自动保存历史会话，可恢复、fork、导出
- **扩展系统**：通过 Pi 包扩展自定义工具、技能与命令
- **极简哲学**：不预设复杂工作流，把自由留给用户（"No permission popups"）

```bash
# 项目地址
# https://github.com/badlogic/pi-mono
# npm: @mariozechner/pi-coding-agent
```

## 与同类工具对比 {#comparison}

| 维度 | Pi Agent | 传统 CLI 助手 | 重型 IDE 插件 |
|------|----------|---------------|---------------|
| 运行环境 | 任意终端 | 终端 | 编辑器内 |
| 模型切换 | 会话中即时切换 | 通常固定 | 依赖插件 |
| 配置复杂度 | 极低 | 低 | 高 |
| 扩展方式 | Pi 包 / 技能 | 脚本 | 插件市场 |
| 会话分支 | 内置树状分支 | 无 | 视实现而定 |

```text
适用场景：喜欢在终端里干活、希望轻量可控、想要多模型自由切换的开发者。
```

## 安装 Pi Agent {#install}

推荐通过 npm 全局安装（需 Node.js 环境）：

```bash
# 全局安装
npm install -g @mariozechner/pi-coding-agent

# 验证安装
pi --version
```

也可下载独立二进制（GitHub Releases）：

```bash
# macOS / Linux
tar -xzf pi-darwin-arm64.tar.gz
./pi

# Windows
# 解压 pi-windows-x64.zip 后运行 pi.exe
```

macOS 若提示"无法打开"，解除隔离即可：

```bash
xattr -c ./pi
```

## 配置 API Key {#api-key}

Pi Agent 支持多家供应商，通过**环境变量**注入 API Key：

```bash
# Anthropic（Claude）
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI（GPT）
export OPENAI_API_KEY=sk-...

# Google（Gemini）
export GEMINI_API_KEY=...

# 其他供应商
export MISTRAL_API_KEY=...     # Mistral
export GROQ_API_KEY=gsk_...   # Groq
export CEREBRAS_API_KEY=csk_...
export XAI_API_KEY=xai-...     # xAI / Grok
export OPENROUTER_API_KEY=sk-or-...
export ZAI_API_KEY=...
```

> 注意：`/model` 命令只会显示**已配置对应 API Key** 的供应商模型。

## 认证方式：OAuth（可选） {#oauth}

Claude Pro/Max 或 GitHub Copilot 订阅用户可用 OAuth，免管 Key：

```bash
# 进入交互会话后执行
pi
# 在 TUI 中输入：
/login
# 选择 "Anthropic (Claude Pro/Max)" 或 "GitHub Copilot"，浏览器授权

# 退出登录（清除 ~/.pi/agent/oauth.json）
/logout
```

## Windows 注意事项 {#windows}

Pi Agent 在 Windows 上**需要一个 bash shell**：

```json
// ~/.pi/agent/settings.json
{
  "shellPath": "C:\\Program Files\\Git\\bin\\bash.exe"
}
```

查找顺序：自定义 `shellPath` → Git Bash → PATH 上的 `bash.exe`（Cygwin/MSYS2/WSL）。多数用户安装 **Git for Windows** 即可。

## 首次运行 {#first-run}

配置好 Key 后，进入任意项目目录启动：

```bash
# 设置 Key（示例）
export ANTHROPIC_API_KEY=sk-ant-...

# 启动交互式 TUI
cd ~/my-project
pi
```

启动时你会看到加载的上下文文件（如 `AGENTS.md`）与技能列表，随后即可直接对话：

```text
You: 帮我在 src/ 下创建一个简单的 Express 服务器
# Agent 会读取、写入、编辑文件，并通过 bash 执行命令
```

## 小结 {#summary}

Pi Agent 通过 `npm install -g @mariozechner/pi-coding-agent` 即可安装，用环境变量或 OAuth 配置模型密钥后，在终端运行 `pi` 即可开始。下一章学习 TUI 交互、快捷键与会话管理。
