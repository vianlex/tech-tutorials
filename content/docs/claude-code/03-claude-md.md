---
title: 第三章 上下文与 CLAUDE.md
linkTitle: CLAUDE.md
description: 项目记忆、CLAUDE.md 写法、分层配置与 /init
weight: 73
---

# 上下文与 CLAUDE.md

CLAUDE.md 是 Claude Code 最重要的配置文件：放在项目里的 Markdown 文件，给 Claude 提供"读代码读不出来的"持久上下文。本章讲它的写法、作用域与自动生成。

## 什么是 CLAUDE.md {#what}

CLAUDE.md 相当于给 Claude 的"项目手册"——构建命令、代码规范、架构决策、测试方式等。它会在每次会话自动加载，省去反复解释。

适合写进 CLAUDE.md 的内容：

- 常用命令：如何构建、测试、lint、部署
- 代码约定：命名风格、目录结构、禁止事项
- 架构决策：为什么这样选型、有哪些坑
- 工具偏好：用哪个测试框架、哪个库

不应写入：能从代码、Git 历史或已有文档推断出的信息。

## 用 /init 生成 {#init}

进入项目后运行 `/init`，Claude 会分析代码库并生成起步版 CLAUDE.md：

```text
claude > /init
# 自动探测构建系统、测试框架、代码模式，生成 CLAUDE.md 草稿
```

建议根文件保持精简（约 50–100 行），每条都问一句："删掉它 Claude 还能做对吗？"

## 手写示例 {#example}

```markdown
# 项目：My SaaS App

## 技术栈
- Next.js 14（App Router）
- TypeScript（strict 模式）
- Tailwind CSS
- Prisma + PostgreSQL

## 约定
- 文件名用 kebab-case
- 组件放在 src/components/
- API 路由放在 src/app/api/
- 一律用 async/await，禁止 .then()

## 测试
- 单元测试用 Jest，E2E 用 Playwright
- 提交前必须跑 npm test

## 注意事项
- 绝不提交 .env 文件
- 默认使用服务端组件
```

## 分层配置与作用域 {#scope}

CLAUDE.md 有多层，优先级由低到高：

```text
~/.claude/CLAUDE.md            全局：个人偏好、编码风格
.claude/CLAUDE.md             项目：项目约定、架构说明
CLAUDE.md（仓库根目录）        项目：快速的项目级指令
```

项目级规则覆盖用户级。对 monorepo 中不同目录有不同约定时，可用 `.claude/rules/` 子目录做**路径作用域规则**，按 Claude 正在处理的文件自动加载。

还可用 `@include` 指令在 CLAUDE.md 中引入其他文件，保持主文件精简：

```markdown
@include docs/conventions/backend.md
@include docs/conventions/frontend.md
```

## 记忆命令 {#memory}

`/memory` 查看当前已加载的文件与规则；Claude 也会跨会话自动保存有用上下文（编码偏好、项目约定、已解决的报错、架构决策）。可随时查看或整理。

```text
claude > /memory
# 列出 Claude 记住的偏好、约定与发现的模式
```

## 配置文件 settings.json {#settings}

除 CLAUDE.md 外，用户级与项目级 `settings.json` 也能持久化设置（模型、语言、环境变量、权限）。示例：

```json
{
  "model": "sonnet",
  "language": "简体中文",
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
    "API_TIMEOUT_MS": "300000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

用户级路径：`~/.claude/settings.json`；项目级：`.claude/settings.json`（覆盖用户级）。

## 小结 {#summary}

好的 CLAUDE.md 是"团队共享手册"，越精简越有效；`/init` 可一键生成草稿，再用分层与 `rules/` 细化。下一章进入权限、MCP、Hooks 与子代理等进阶能力。
