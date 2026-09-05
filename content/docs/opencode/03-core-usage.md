---
title: 第三章 核心用法
linkTitle: 核心用法
description: Plan/Build 模式、文件引用、图片输入与会话管理
weight: 123
---

# 核心用法

## Plan 与 Build 模式 {#plan-build}

OpenCode 有两种核心模式，用 **Tab 键**在右下角指示处切换：

```text
Plan 模式      禁用文件修改，只生成实现方案，适合先对齐思路
Build 模式     默认模式，可读取、编辑、运行命令，真正落地改动
```

典型工作流：

```text
# 1) 按 Tab 切到 Plan 模式，描述需求，让它出方案
Add a "recently deleted" screen and soft-delete support for notes.

# 2) 阅读方案，可继续补充上下文（如拖入参考图）
# 3) 按 Tab 切回 Build 模式，批准落地
Looks good, go ahead and implement it.
```

> 若 `OPENCODE_EXPERIMENTAL_PLAN_MODE` 尚未默认开启，可在环境变量中启用该实验特性。

## 文件引用：@ 语法 {#file-ref}

对话中用 `@` 模糊搜索并引用项目文件，内容会自动加入上下文：

```text
How is auth handled in @packages/functions/src/api/index.ts?

Compare our setup with @docs/README.md
```

在命令行里同样可用 `@` 指定文件：

```bash
# 让 Agent 基于某文件内容回答
opencode run @prompt.md "按这个模板生成代码"
```

配置的 references 也会出现在 `@` 自动补全中，输入 `@alias` 加入整块上下文，或 `@alias/` 在该引用内补全文件。

## 执行命令：! 前缀 {#bash}

消息以 `!` 开头可直接运行 shell 命令，输出作为工具结果注入对话：

```text
!ls -la
!git status
```

## 图片输入：拖拽与引用 {#images}

OpenCode 支持视觉输入，把截图或设计图喂给模型：

```text
# 直接把图片文件拖拽进终端即可附加到当前提示
# 也可在消息里引用本地图片路径

Take a look at this image [Image #1] and use it as the UI reference.
```

图片非常适合「按设计稿实现界面」「排查报错截图」等场景。

## 撤销与重做：/undo /redo {#undo-redo}

对改动不满意时，可用 `/undo` 回退最近一次消息及其产生的文件变更：

```text
/undo     # 撤销最近一条消息及其文件改动，并重新显示你的原话
/redo     # 在 /undo 之后，重做被撤销的改动
```

```text
# /undo 可多次执行，逐条回退
# 内部基于 Git 管理文件变更，因此项目需是 Git 仓库
```

## 会话管理：/sessions {#sessions}

OpenCode 用会话组织对话，可随时列出与切换：

```text
/sessions     # 列出并切换会话（别名 /resume、/continue）
/new          # 开始新会话（别名 /clear）
```

命令行等价方式：

```bash
opencode --continue          # -c：继续最近会话
opencode --session <id>      # -s：继续指定会话 ID
opencode --fork <id>         # 继续时 fork 出新分支会话
opencode session list        # 列出所有会话
opencode session delete <id> # 删除某个会话
```

## 压缩上下文：/compact {#compact}

长会话占用过多 token 时，可手动压缩（别名 `/summarize`）：

```text
/compact
```

也支持自动压缩（默认开启），可用环境变量 `OPENCODE_DISABLE_AUTOCOMPACT` 关闭。

## 导出与分享 {#export-share}

把会话导出为 Markdown，或生成可分享链接：

```text
/export     # 导出当前会话为 Markdown，并用默认编辑器打开
/share      # 生成当前会话分享链接并复制到剪贴板
/unshare    # 取消分享当前会话
```

会话默认不分享，`/share` 后才会上传并生成链接。

## 小结 {#summary}

本章覆盖了 Plan/Build 模式切换、`@` 文件引用、`!` 命令执行、图片输入、`/undo`/`/redo` 回退，以及会话管理与分享。下一章讲解如何通过 `opencode.json`、自定义 agent 与规则文件深度定制 OpenCode。
