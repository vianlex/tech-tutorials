---
title: 第四章 进阶能力
linkTitle: 进阶能力
description: 权限模式、MCP 服务器、Hooks、自定义斜杠命令与子代理
weight: 74
---

# 进阶能力

这一章讲让 Claude Code 更可控、更强悍的机制：权限模式、MCP 扩展、Hooks 钩子、自定义斜杠命令与子代理。

## 权限模式 {#permissions}

Claude Code 用权限模式控制"何时需要你确认"，交互中用 `Shift+Tab` 切换：

```text
default      默认：写文件、跑命令、用 MCP 前都会询问
plan         计划：只读，不修改文件，先讨论方案
accept edits 自动允许文件编辑，命令仍会询问
auto         自动模式：按内置分类器自动放行（CI / 脚本用）
```

最高权限（非交互全放行）仅在沙箱中使用：

```bash
claude --dangerously-skip-permissions "自动修复所有 lint 报错"
```

在 `settings.json` 里配置精细规则，`deny` 优先级高于 `allow`：

```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Glob", "LS", "Bash(npm test*)"],
    "deny": ["Bash(rm -rf *)", "Bash(git push --force)"],
    "defaultMode": "default"
  }
}
```

规则支持通配，复合命令（`&&` `;` `|`）中任一段命中 `deny` 都会被整体拦截。

## MCP 服务器 {#mcp}

MCP（Model Context Protocol）让 Claude 连接外部工具（GitHub、数据库、浏览器等）。用 CLI 添加：

```bash
# 添加 GitHub MCP 服务器
claude mcp add github -- npx -y @anthropic-ai/mcp-server-github

# 添加文件系统 MCP 服务器（限定目录）
claude mcp add filesystem -- npx -y @anthropic-ai/mcp-server-filesystem /path/to/dir

# 列出 / 移除已配置的服务器
claude mcp list
claude mcp remove filesystem
```

也可在 `mcp.json` 中静态配置（用户级 `~/.claude/mcp.json` 或项目级 `.claude/mcp.json`）：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your-token-here" }
    }
  }
}
```

> 共享的 MCP 配置可提交到 `.mcp.json`，但**不要把令牌直接写进去**。

在交互中用 `/mcp` 查看连接状态与配置密钥。

## Hooks 钩子 {#hooks}

Hooks 是在特定生命周期事件自动运行你定义的命令（不是 Claude 主动选择的工具）。常见事件：`PreToolUse`（工具执行前，可拦截）、`PostToolUse`（执行后）、`Notification`、`Stop`、`UserPromptSubmit`。

项目级 `.claude/settings.json` 示例——编辑后自动 lint，提交前拦截危险命令：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "npm run lint",
        "matcher": "Edit"
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": "echo '即将调用: $TOOL_NAME'",
        "matcher": "Write"
      }
    ]
  }
}
```

`PreToolUse` 钩子退出码为 `2` 时直接阻断该工具调用，比内置权限更底层。

## 自定义斜杠命令 {#custom-commands}

把可复用的提示写进 `.claude/commands/`（项目级）或 `~/.claude/commands/`（用户级），文件即命令名：

```markdown
# .claude/commands/review.md
请对本次改动做一次代码评审，重点关注：
- 是否引入空指针 / 未处理异常
- 是否有明显的性能问题
- 命名与本项目约定是否一致
输出具体文件与行号。
```

```text
claude > /review
```

## 子代理（Subagents） {#subagents}

子代理是带独立上下文与工具集的专用 agent，适合隔离大型探索、并行处理，避免污染主会话。定义在 `.claude/agents/`（项目）或 `~/.claude/agents/`（用户）：

```markdown
---
name: security-reviewer
description: 审查 Java / Spring 代码中的安全风险
tools: Read, Grep, Glob, Bash
model: opus
---

审查目标 diff 是否存在：
- SQL 注入与不安全的动态查询
- 认证 / 授权绕过
- 提交到代码中的密钥
- 不安全的反序列化或命令执行
返回具体文件与行号，除非明确要求否则不要改写代码。
```

内置子代理有 `Explore`（只读探索，轻量模型）、`Plan`（只读规划）、`general-purpose`（完整工具集）。用自然语言或 `/agents` 查看并调用。

## 小结 {#summary}

权限模式管"确认"，MCP 扩"能力"，Hooks 做"自动化"，子代理隔离"重活"。下一章用真实工作流把这些串起来，并给出最佳实践与避坑清单。
