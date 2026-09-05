---
title: 第二章 分支与合并
linkTitle: 分支合并
description: Git 分支管理、merge 与 rebase、冲突解决
weight: 112
---

# 分支与合并

分支是 Git 最强大的特性之一，它让开发者可以安全地并行开发而不互相干扰。本章介绍分支的创建切换、合并、变基及冲突处理。

## 分支基础 {#branch-basics}

```bash
# 查看本地分支（* 表示当前分支）
git branch

# 查看所有分支（含远程）
git branch -a

# 创建新分支
git branch feature/login

# 切换分支
git switch feature/login

# 创建并切换到新分支（推荐）
git switch -c feature/login

# 删除已合并的分支
git branch -d feature/login

# 强制删除未合并分支（谨慎）
git branch -D feature/login
```

> 现代 Git 推荐使用 `git switch` / `git switch -c` 替代 `git checkout` 来切换分支，语义更清晰。

## 合并分支 {#merge}

将其他分支的改动合并到当前分支：

```bash
# 切换到目标分支
git switch main

# 合并 feature 分支
git merge feature/login
# 合并成功会生成一次新的合并提交

# 禁用快进合并，始终保留合并提交
git merge --no-ff feature/login

# 合并前预览差异
git diff main...feature/login
```

## 变基 {#rebase}

`rebase` 将当前分支的提交「重放」到目标分支之上，得到线性历史：

```bash
# 将当前分支变基到 main
git switch feature/login
git rebase main

# 变基过程中遇到冲突，解决后继续
# 编辑冲突文件 -> git add -> 继续
git add conflicted-file.txt
git rebase --continue

# 中止变基，回到操作前状态
git rebase --abort
```

merge 与 rebase 的区别：

| 操作 | 历史形态 | 适用场景 |
|------|----------|----------|
| merge | 保留分支拓扑，有合并提交 | 公共分支、需要完整历史 |
| rebase | 线性、整洁 | 本地分支整理后再合并 |

> 黄金法则：不要对已推送到远程的提交做 rebase，否则会改写他人历史。

## 冲突解决 {#conflict}

当两个分支修改了同一处内容，合并/变基时会产生冲突：

```bash
# 合并触发冲突
git merge feature/login
# CONFLICT (content): Merge conflict in src/app.js

# 冲突文件中的标记
# <<<<<<< HEAD
# 当前分支的内容
# =======
# 对方分支的内容
# >>>>>>> feature/login
```

解决步骤：

```bash
# 1. 手动编辑文件，保留正确内容并删除标记
# 2. 标记为已解决
git add src/app.js
# 3. 完成合并提交（merge 时）
git commit
# 或（rebase 时）
git rebase --continue

# 查看剩余未解决的冲突
git diff --name-only --diff-filter=U

# 使用图形化工具辅助解决
git mergetool
```

## 分支策略简介 {#strategy}

常见的分支管理模型：

```bash
# Git Flow：长期维护 main（生产）与 develop（开发）分支
main        o-----o-----------o----  (生产发布)
             \   /           /
develop      o-o-o-o-o-o-o-o-o
               \   / \   /
feature         f1  f2  f3

# GitHub Flow：只有一个 main，所有改动通过短生命周期分支 + PR
main   o--o--o--o--o
        \  \  \  \
feat    a  b  c  d

# Trunk-Based：大多数提交直接进 main， release 分支按需切出
```

常用约定：

- `main`：稳定可发布分支
- `feature/*`：功能开发分支
- `hotfix/*`：线上紧急修复
- `release/*`：发布准备分支

## 重命名与清理 {#rename-clean}

```bash
# 重命名本地分支
git branch -m old-name new-name

# 清理已失效的远程跟踪分支
git fetch --prune

# 查看各分支最后一次提交时间，便于清理
git branch -v
```

## 小结 {#summary}

本章掌握了分支的创建切换、merge 与 rebase 的差异、冲突解决流程，以及常见分支策略。下一章将进入远程协作，学习 remote、push/pull 与 Pull Request 工作流。
