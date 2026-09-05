---
title: 第五章 进阶与最佳实践
linkTitle: 进阶实践
description: tag 版本发布、submodule/subtree、Git Hooks 与常见场景速查
weight: 115
---

# 进阶与最佳实践

掌握基础后，本章介绍版本发布标签、多仓库管理、自动化钩子，以及日常高频场景的速查命令。

## 标签与版本发布 {#tag}

标签用于标记重要节点（如发布版本），推荐带注解标签：

```bash
# 创建轻量标签
git tag v1.0.0

# 创建带注解标签（推荐，含作者与时间）
git tag -a v1.0.0 -m "发布 1.0.0 正式版"

# 对历史某次提交打标签
git tag -a v0.9.0 -m "0.9 预发布" <commit-hash>

# 查看标签
git tag
git tag -l "v1.*"         # 按模式过滤
git show v1.0.0           # 查看标签详情

# 推送标签到远程
git push origin v1.0.0
git push origin --tags    # 推送全部标签

# 删除标签
git tag -d v1.0.0
git push origin --delete v1.0.0
```

语义化版本建议遵循 `MAJOR.MINOR.PATCH`：主版本不兼容变更、次版本新增功能、修订号修复缺陷。

## 子模块 {#submodule}

在一个仓库中引用另一个仓库（如共用第三方库）：

```bash
# 添加子模块
git submodule add https://github.com/user/lib.git vendor/lib

# 克隆含子模块的项目
git clone --recurse-submodules https://github.com/user/repo.git

# 初始化并更新已存在的子模块
git submodule update --init --recursive

# 更新子模块到远程最新
git submodule update --remote vendor/lib

# 查看子模块状态
git submodule status
```

## 子树 {#subtree}

`subtree` 将外部仓库作为目录合并进来，无需 `.gitmodules`，对协作者更友好：

```bash
# 添加外部仓库为 subtree
git subtree add --prefix=libs/util https://github.com/user/util.git main --squash

# 从上游拉取更新
git subtree pull --prefix=libs/util https://github.com/user/util.git main --squash

# 将本地改动推送回上游
git subtree push --prefix=libs/util https://github.com/user/util.git main
```

submodule 与 subtree 的选择：submodule 引用独立仓库、指针灵活但配置复杂；subtree 完全合并进主仓库、操作简单但历史较重。

## Git Hooks {#hooks}

钩子在特定事件（提交、推送等）前后自动执行脚本，位于 `.git/hooks/`：

```bash
# 查看已有钩子样本
ls .git/hooks
# pre-commit.sample  commit-msg.sample ...

# 启用 pre-commit 钩子（提交前运行检查）
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

常用钩子与典型用途：

| 钩子 | 触发时机 | 用途 |
|------|----------|------|
| pre-commit | 提交前 | 运行 lint、格式化检查 |
| commit-msg | 提交信息写好后 | 校验提交信息格式 |
| pre-push | 推送前 | 运行测试套件 |
| post-merge | 合并后 | 自动安装依赖 |

示例 `pre-commit` 钩子（提交前检查代码风格）：

```bash
#!/bin/sh
# .git/hooks/pre-commit
npm run lint
if [ $? -ne 0 ]; then
  echo "lint 未通过，提交已中止"
  exit 1
fi
```

> 钩子默认不随仓库分发；团队共享可借助 `core.hooksPath` 指向仓库内的 `.githooks/` 目录。

## 常见场景速查 {#cheatsheet}

```bash
# 撤销工作区某个文件的改动（回到最近提交状态）
git checkout -- <file>
git restore <file>            # 现代写法

# 取消已暂存的文件
git restore --staged <file>

# 修改最近一次提交信息
git commit --amend -m "新的信息"

# 查看某行代码是谁、何时修改的
git blame <file>

# 丢弃所有未提交改动（危险）
git reset --hard

# 临时切换提交查看旧版本
git checkout <commit-hash>

# 清理未被跟踪的文件（含目录，-x 含忽略文件）
git clean -fd
git clean -fdx                 # 彻底清理

# 简化提交图
git log --oneline --graph --decorate --all
```

## 小结 {#summary}

本教程系统讲解了 Git 的安装配置、分支合并、远程协作、历史管理与撤销，以及标签、子模块、Git Hooks 和场景速查。熟练运用这些命令，即可从容应对个人与团队的日常版本控制工作。
