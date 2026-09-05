---
title: 第一章 简介与安装
linkTitle: 简介与安装
description: OpenCode 简介、三形态与安装
weight: 121
---

# 简介与安装

## 什么是 OpenCode {#what}

OpenCode 是一个开源的 AI 编程 Agent，由 SST/Anomaly 团队开发（官网 opencode.ai）。它免费内置可用模型，也支持连接任意厂商的 LLM（Claude、GPT、Gemini、DeepSeek、Groq 等），覆盖 75+ 提供方（基于 models.dev）。

核心特性：

- **LSP 自动加载**：根据项目自动启用对应语言服务器，让模型理解代码
- **多会话并行**：同一项目可同时启动多个 Agent 协作
- **分享链接**：任意会话可生成分享链接，方便协作或排错
- **任意模型 / 任意编辑器**：终端、桌面、IDE 三种形态通吃

## 三种形态对比 {#forms}

OpenCode 提供三种使用形态，能力一致、入口不同：

```text
终端 TUI        在终端直接运行 opencode，最轻量，适合本地开发
桌面 App        独立桌面应用，体验接近 IDE，开箱即用
IDE 扩展        在 VS Code / Cursor / Zed 等编辑器中内嵌使用
```

绝大多数命令与配置在三种形态下通用，本教程以终端 TUI 为主线讲解。

## 安装：macOS / Linux {#install-unix}

最推荐的方式是官方安装脚本：

```bash
# 官方安装脚本（推荐）
curl -fsSL https://opencode.ai/install | bash
```

也可使用各平台包管理器：

```bash
# Node.js（npm / bun / pnpm / yarn 任选其一）
npm install -g opencode-ai

# Homebrew（macOS / Linux，推荐官方 tap 获取最新版）
brew install anomalyco/tap/opencode

# Arch Linux
sudo pacman -S opencode           # 稳定版
paru -S opencode-bin              # AUR 最新版
```

> 官方 tap（`anomalyco/tap/opencode`）更新最及时；Homebrew 官方公式 `brew install opencode` 由社区维护，更新较慢。

## 安装：Windows {#install-windows}

Windows 下推荐使用 WSL 以获得最佳兼容性与性能，但原生也支持多种安装方式：

```bash
# Chocolatey
choco install opencode

# Scoop
scoop install opencode

# Node.js
npm install -g opencode-ai

# Mise
mise use -g github:anomalyco/opencode

# 也可直接从 Releases 下载二进制，或用 Docker 运行
docker run -it --rm ghcr.io/anomalyco/opencode
```

## 从源码 / Releases {#install-binary}

不想用包管理器时，可从 GitHub Releases 下载对应平台的预编译二进制，解压后将 `opencode` 加入 `PATH` 即可。

```bash
# 下载后放入 PATH 目录（示例：Linux/macOS）
sudo mv opencode /usr/local/bin/
```

## 验证安装 {#verify}

安装完成后，检查版本并启动一次：

```bash
# 查看版本号
opencode --version

# 查看帮助（列出全部子命令）
opencode --help

# 进入当前目录的 TUI（需先配置 Provider，见第二章）
opencode
```

能正常打印版本号即说明安装成功。若提示 `command not found`，请确认安装目录已加入 `PATH`。

## 小结 {#summary}

本章介绍了 OpenCode 是什么、三种形态的差异，以及 macOS/Linux/Windows 各平台的安装与版本验证方法。下一章将讲解如何配置模型提供方并创建你的第一个对话。
