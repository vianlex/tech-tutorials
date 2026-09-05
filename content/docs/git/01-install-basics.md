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

## 小结 {#summary}

本章覆盖了安装、全局配置、初始化/克隆、核心的 add/commit/status/log 工作流，以及 `.gitignore` 的使用。下一章将学习分支的创建、切换、合并与变基，这是 Git 协作的核心能力。
