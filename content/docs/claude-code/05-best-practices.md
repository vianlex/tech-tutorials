---
title: 第五章 实战技巧与最佳实践
linkTitle: 最佳实践
description: Claude Code 典型工作流、大任务拆解、效率技巧与常见坑
weight: 75
---

# 实战技巧与最佳实践

把前几章的能力组合成可靠工作流，才能稳定产出。本章给出典型流程、大任务拆解方法、效率技巧与避坑清单。

## 典型工作流 {#workflow}

复杂改动推荐"探索 → 计划 → 执行 → 验证"四步：

```text
claude > 先只读地读一遍仓库，搞清楚鉴权中间件怎么调用的（探索）
claude > 基于上面的理解给我一份改造计划，不要改代码（计划）
claude > 按方案实现，每步改完跑 npm test（执行）
claude > 用 /diff 检查改动，再补一个集成测试（验证）
```

测试驱动开发（TDD）也很顺手：先写失败测试让 Claude 看到失败，再迭代到通过，避免凭空猜测实现。

## 大任务拆解 {#breakdown}

任务越大越要拆细、给清验收标准，并显式说明项目目录与目标：

```text
claude > 项目在 ./web，目标是给购物车加优惠券功能：
1. 数据模型新增 Coupon 表
2. service 层加校验与计算逻辑
3. 暴露 POST /cart/coupon 接口
4. 补单元测试与接口测试
每步完成后停下来等我确认再继续。
```

Claude Code 自带 Task 工具会显示待办清单，给你进度可见性。多步独立任务可交子代理并行，长时调查用 `/background` 后台跑。

## 巧用上下文 {#context-tips}

```text
# 用 @ 精准喂关键文件，而不是让 Claude 大海捞针
claude > 参考 @src/payment/charge.ts 重构退款逻辑

# 用 ! 直接带入命令结果
claude > 当前分支落后于 main 多少？ !git rev-list --count main..HEAD

# 上下文过长时压缩，而不是开新会话丢信息
claude > /compact
```

写好 CLAUDE.md（见第三章）是"一次投入、长期回报"的最高性价比动作。

## 效率技巧 {#efficiency}

```bash
# 非交互一次性任务，结果直接进管道
claude -p "给所有 .ts 文件头加 Apache-2.0 许可证注释"

# 恢复上次会话继续未完成的活
claude -c

# 用 /permissions 随时查看当前放行与拦截规则
# 用 /cost 关注本会话 token 与费用
```

把重复操作沉淀为自定义斜杠命令（`.claude/commands/`）和子代理（`.claude/agents/`），团队共享后人人受益。

## 隔离并行工作 {#isolation}

并行特性 / 修复用 Git worktree 隔离，互不干扰：

```bash
claude --worktree feature-auth
claude --worktree bugfix-payment
```

子代理改文件时也会在临时 worktree 中工作，无改动则自动清理。

## 常见坑 {#pitfalls}

- **CLAUDE.md 过长**：删掉从代码能推断的规则，保持精简。
- **上下文过载**：一个会话混太多主题会用 `/clear` 重开，或写 `HANDOFF.md` 交接。
- **死循环修正**：连续三次失败就换更清晰的提示重新开始。
- **权限过宽**：优先 deny-by-default，再叠加 allow 规则。
- **测试全绿≠正确**：要求额外证据或人工复核。
- **无浏览器环境忘设 Key**：CI 用 `ANTHROPIC_API_KEY` 而非 OAuth。
- **sudo 装 npm 包**：会导致后续文件权限问题，用 nvm 或修正 npm prefix。

## 小结 {#summary}

可靠使用 Claude Code = 清晰 CLAUDE.md + 先计划后执行 + 改完验证 + 用 worktree / 子代理隔离重活 + 收紧权限。至此五章结束，你已经可以从安装一路用到进阶工作流。
