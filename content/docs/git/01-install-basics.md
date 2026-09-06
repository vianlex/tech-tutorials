---
title: 第一章 安装与基础操作
linkTitle: 基础操作
description: Git 安装、初始配置与基本命令
weight: 111
---

# 安装与基础操作

本章介绍如何在各平台安装 Git、完成首次使用前的全局配置，以及最常用的本地仓库操作命令。

## 安装 Git {#install}

Git 2.40+ 在各平台的安装方式：

```bash
# macOS（使用 Homebrew）
brew install git

# Windows（使用 Chocolatey）
choco install git

# Debian/Ubuntu
sudo apt-get update && sudo apt-get install git

# 验证安装版本
git --version
# git version 2.45.1
```

## 初始配置 {#config}

首次使用需配置用户名与邮箱（提交时会记录在作者信息中）：

```bash
# 全局配置（对所有仓库生效）
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# 设置默认分支名（现代 Git 推荐 main）
git config --global init.defaultBranch main

# 开启彩色输出与更友好的 diff
git config --global color.ui auto
git config --global diff.colorMoved default

# 查看当前配置
git config --list
```

## 初始化与克隆 {#init-clone}

创建新仓库或从远程克隆：

```bash
# 在当前目录初始化一个空仓库
git init

# 在指定目录初始化
git init my-project
cd my-project

# 克隆远程仓库（HTTPS 或 SSH）
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git

# 克隆指定分支
git clone -b develop https://github.com/user/repo.git
```

## 查看状态 {#status}

`git status` 用于随时查看工作区与暂存区的状态：

```bash
git status

# 精简输出（两列状态标记）
git status -s
#  M src/main.go   已修改未暂存
# A  README.md    已暂存
```

状态标记含义：左侧列表示暂存区状态，右侧列表示工作区状态；`M` 修改、`A` 新增、`??` 未跟踪。

## 暂存与提交 {#add-commit}

标准的工作流是「修改 → 暂存 → 提交」：

```bash
# 暂存单个文件
git add README.md

# 暂存当前目录所有改动（谨慎使用）
git add .

# 暂存已跟踪文件的更新（不含新文件）
git add -u

# 提交并填写信息
git commit -m "feat: 添加项目说明文档"

# 跳过暂存区，直接提交所有已跟踪文件的改动
git commit -a -m "fix: 修正错别字"

# 修补上一次提交（修改信息或补充文件）
git commit --amend -m "feat: 添加项目说明文档（补充示例）"
```

## 查看提交历史 {#log}

```bash
# 标准日志
git log

# 单行精简展示
git log --oneline

# 图形化展示分支合并关系
git log --oneline --graph --all

# 查看最近 5 条，并显示文件改动统计
git log -5 --stat

# 按作者筛选
git log --author="Your Name"
```

## 忽略文件 {#gitignore}

使用 `.gitignore` 排除不需要纳入版本控制的文件：

```bash
# 忽略编译产物与依赖目录
echo "node_modules/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.log" >> .gitignore

# 排除所有 .env 文件
echo ".env" >> .gitignore
```

`.gitignore` 常见规则示例：

```gitignore
# 注释以 # 开头
# 忽略指定文件
secret.txt

# 忽略整个目录
build/

# 忽略所有 .log 文件
*.log

# 但保留 important.log
!important.log

# 仅忽略根目录下的 TODO
/TODO
```

查看哪些被忽略、以及文件为何被忽略：

```bash
# 列出被忽略的文件
git status --ignored

# 检查某个文件被哪条规则忽略
git check-ignore -v config.json
```

## 查看差异 {#diff}

`git diff` 是排查「我到底改了什么」最常用的命令，它有多种用法：

```bash
# 工作区 vs 暂存区（已修改但未 git add 的内容）
git diff

# 暂存区 vs 最新提交（已 git add 但未 commit 的内容）
git diff --staged
git diff --cached             # 同 --staged

# 工作区 vs 最新提交（工作区的全部未提交改动）
git diff HEAD

# 两个提交之间的差异
git diff <commit-a> <commit-b>

# 两个分支的差异（... 三点表示「共同祖先之后」的差异）
git diff main...feature/login

# 仅查看某个文件的差异
git diff -- src/app.js

# 仅看文件统计（不改动的行数）
git diff --stat
```

实用技巧：

```bash
# 单词级 diff，适合看一段文本中改了哪个词
git diff --word-diff

# 忽略空白差异（缩进被改、tab/空格切换时不显示）
git diff -w
git diff --ignore-all-space

# 仅显示改动的文件名（用于快速看影响范围）
git diff --name-only

# 在 diff 中搜索关键词
git diff -S "TODO"            # 搜索「删除/新增含 TODO 的行」
git diff -G "function login"  # 搜索「改动触及该模式的行」
```

