---
title: 第五章 实战与最佳实践
linkTitle: 实战与最佳实践
description: Pi Agent 的典型工作流、真实案例与效率技巧
weight: 65
---

# 实战与最佳实践

## 典型工作流 {#workflow}

日常开发中的推荐流程：先写 `AGENTS.md` 约定项目，再进入会话迭代。

```text
1. 在项目根目录编写 AGENTS.md（技术栈、目录结构、代码风格）
2. pi 进入交互会话，用自然语言描述任务
3. 用 @ 引用相关文件，用 ! 让 Agent 跑测试/构建
4. 不满意时 /tree 回到历史节点，/fork 另开分支尝试
5. /compact 压缩长上下文，保持会话轻量
6. /export 归档关键会话为 HTML 留档
```

```bash
# 启动时即命名会话，便于后续 -r 找回
pi --name "实现登录接口"
```

## 非交互 / CI 模式 {#headless}

把 Pi Agent 嵌入脚本与流水线，用 `-p` 打印或 `--mode` 结构化输出：

```bash
# 打印模式：直接拿到结果，适合脚本
pi -p "为 src/calc.ts 生成单元测试"

# 管道输入
git diff | pi -p "评审这次改动，指出风险"

# JSON 行事件流（程序解析）
pi --mode json "重构 utils.ts"

# RPC 模式：进程集成（严格 LF 分隔 JSONL）
pi --mode rpc "..."

# 限制工具，提升自动化安全性
pi -p -t read,bash "运行 npm test 并总结失败用例"
pi -p -xt edit,write "只分析不修改代码"
```

## 真实案例 {#cases}

```bash
# 案例 1：快速搭脚手架
pi "用 TypeScript + Express 创建一个带健康检查端点的服务，包含 Dockerfile"

# 案例 2：代码审查
pi -p @src/payment.ts "检查这里的并发与错误处理问题"

# 案例 3：结合视觉模型看图修 Bug
pi -p @error-screenshot.png "这是什么报错，怎么修？"

# 案例 4：多步骤重构，中途分支
pi "把 callbacks 改成 async/await"
# 会话中：/fork 从某节点尝试另一种实现，对比后再决定
```

## 效率技巧 {#tips}

模型与上下文：

```bash
# 用思考级别控制成本与质量
pi --model sonnet --thinking low "简单改名"
pi --model opus  --thinking high "设计并发方案"

# 固定循环模型范围，Ctrl+P 快速切换
pi --models "sonnet,opus,gpt-4o"
```

工具与权限：

```bash
# 只读分析：禁用写入类工具
pi -xt edit,write "解释这段正则"

# 临时会话做实验，不污染历史
pi --no-session "随便问个问题"
```

项目级提速：

```text
# 把常用提示写成模板，放在 .pi/prompts/，用 /name 直接展开
# 把团队规范固化到 AGENTS.md，减少重复说明
# 用 @ 精确引用文件，避免让 Agent 全仓扫描
# 长任务中途 /compact，避免上下文溢出导致质量下降
```

会话再利用：

```bash
pi -c                 # 继续上次，承接上下文
pi -r                 # 挑选历史会话
pi --fork <id>        # 基于旧会话开新枝
/share                # 生成可分享的会话回顾链接
```

## 小结 {#summary}

Pi Agent 既能交互式结对编程，也能以 `-p`/`--mode` 融入自动化；配合 `AGENTS.md`、扩展与分支会话，可覆盖从脚手架到 CI 审查的多种场景。至此，本教程的安装、使用、配置、扩展与实战已全部覆盖。
