---
title: 第四章 扩展与自定义
linkTitle: 扩展与自定义
description: Pi Agent 的扩展系统、自定义工具/命令与项目集成
weight: 64
---

# 扩展与自定义

## 扩展系统概览 {#extension-overview}

Pi Agent 通过 **Pi 包（Pi Package）** 分发扩展、技能、提示模板与主题。扩展以**完整系统权限**运行，可注册自定义工具、替换内置工具、监听事件、定制压缩与权限等。

```text
扩展可做的事：
- 注册自定义工具 / 命令（pi.registerTool / pi.registerCommand）
- 监听事件：tool_call、project_trust 等（pi.on）
- 子代理、计划模式、Git 检查点、MCP 集成
- 自定义编辑器、状态行、主题、压缩策略
```

## 安装扩展包 {#install-ext}

使用 `pi install` 从多种来源安装：

```bash
# 从 npm 安装
pi install npm:@foo/pi-tools
pi install npm:@foo/pi-tools@1.2.3      # 固定版本

# 从 git 安装（支持 tag / commit）
pi install git:github.com/user/repo
pi install git:github.com/user/repo@v1

# 从本地路径安装
pi install ./my-local-extension

# -l：项目本地安装（存至 .pi/git/ 或 .pi/npm/）
pi install -l npm:@foo/pi-tools
```

管理已安装包：

```bash
pi list                  # 列出已安装包
pi remove npm:@foo/pi-tools   # 卸载（uninstall 同义）
pi update --all          # 更新 pi 及所有包
pi update --self         # 仅更新 pi
pi update --extensions   # 仅更新扩展
pi config                # 启用 / 禁用包资源（扩展、技能等）
```

> 安全警告：Pi 包执行任意代码，安装前请审查源码。

## 编写自定义扩展 {#write-ext}

扩展是一个默认导出函数的 TypeScript 模块：

```typescript
// my-extension/index.ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // 注册一个自定义工具
  pi.registerTool({
    name: "deploy",
    description: "部署当前项目",
    parameters: { type: "object", properties: {} },
    execute: async () => {
      // 调用 bash 执行部署脚本
      return { output: "deployed" };
    },
  });

  // 注册一个斜杠命令
  pi.registerCommand("stats", {
    description: "显示项目统计",
    run: async (ctx) => "TODO: stats",
  });

  // 监听事件
  pi.on("tool_call", async (event, ctx) => {
    console.log("工具调用:", event.tool);
  });
}
```

在 `package.json` 中声明 Pi 包（含 `pi` 键）：

```json
{
  "name": "my-pi-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

无 manifest 时也会自动发现常规目录。扩展放置位置：

```text
~/.pi/agent/extensions/   全局
.pi/extensions/           项目级
Pi 包内部目录
```

## 技能 Skills {#skills}

技能遵循 [Agent Skills 标准](https://agentskills.io)，通过 `/skill:name` 调用或自动加载：

```markdown
<!-- ~/.pi/agent/skills/my-skill/SKILL.md -->
# My Skill
Use this skill when the user asks about X.
## Steps
1. Do this
2. Then that
```

技能搜索目录：

```text
~/.pi/agent/skills/   全局
~/.agents/skills/     兼容目录
.pi/skills/           项目级（从 cwd 向上遍历）
.agents/skills/
```

启动时加载自定义技能：

```bash
pi --skill ./skills/my-skill
pi --no-skills        # 禁用技能发现
```

## 项目集成与信任 {#project-trust}

项目级资源与配置放在 `.pi/` 目录：

```text
.pi/settings.json      项目设置（需信任后加载）
.pi/prompts/           提示模板（/name 展开）
.pi/skills/            本地技能
.pi/extensions/        本地扩展
.pi/themes/            本地主题
.pi/SYSTEM.md          系统提示替换
.pi/git/  .pi/npm/     本地安装包的位置
```

首次在含项目本地设置/资源的目录交互启动时，Pi 会请求**信任**：

```text
# 交互模式中保存信任决策（写入 ~/.pi/agent/trust.json，需重启生效）
/trust

# 非交互模式：用 defaultProjectTrust 或 CLI 控制
pi -a           # --approve：本次运行信任项目本地文件
pi -na          # --no-approve：本次运行忽略项目文件

# 关闭项目资源发现
pi --no-extensions
pi --no-themes
```

## 小结 {#summary}

通过 `pi install` 可快速接入社区扩展，用 `ExtensionAPI` 能编写自定义工具与命令；项目约定应放入 `.pi/` 并经过信任。下一章用真实工作流把以上能力串起来。
