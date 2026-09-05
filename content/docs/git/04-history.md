---
title: 第四章 历史管理与撤销
linkTitle: 历史管理
description: reset、revert、stash、reflog、cherry-pick 等撤销与历史操作
weight: 114
---

# 历史管理与撤销

本章介绍如何安全地撤销改动、整理提交历史，以及在误操作时找回丢失的提交。

## reset 三种模式 {#reset}

`git reset` 将当前分支指针移动到指定提交，不同模式影响工作区和暂存区：

```bash
# 软重置：仅移动分支指针，保留暂存区与工作区
git reset --soft HEAD~1

# 混合重置（默认）：移动指针并重置暂存区，保留工作区
git reset --mixed HEAD~1
git reset HEAD~1          # 等价于 --mixed

# 硬重置：彻底丢弃目标提交之后的所有改动（危险）
git reset --hard HEAD~1
```

三种模式对比：

| 模式 | 分支指针 | 暂存区 | 工作区 |
|------|----------|--------|--------|
| --soft | 移动 | 保留 | 保留 |
| --mixed | 移动 | 重置 | 保留 |
| --hard | 移动 | 重置 | 重置 |

> `--hard` 会永久删除未提交的改动，使用前务必确认工作区已保存。

## 撤销提交（revert） {#revert}

`revert` 通过生成一次**新的提交**来抵消历史提交，不改写已有历史，适合已推送的提交：

```bash
# 撤销某次提交（会生成反向提交）
git revert <commit-hash>

# 撤销最近一次提交
git revert HEAD

# 撤销多次提交（生成多个反向提交）
git revert HEAD~3..HEAD

# 撤销但不自动提交，便于合并处理
git revert --no-commit HEAD~2..HEAD
```

`reset` vs `revert`：本地未推送的改动用 `reset` 整理；已共享的历史用 `revert` 撤销。

## 暂存改动（stash） {#stash}

临时保存未完成的改动，以便切换分支或拉取更新：

```bash
# 暂存当前工作区与暂存区
git stash

# 暂存并附带描述
git stash push -m "正在进行登录重构"

# 查看所有 stash
git stash list
# stash@{0}: On main: 正在进行登录重构

# 恢复最近一次暂存并删除它
git stash pop

# 仅恢复不删除
git stash apply stash@{0}

# 删除指定暂存
git stash drop stash@{0}

# 清空全部暂存
git stash clear
```

## 找回丢失提交（reflog） {#reflog}

`reflog` 记录 HEAD 的每一次移动，是误删提交的「后悔药」：

```bash
# 查看 HEAD 变动历史
git reflog
# a1b2c3d HEAD@{0}: reset: moving to HEAD~1
# e4f5g6h HEAD@{1}: commit: feat: 完成支付模块

# 找回被 reset 掉的提交
git reset --hard e4f5g6h

# 仅查看某分支的 reflog
git reflog show main
```

> reflog 是本地记录，默认保留约 90 天，且不会同步到远程。

## 拣选提交（cherry-pick） {#cherry-pick}

将某个（或某些）提交复制到当前分支：

```bash
# 拣选单个提交
git cherry-pick <commit-hash>

# 拣选一段连续提交（不含起点）
git cherry-pick A..C     # 应用 B、C

# 含起点
git cherry-pick A^..C

# 冲突时解决后继续
git add conflicted.txt
git cherry-pick --continue
```

## 交互式变基整理 {#interactive-rebase}

在合并前整理本地提交历史：

```bash
# 对最近 3 次提交进行交互式变基
git rebase -i HEAD~3
```

编辑器中的常用指令：

```text
pick   a1b2c3d feat: 添加登录页
reword b2c3d4e fix: 修正样式      # 修改提交信息
squash c3d4e5f 补充细节          # 合并到上一条
edit   d4e5f6g 草稿              # 暂停以便修改
drop   e5f6g7h 无用提交          # 删除
```

继续或中止：

```bash
git rebase --continue
git rebase --abort
```

## 小结 {#summary}

本章覆盖了 reset 三模式、revert 安全撤销、stash 临时保存、reflog 找回丢失提交，以及 cherry-pick 与交互式变基整理。下一章将介绍标签、子模块、Git Hooks 与常见场景速查。
