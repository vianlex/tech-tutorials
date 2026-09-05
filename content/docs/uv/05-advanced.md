---
title: 第五章 进阶与常见问题
linkTitle: 进阶与常见问题
description: workspace 多包工作区、锁文件与可复现构建、uv build/publish 构建发布、常见命令速查与高频排坑
weight: 165
---

# 进阶与常见问题

前四章覆盖了 uv 的日常用法，本章进入进阶主题：多包工作区、可复现构建、打包发布，以及那些「一踩就懵」的坑。

## workspace 多包工作区 {#workspace}

大型项目往往拆成多个包（库 + 应用 + 工具），uv 的 workspace 让你在一个仓库里统一管理它们。

```toml
# 根 pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]      # 成员包的位置

# 或显式列出
# members = ["lib", "app"]
```

目录结构：

```text
monorepo/
├── pyproject.toml           # workspace 根
├── uv.lock                  # 单一锁文件，统一管理所有成员
└── packages/
    ├── lib/                 # 公共库
    │   └── pyproject.toml
    └── app/                 # 应用
        └── pyproject.toml
```

成员包之间可互相依赖（`uv add "lib"`），uv 会自动解析为本地路径依赖。整个 workspace 共享一份 `uv.lock`，保证版本一致。

> [!NOTE]
> workspace 的收益：**单一锁文件**避免各子包版本漂移，**本地包互相依赖**无需先发布到 PyPI，**一次命令构建全部**。适合 monorepo 组织方式。

## 锁文件与可复现构建 {#reproducible}

`uv.lock` 是 uv 保证「可复现」的核心。它记录了：

- 每个依赖的**精确版本**与**内容哈希**
- **跨平台**的解析结果（Windows/macOS/Linux 各自的 wheel）

最佳实践：

```bash
# 开发：解析并锁定
uv lock

# CI / 部署：严格按锁文件同步，不重新解析
uv sync --frozen
uv lock --check     # 若 lock 与 pyproject 不一致则报错，用于 CI 门禁
```

> [!TIP]
> `--frozen` 和 `--locked` 的区别：`--frozen` 完全不解析、直接用锁文件；`--locked` 允许解析但要求结果与锁文件一致（不一致就报错）。CI 建议用 `--locked` 或 `--frozen` 防止依赖漂移。

## 构建与发布 {#build-publish}

```bash
uv build                # 构建 sdist + wheel 到 dist/
uv build --wheel        # 只构建 wheel
uv publish              # 发布到 PyPI（需配置 token）
```

发布前需配置凭证（`UV_PUBLISH_TOKEN` 环境变量或 `uv publish --token`）。发布到私有源用 `--publish-url`。

```bash
# 发布到私有 PyPI 源
uv publish --publish-url https://pypi.example.com/simple/
```

## 配置 uv 行为 {#config}

uv 的配置写在 `pyproject.toml` 的 `[tool.uv]`，或环境变量 `UV_*`，或 `uv.toml`：

```toml
[tool.uv]
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"   # 换国内镜像加速
```

```bash
# 常见环境变量
UV_INDEX_URL=...          # 指定包索引（镜像）
UV_HTTP_TIMEOUT=...       # 网络超时
UV_NO_CACHE=1             # 禁用缓存
```

> [!TIP]
> 国内使用若下载慢，可配置清华/阿里镜像：`[tool.uv] index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"`，或设置环境变量 `UV_INDEX_URL`。

## 常用命令速查 {#cheatsheet}

```bash
# Python 与虚拟环境
uv python install 3.12      # 安装 Python
uv venv --python 3.12       # 创建虚拟环境
uv run <cmd>                # 免激活运行

# 项目管理
uv init my-app              # 创建项目（0.12 默认 src 布局）
uv init --no-package app    # 创建扁平脚本项目
uv add requests             # 添加依赖
uv add --dev pytest         # 添加开发依赖
uv remove requests          # 删除依赖
uv sync                     # 同步环境
uv lock                     # 锁定依赖

# 工具
uv tool install ruff        # 安装全局工具
uvx ruff check .            # 临时运行工具

# 构建发布
uv build                    # 构建包
uv publish                  # 发布

# 维护
uv cache clean              # 清理缓存
uv self update              # 更新 uv 自身
```

## 高频排坑 {#pitfalls}

### 1. uv add 后依赖没生效

`uv add` 已自动同步，但若手动改了 `pyproject.toml`，需跑 `uv sync` 让环境与声明一致。

### 2. 报错「找不到 Python」

项目 `requires-python` 要求的版本本机没有，且 uv 因网络/策略无法自动下载。解决：`uv python install 3.12` 手动装，或放宽 `requires-python` 约束。

### 3. uv run 用了错误的 Python

检查项目 `.venv` 是否存在、`requires-python` 是否匹配。可用 `uv run python -V` 确认实际版本。

### 4. 团队环境不一致

锁文件没提交或没同步。确保 `uv.lock` 进版本库，协作时 `git pull` 后 `uv sync --locked`。

### 5. 0.12 升级后 `uv init` 结构变了

这是**预期行为**（默认变为可发布包）。想要旧的扁平布局用 `uv init --no-package`。老项目不受影响，无需改动。

### 6. 换镜像后仍慢

镜像只影响下载，解析仍访问源索引。确认 `index-url` 配置正确，并清理缓存重试：`uv cache clean`。

> [!WARNING]
> 若项目里同时存在 `requirements.txt` 和 `pyproject.toml`，`uv pip` 和 `uv add` 会各管各的，容易造成「两套依赖真相」。迁移完成后建议删掉 `requirements.txt`，统一用 `pyproject.toml` + `uv.lock`。

## 小结 {#summary}

本章覆盖了 uv 的进阶能力：workspace 多包工作区、锁文件与可复现构建（`--frozen`/`--locked`）、构建发布、配置镜像，以及高频排坑。至此 Uv 教程五章结束，从安装、Python/环境管理、依赖、项目到进阶，足以把 uv 作为日常主力工具，让 Python 开发告别繁琐的工具链拼接。
