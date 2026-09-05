---
title: 第三章 远程协作
linkTitle: 远程协作
description: remote、push/pull/fetch、SSH 配置与协作工作流
weight: 113
---

# 远程协作

Git 是分布式的，每个开发者都拥有完整仓库副本。本章介绍如何连接远程仓库、同步代码，以及基于 Pull Request 的协作流程。

## 管理远程仓库 {#remote}

```bash
# 查看已配置的远程（默认名为 origin）
git remote -v

# 添加远程仓库
git remote add origin git@github.com:user/repo.git

# 修改远程地址（如从 HTTPS 切换到 SSH）
git remote set-url origin git@github.com:user/repo.git

# 重命名与删除
git remote rename origin upstream
git remote remove upstream
```

## 推送与拉取 {#push-pull}

```bash
# 推送当前分支到 origin，并建立跟踪关系
git push -u origin main

# 推送后续提交（已建立跟踪后可简写）
git push

# 推送所有分支
git push --all origin

# 拉取并合并远程更新到本地
git pull

# 等价于 fetch + rebase，保持线性历史
git pull --rebase

# 仅获取远程更新，不自动合并
git fetch origin
```

`fetch` 与 `pull` 的区别：`fetch` 只下载数据不改动工作区；`pull` = `fetch` + 自动 `merge`/`rebase`。

## 配置 SSH {#ssh}

使用 SSH 协议可避免每次输入密码：

```bash
# 生成 ED25519 密钥（推荐）
ssh-keygen -t ed25519 -C "you@example.com"

# 查看公钥内容，复制到 Git 托管平台的 SSH 设置中
cat ~/.ssh/id_ed25519.pub

# 测试与 GitHub 的连接
ssh -T git@github.com
# Hi user! You've successfully authenticated.
```

配置多账号时的 `~/.ssh/config` 示例：

```sshconfig
# GitHub 个人账号
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519

# 企业账号
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
```

## Pull Request 工作流 {#pr-workflow}

典型的分支协作流程：

```bash
# 1. 从最新的 main 切出功能分支
git switch main && git pull
git switch -c feature/search

# 2. 开发、提交
git add . && git commit -m "feat: 实现搜索功能"

# 3. 推送到远程
git push -u origin feature/search

# 4. 在平台发起 Pull Request / Merge Request
# 5. 评审通过后合并，删除远端分支
git push origin --delete feature/search
```

合并后保持本地 main 同步：

```bash
git switch main
git pull
git branch -d feature/search   # 合并后本地分支已可删除
```

## Fork 协作 {#fork}

为开源项目贡献代码时常用 fork 模式：

```bash
# 1. 在平台 Fork 仓库，然后克隆自己的副本
git clone git@github.com:yourname/repo.git
cd repo

# 2. 添加上游仓库（原始项目）为 upstream
git remote add upstream git@github.com:original/repo.git

# 3. 同步上游最新改动
git fetch upstream
git merge upstream/main

# 4. 在自己的分支开发并推送
git switch -c fix-typo
git commit -am "docs: 修正文档错别字"
git push -u origin fix-typo

# 5. 向上游仓库发起 Pull Request
```

## 跟踪分支 {#tracking}

```bash
# 查看本地分支与远程的跟踪关系
git branch -vv

# 基于远程分支创建本地跟踪分支
git switch -c develop --track origin/develop

# 将本地已有分支关联远程分支
git branch --set-upstream-to=origin/develop
```

## 小结 {#summary}

本章掌握了 remote 管理、push/pull/fetch 同步、SSH 配置、Pull Request 与 fork 协作流程。下一章将学习历史管理与撤销技巧，包括 reset、revert、stash 等命令。