## 查看某次提交的内容 {#show}

`git show` 用于查看某个对象（提交、tag、blob）的详细信息：

```bash
# 查看某次提交的完整信息 + diff
git show <commit-hash>

# 仅显示提交信息
git show --stat <commit-hash>

# 仅看该提交的文件名
git show --name-only <commit-hash>

# 查看某个 tag 指向的内容
git show v1.0.0

# 查看某个文件的当前内容（HEAD 版本）
git show HEAD:src/app.js
```

## 高阶 log 用法 {#log-advanced}

日常排查问题时，`git log` 配合参数非常强大：

```bash
# 按提交信息搜索
git log --grep="登录"          # 匹配提交信息中含「登录」
git log --grep="^fix"          # 正则：fix 开头的提交

# 按代码改动搜索
git log -S "getUserById"       # 该字符串被增删的所有提交
git log -G "TODO"              # 改动触及该正则的所有提交

# 按时间/作者/范围筛选
git log --since="2 weeks ago"
git log --until="2026-01-01"
git log --author="alice"
git log --since="2026-08-01" --until="2026-09-01"

# 自定义输出格式
git log --pretty=format:"%h %an %s"     # 紧凑格式：hash 作者 主题
git log --pretty=format:"%h %ad %s" --date=short

# 查看某个文件的所有改动历史（跟随重命名）
git log --follow -- src/app.js

# 仅看某段时间内的某文件的改动
git log --since="2026-01-01" -- src/app.js

# 图形化查看分支合并拓扑
git log --oneline --graph --all --decorate
```

常用格式占位符：`%h` 短 hash、`%H` 完整 hash、`%an` 作者、`%ae` 邮箱、`%ad` 日期、`%s` 主题、`%b` 正文。

## checkout / restore / switch 三件套 {#restore-checkout-switch}

现代 Git 拆分了原本由 `git checkout` 一肩挑的功能：

| 命令 | 用途 | 等价旧写法 |
|------|------|-----------|
| `git switch <branch>` | 切换分支 | `git checkout <branch>` |
| `git switch -c <new>` | 创建并切换分支 | `git checkout -b <new>` |
| `git restore <file>` | 丢弃工作区某文件的改动 | `git checkout -- <file>` |
| `git restore --staged <file>` | 取消暂存（文件回到工作区） | `git reset HEAD <file>` |
| `git restore --staged --worktree <file>` | 同时恢复工作区与暂存区 | `git checkout HEAD -- <file>` |

> 建议：新写的脚本与教程统一用 `switch` + `restore`，语义最清晰。

## 常用 alias 配置 {#aliases}

把高频命令写成别名能显著提升效率，写入 `~/.gitconfig`：

```ini
[alias]
    st = status -sb
    co = checkout
    br = branch
    lg = log --oneline --graph --decorate --all
    last = log -1 --stat
    unstage = restore --staged
    discard = restore
    amend = commit --amend --no-edit
    pf = push --force-with-lease
    aa = add -A
    cm = commit -m
    cmn = commit -m
```

使用：

```bash
git st           # 等价 git status -sb
git lg           # 图形化 log
git unstage .    # 取消全部暂存
git pf           # 安全强制推送
```

## 清理未跟踪文件 {#clean}

```bash
# 预览将被删除的文件（不实际执行）
git clean -nd

# 删除未跟踪的文件
git clean -f

# 同时删除未跟踪的目录
git clean -fd

# 连同被忽略的文件也清理（彻底，常用于重置工作区）
git clean -fdx

# 与 reset --hard 配合：彻底回到 HEAD 状态
git reset --hard && git clean -fdx
```

> `git clean -fdx` 会**永久删除**所有未跟踪 + 被忽略的文件（包括 `.env`、`node_modules/`），执行前务必确认。

## 完整日常流程回顾 {#daily-flow}

把本章命令串成一个最常用的工作日循环：

```bash
# 1. 起床开始干活：同步最新
git switch main
git pull --rebase

# 2. 开新功能
git switch -c feature/search

# 3. 边写边查
git status
git diff
git add src/search.ts
git commit -m "feat: 接入搜索接口"

# 4. 推到远端
git push -u origin feature/search

# 5. 推送前想再改最后一次
git commit --amend -m "feat: 接入搜索接口（补充错误处理）"
git push --force-with-lease

# 6. 一阶段干完了，先暂存切去修 bug
git stash push -m "搜索功能做到一半"
git switch -c hotfix/empty-list
# 修完再切回去
git switch feature/search
git stash pop
```

## 小结 {#summary}

本章覆盖了安装、全局配置、初始化/克隆、核心的 add/commit/status/log 工作流，以及 `.gitignore` 的使用。下一章将学习分支的创建、切换、合并与变基，这是 Git 协作的核心能力。
