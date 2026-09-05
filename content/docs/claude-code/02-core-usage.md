---
title: 第二章 核心用法
linkTitle: 核心用法
description: Claude Code 斜杠命令、@文件引用、图片输入与 Git 集成
weight: 72
---

# 核心用法

掌握交互技巧能显著提升效率。本章覆盖斜杠命令、`@` 文件引用、图片输入、Git 集成与会话恢复。

## 斜杠命令 {#slash-commands}

在 `claude >` 提示符下输入 `/` 加命令名，常用如下：

```text
/help        列出所有斜杠命令及说明
/clear       清空当前对话，开始新会话（保留目录分析）
/compact     压缩会话历史以释放上下文窗口
/context     查看当前 token 用量与已加载文件
/cost        查看本次会话的 token 消耗与费用
/diff        显示 Claude 修改过的文件差异
/doctor      诊断安装与连接是否正常
/init        分析项目并生成 CLAUDE.md
/mcp         管理 MCP 服务器连接
/permissions 查看当前权限规则
/memory      查看已加载的记忆与规则
/resume      恢复之前的会话
/rewind      回退到之前的某一轮（代码与对话）
/config      打开交互式设置面板
```

查看全部命令随时用 `/help`。

## @文件引用 {#file-refs}

用 `@` 把指定文件或目录注入当前消息作为上下文：

```text
claude > 参考 @src/auth/login.ts 实现登出接口
claude > 读取 @docs/api/ 下所有文档，总结鉴权流程
```

`!` 前缀可先执行 Shell 命令、把结果带入对话：

```text
claude > 看一下最近的提交 !git log --oneline -5
```

## 图片输入 {#image-input}

Claude Code 支持直接读取图片（截图、报错图、设计稿）。把图片路径用 `@` 引用，或把图片放到命令行参数里：

```bash
# 启动时直接附带图片
claude "根据 @screenshot.png 修复这个报错界面"

# 交互中引用
claude > 这个布局对不上 @design/mockup.png，请调整 CSS
```

## Git 集成 {#git}

Claude Code 原生理解 Git，能检查改动、切分支、提交与创建 PR。

```text
claude > 看一下当前未提交的改动并帮我写 commit message
claude > 把 feature/login 合并到 main 并解决冲突
claude > 基于当前分支创建一个 PR，标题写"feat: 登录模块"
```

常用 Git 相关交互：

```text
claude > 用 /diff 回顾你改了哪些文件
claude > 这些改动我不满意，用 /rewind 回退到上一轮
claude > 给本次修改加一个清晰的提交信息并提交
```

## 会话恢复 {#resume}

每次会话的历史可恢复，适合跨天继续未完成的任务。

```bash
# 恢复最近一次会话
claude -c

# 启动时直接带一条提示
claude -c "继续昨天的重构，先跑通测试"

# 交互中用命令恢复更早的会话
/resume
```

忘记上下文是否过大时，用 `/compact` 手动压缩，或在占用接近 95% 时 Claude 会自动压缩。

## 非交互（打印）模式 {#print-mode}

`-p` 让 Claude Code 执行一条指令后直接输出结果，适合脚本与 CI：

```bash
# 一次性命令，结果打印到标准输出
claude -p "给 src/calc.ts 加一句函数级注释，不要改逻辑"

# 配合管道，从文件读需求
cat request.txt | claude -p "按上述要求修改代码"
```

## 小结 {#summary}

`/help` 探索命令、`@` 精准喂上下文、`!` 带 Shell 结果、`claude -c` 续上会话，是日常最高频的操作。下一章讲如何写好 CLAUDE.md 让 Claude 记住你的项目。
