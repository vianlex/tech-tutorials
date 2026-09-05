---
title: 第三章 核心概念
linkTitle: 核心概念
description: plugin/profile/bundle/patch、配置层叠顺序与 DSH_HOME
weight: 133
---

# 核心概念

## 一台 dsh 是一个插件树 {#plugin-tree}

跑起来的 dsh 本质上是一棵「插件树」。后面反复会碰到四个名词：

| 概念 | 是什么 |
| --- | --- |
| **plugin** 插件 | 一个 TypeScript 模块，导出一个 `apply(ctx)`（或对象/类），向运行时注册能力 |
| **profile** 具名组合 | 躺在 Harness home 里的「配方」，列出堆叠哪些 bundle、装哪些 out-of-tree 插件、以及你自己的 `cordis.patch.yml` |
| **bundle** 分发包 | 一组 Cordis 配置行 + 挂载的代码，是可分发的包（如 `@deepseek-ai/dsh-base`） |
| **patch** 补丁 | 一个「按 id 改一行或插一行」的 YAML 文件（`cordis.patch.yml`） |

## profile：内置模板 {#profile}

内置 profile 有五个：`web`、`headless`、`sdk`、`sdk-minimal`、`acp`。

```bash
# 用某个 profile 启动
dsh --profile headless "Reply with exactly the single word: ok"
dsh --profile web --dump-config
```

- `web`：带浏览器应用的完整交互界面。
- `headless`：无 server 的一次性 runner，适合脚本自动化。
- `sdk` / `sdk-minimal`：供 SDK 程序化调用。
- `acp`：Agent Client Protocol 接入。

## bundle：分发的插件包 {#bundle}

bundle 是「分发包」格式——一组 Cordis 配置 + 它们挂载的代码。常见几个：

```text
@deepseek-ai/dsh-base        模型接入、完整工具集、持久化会话、沙箱与权限策略
@deepseek-ai/dsh-web-app     在 base 之上追加浏览器应用
@deepseek-ai/dsh-headless    追加无 server 的一次性 runner
```

## patch：按 id 改/插一行 {#patch}

patch 用 YAML 按 `id` 修改或插入配置行。插件路径必须是**绝对路径**；对同一条配置，**后应用的层优先**，且 patch 替换的是目标行的整个 `config`，不是深度合并。

```yaml
# cordis.patch.yml 示例：往插件树里插入一个本地插件
- insert:
  - id: greet-tool
    name: '/absolute/path/to/scratch-plugin/src/greet-tool.ts'
```

## 配置层叠顺序 {#layering}

一台 dsh 启动时按固定顺序组装，越靠后的层优先级越高：

```text
profile 中的每个 bundle（按声明顺序）
  → profile 自己的 cordis.patch.yml
    → home 级 $DSH_HOME/cordis.patch.yml
      → 命令行 --patch 覆盖层
```

## 查看实际装配：--dump-config {#dump-config}

```bash
# 打印你机器上实际装配出来的插件树（含所有 patch 应用后）
dsh --profile web --dump-config

# 打印默认树（不启动、不套用任何 patch）
dsh --profile web --dump-default-config
```

每一行都是「`id` + 包名 + `config`」——这就是「一切皆插件」最直观的现场：模型、工具、会话、agent 循环全是一排可 patch 的插件行。排查「插件没加载 / 配置没生效」时首选这条命令。

```bash
# 只看某个插件是否就位
dsh --profile web --dump-config | grep greet-tool
```

## DSH_HOME 与配置文件位置 {#dsh-home}

dsh 把 profile、凭据、session、storage 等持久化内容放在 **Harness home**，默认 `~/.dsh`，可被环境变量 `DSH_HOME` 显式覆盖。

```text
$DSH_HOME/                      Harness home（默认 ~/.dsh）
  .credentials.yaml            凭据（API Key 等），页面只显示脱敏描述符
  settings.yaml                配置（如默认 preset、通用设置）
  cordis.patch.yml             home 级 patch（全 profile 生效）
  .agent-presets/              自定义 agent preset（创造模式保存于此）
  profiles/<name>/             各 profile 自己的补丁与配置
  sessions/                    会话与 append-only 轨迹日志
```

```bash
# 改变持久化目录（加载插件、凭据解析都会读这个新位置）
export DSH_HOME="$HOME/.dsh-dev"
dsh --profile web --dump-config
```

> 凭据解析优先级：**环境变量 → `.credentials.yaml` → `.env` 文件**。`.credentials.yaml` 含明文密钥，切勿提交到 Git。

## 小结 {#summary}

本章厘清了 plugin/profile/bundle/patch 四件套与「配置越靠后优先级越高」的层叠顺序，并学会用 `--dump-config` 看清真实装配、用 `DSH_HOME` 控制持久化位置。下一章进入插件开发：从 `apply(ctx)` 到 `defineTool` 写第一个工具。
