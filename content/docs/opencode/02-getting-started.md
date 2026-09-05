---
title: 第二章 快速上手
linkTitle: 快速上手
description: 配置 Provider、生成 AGENTS.md 与第一个对话
weight: 122
---

# 快速上手

## 配置 Provider：/connect {#connect}

首次使用需先配置模型提供方。新手最简单的方式是 TUI 内的 `/connect` 命令，配合 OpenCode Zen（官方精选、已验证的模型列表）。

在 TUI 中执行：

```text
/connect
```

然后选择 `opencode`（即 Zen），按提示打开 https://opencode.ai/auth 登录、绑定账单并复制 API key，回到终端粘贴即可。Zen 由 OpenCode 团队托管，无需自己申请各厂商 key。

```text
┌ API key
│ （在此粘贴从 opencode.ai/auth 复制的 key）
└ enter
```

也可在 `/connect` 中选择其他提供方（Anthropic、OpenAI、Google、DeepSeek、Groq 等），直接粘贴对应的 API key。

## 配置 Provider：opencode auth login {#auth-login}

除了 TUI 内配置，还可在命令行用 `opencode auth login` 登录。它基于 models.dev 的提供方列表，可配置任意厂商的凭据，凭证保存在 `~/.local/share/opencode/auth.json`。

```bash
# 交互式选择提供方并登录
opencode auth login

# 直接指定提供方（跳过选择步骤）
opencode auth login --provider anthropic

# 查看已登录的提供方
opencode auth list        # 或 opencode auth ls

# 退出某个提供方
opencode auth logout
```

`/connect` 与 `auth login` 的区别：

```text
/connect        在 TUI 内操作，推荐新手；首选 OpenCode Zen 或粘贴 key
auth login      在命令行操作，凭证落盘到 ~/.local/share/opencode/auth.json
两者最终都让 OpenCode 在启动时加载到提供方与 key（也支持环境变量或 .env）
```

## 初始化项目：/init {#init}

进入项目目录后，运行 `/init` 让 OpenCode 分析代码库并生成 `AGENTS.md`：

```bash
# 先切到你的项目
cd /path/to/project

# 启动 TUI
opencode
```

在 TUI 中输入：

```text
/init
```

`/init` 会分析项目结构、技术栈与编码习惯，并在项目根生成 `AGENTS.md`。**建议将该文件提交到 Git**，它帮助 OpenCode 理解项目、保持一致性。

## AGENTS.md 是什么 {#agents-md}

`AGENTS.md` 是项目的「智能体说明书」，类似 `README` 但面向 AI。内容通常包括：

```text
- 项目使用的语言、框架与构建命令
- 目录结构与模块职责
- 代码风格与约定（命名、格式化、测试规范）
- 常见任务的操作方式（如如何运行测试、启动服务）
```

除 `/init` 自动生成外，你也可以手动维护它，或在配置里通过 `instructions` 引入更多规则文件（详见第四章）。

## 第一个对话 {#first-chat}

配置好 Provider 并 `/init` 后，即可开始对话。OpenCode 能回答关于代码库的问题：

```text
Give me a quick summary of the codebase.

How is authentication handled in @packages/functions/src/api/index.ts
```

用 `@` 可模糊搜索并引用项目内文件，文件内容会自动注入对话上下文。`@` 遵循 `.gitignore`，不会把忽略文件拽进来。

## 添加功能：先规划再构建 {#plan-build}

对较复杂的需求，建议先让 OpenCode 出方案：

```text
# 按 Tab 切换到 Plan 模式（右下角有模式指示）
# Plan 模式禁用文件修改，只产出实现方案

When a user deletes a note, flag it as deleted in the database,
then create a screen showing recently deleted notes.

# 满意后，再按 Tab 切回 Build 模式，让它落地
Sounds good! Go ahead and make the changes.
```

## 小结 {#summary}

本章完成了 Provider 配置（`/connect` 与 `auth login` 两种路径）、用 `/init` 生成 `AGENTS.md`，并发起了第一个对话与「先规划后构建」的流程。下一章深入核心用法：模式切换、`@` 引用、图片输入与会话管理。
