---
title: 第五章 进阶与最佳实践
linkTitle: 进阶与最佳实践
description: CLI 非交互执行、serve 无头 API、GitHub agent 与效率技巧
weight: 125
---

# 进阶与最佳实践

## CLI 非交互执行：opencode run {#run}

`opencode run` 不启动 TUI，直接把提示交给模型，适合脚本与自动化：

```bash
# 直接提问
opencode run "Explain how closures work in JavaScript"

# 指定模型、Agent、附加上下文
opencode run "Add input validation to the login form" \
  --model anthropic/claude-sonnet-4-5 \
  --agent build \
  --file src/login.ts

# 输出原始 JSON 事件流（便于程序解析）
opencode run "List all routes" --format json

# 自动批准非显式拒绝的权限
opencode run "Refactor utils.ts" --auto

# 附加到已运行的 serve 实例，避免每次冷启动 MCP
opencode serve &
opencode run --attach http://localhost:4096 "Explain async/await in JS"
```

常用参数：`--model/-m`、`--agent`、`--file/-f`、`--format`、`--session/-s`、`--continue/-c`、`--share`、`--title`、`--variant`、`--thinking`、`--auto`、`--dir`。

## 无头 API：opencode serve {#serve}

`opencode serve` 启动一个不带 TUI 的 HTTP 服务，对外提供 API 访问：

```bash
# 启动无头服务（默认随机端口）
opencode serve --port 4096 --hostname 0.0.0.0

# 启用 HTTP Basic Auth（用户名默认 opencode）
OPENCODE_SERVER_PASSWORD=secret opencode serve
```

配套命令：

```bash
opencode attach http://10.20.30.40:4096   # 用 TUI 连上远端后端
opencode web --port 4096                   # 启动带网页界面的无头服务
opencode acp                               # 启动 ACP（Agent Client Protocol）服务，stdin/stdout 通信
```

## GitHub Agent：自动化仓库 {#github}

`opencode github install` 在仓库中安装 GitHub Agent（配置 Actions 工作流），常用于 PR 自动处理：

```bash
# 在当前仓库安装 GitHub Agent（交互引导配置）
opencode github install

# 在 GitHub Actions 中运行（一般无需手动调用）
opencode github run --event "issue_comment" --token "$GITHUB_TOKEN"
```

## 多会话并行 {#parallel}

OpenCode 原生支持多会话，同一项目可同时跑多个 Agent：

```bash
# 终端 1：处理功能 A
opencode --session feat-a

# 终端 2：处理功能 B（互不干扰）
opencode --session feat-b

# 或在一个 TUI 内用 /sessions 切换、/new 开新会话
```

利用多会话可把「调研」「实现」「审查」拆给不同 Agent 并行推进。

## 会话与统计维护 {#stats}

定期清理与复盘会话：

```bash
opencode session list -n 20        # 最近 20 个会话（table/json）
opencode session delete <id>      # 删除指定会话
opencode stats --days 7            # 近 7 天 token 用量与成本
opencode stats --models 5          # 按模型拆分用量（Top 5）
opencode import https://opncd.ai/s/abc123   # 从分享链接导入会话
```

## 效率技巧 {#tips}

```text
- 复杂需求先 Tab 进 Plan 模式对齐方案，再切回 Build 落地
- 用 @文件 精准喂上下文，避免让模型全库扫描
- 把常用流程沉淀为自定义命令（.opencode/commands/*.md）
- 长会话及时 /compact，控制 token 成本
- 团队共享 opencode.json 与 AGENTS.md，统一约定
- 用 opencode run --auto 做批量/脚本化改动
- 升级：opencode upgrade（可指定版本 opencode upgrade v0.1.48）
- 卸载：opencode uninstall
```

## 小结 {#summary}

本章覆盖了 `opencode run` 非交互执行、`serve` 无头 API 与 `attach`/`web` 形态、GitHub Agent 自动化、多会话并行，以及会话维护与效率技巧。至此你已具备从安装到进阶使用 OpenCode 的完整能力。
