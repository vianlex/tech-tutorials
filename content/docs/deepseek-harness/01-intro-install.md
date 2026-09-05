---
title: 第一章 简介与安装
linkTitle: 简介与安装
description: DeepSeek Harness 简介、三种安装方式
weight: 131
---

# 简介与安装

## 它是什么 {#what}

DeepSeek Harness（简称 **dsh**）是 DeepSeek 开源的 Agent 框架，仓库 `deepseek-ai/deepseek-harness`，npm 包 `@deepseek-ai/dsh`。

核心公式只有一句话：**Agent = Model + Harness**。

```text
Model     可替换的部件（DeepSeek / OpenAI 兼容模型等）
Harness   模型之外的一切：工具注册、任务规划、沙箱、会话存储、agent 循环
```

它构建在 [Cordis](https://github.com/cordiverse/cordis) 元框架之上，slogan 是「一切皆插件」（Everything is a Plugin）——模型适配器、工具集、沙箱、会话存储、agent 循环本身，全都是可以热插拔的插件。想给某个 session 换一套能力，就「挂一个插件」，而不是 fork 源码改核心。

## 与成品编码工具的区别 {#difference}

| 维度 | 成品编码工具（如 Claude Code） | DeepSeek Harness |
| --- | --- | --- |
| 定位 | 开箱即用的编码助手 | 可拼装的 Agent 运行时 |
| 扩展方式 | 有限插件/钩子 | 一切皆插件，plugin/profile/bundle/patch |
| 模型 | 通常绑定一家 | provider-agnostic，任意 OpenAI 兼容模型 |
| 适用 | 直接用 | 需要定制能力、做二次开发 |

简单说：编码工具是「装好就能用」的产品，Harness 是「把能力拆成一个个插件让你自己组装」的框架。

## 环境要求 {#requirements}

```text
Node.js   ^22.19.0 || >=24.0.0   （官方 engines 声明；推荐 v24 LTS）
pnpm      源码构建 / 插件开发需要（官方 packageManager 为 pnpm 11）
Git       源码安装需要
API Key   DeepSeek 开放平台申请（同时覆盖模型调用与内置联网搜索）
```

验证 Node 版本：

```bash
node --version   # 应显示 v22.19+ 或 v24+
```

> 受限环境（无 root / 沙箱）下 `npm install` 可能明显变慢，因为「一切皆插件」是真按包拆分，依赖树较大，这是正常现象。

## 方式一：npx 快速体验 {#npx}

无需全局安装，一条命令直接运行：

```bash
# 默认在 http://127.0.0.1:3080 启动 Web UI，本机还会自动打开浏览器
npx @deepseek-ai/dsh web

# 不自动打开浏览器（SSH 远程启动常用）
npx @deepseek-ai/dsh web --no-open

# 指定端口（默认 3080 被占用时）
npx @deepseek-ai/dsh web --port 8080
```

## 方式二：npm 全局安装 {#npm-global}

适合频繁使用 `dsh` 命令：

```bash
# 全局安装
npm install -g @deepseek-ai/dsh

# 验证安装
dsh --version

# 启动 Web UI
dsh web
```

## 方式三：源码安装（插件 / 二次开发） {#source}

想读源码、改框架、写插件时用：

```bash
# 1) 克隆仓库
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness

# 2) 启用 corepack 并安装依赖（务必用 pnpm）
corepack enable
pnpm install

# 3) 构建（不要省略，否则 Web 页面缺少产物）
pnpm run build

# 4) 启动
pnpm dsh web
```

> `pnpm run build` 负责准备构建产物，`pnpm dsh web` 直接使用这些产物，不会再重新构建。构建产物位于 `apps/web/dist/`（Web 前端）与 `apps/cli/dist/`（CLI）。

## 验证启动 {#verify}

无论哪种方式，终端出现下面这行即代表启动成功：

```text
dsh web: http://127.0.0.1:3080
```

浏览器打开该地址即可进入 Web UI。注意：**Web UI 默认只监听 `127.0.0.1`**，不暴露到局域网——这是有意的安全默认。

```bash
# 查看当前版本与已加载的插件装配（排查用）
dsh --version
dsh --profile web --dump-config
```

## 小结 {#summary}

本章介绍了 dsh 的核心公式与「一切皆插件」理念，对比了它与成品编码工具的差异，并给出 npx、npm 全局、源码三种安装路径。下一章带你启动 Web UI、配置 API Key、选择 workspace 并发出第一个任务，同时认识四种运行模式。
