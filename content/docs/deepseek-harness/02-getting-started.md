---
title: 第二章 快速上手
linkTitle: 快速上手
description: 启动 Web UI、配置模型、选择 workspace、第一个会话与四种模式
weight: 132
---

# 快速上手

## 启动 Web UI {#start-web}

先进入你打算让 Agent 操作的项目目录，再启动——Harness 会把启动命令所在目录当作默认文件系统位置：

```bash
# 建议在一个专门的空项目目录里启动，避免它「看到」整个家目录
mkdir -p dsh-demo && cd dsh-demo

# 启动
npx @deepseek-ai/dsh web
```

终端出现下面这行、浏览器自动打开即为成功（SSH 远程不会自动打开，只需手动复制地址）：

```text
dsh web: opening the default browser; pass --no-open to disable
dsh web: http://127.0.0.1:3080
```

## 两步初始配置 {#two-steps}

启动后，要让 Agent「活过来」需要两步基础配置。

### 1. 配置模型 API Key {#api-key}

进入 **Settings → Models**，找到 DeepSeek 卡片，把 API Key 粘贴进「API 密钥」输入框并保存。

```text
设置 → 模型 → DeepSeek
  在「API 密钥」输入框粘贴你的 Key → 保存
```

- 保存后**立即生效，无需重启**；页面是 write-only 设计，只显示脱敏描述符，不回显明文。
- 凭据写入 `$DSH_HOME/.credentials.yaml`（默认即 `~/.dsh/.credentials.yaml`）。
- 也可在启动前用环境变量预注入：

```bash
# Linux / macOS
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"   # 可选，自定义网关时设置

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"
```

```yaml
# 等价写法：直接编辑 ~/.dsh/.credentials.yaml
DEEPSEEK_API_KEY: sk-xxxxxxxxxxxxxxxx
```

> 其他厂商（Anthropic、OpenAI 等）点 **+ 添加提供方**；公司网关/自建服务用 **+ 添加自定义提供方**（填 Provider ID、API 地址、协议、Key 四项）。

### 2. 选择 workspace {#workspace}

点击 **Choose workspace**，加入并选中你启动 `dsh` 的那个项目目录。

```text
Choose workspace → 选择 / 添加本地项目目录
```

Agent 的所有文件操作都会被限制在该目录内部（workspace 是安全边界）。**未选 workspace 之前，会话输入框是灰的不可用**——这是设计如此。

## 第一个会话 {#first-session}

新建一个 session，发一句简单任务：

```text
Summarize this repository and identify its main packages.
```

此时 Agent 就能读/改 workspace 文件、跑命令、委派子任务，并在需要审批的操作前询问你。建议先从小任务开始，确认 key、workspace 边界与沙箱都正常，再交给它真实工作。

> 安全行为：Agent 想把文件写到工作区外会被 workspace-write 沙箱拦截，并自动降级为写入工作区内。

## 四种运行模式 {#modes}

每个会话挂载一个 Agent 预设（preset），决定它有哪些工具与人格。切换入口在会话输入框左侧的模式选择器；**同一会话选定模式后中途不能切换，新建会话才生效**。

| 模式（界面名） | 内部键名 | 特点 | 适用 |
| --- | --- | --- | --- |
| 标准 Standard | `standard` | 完整工具集：文件编辑、Shell、文件/网页检索、Skills、计划、子 Agent、工作流 | 日常编码、项目分析（默认推荐） |
| PTC / Code | `code` | 标准 + Code Mode SDK，模型写一段 TypeScript 一次组合多步调用 | 多步批量、复杂自动化 |
| 极简 Minimal | `minimal` | 仅持久 bash + `str_replace_editor` 两个工具 | 基准测试、最小干预 |
| 创造 Creation | `cordis` | 标准 + 运行时检查、内存插件实验、preset 创作引导 | 开发插件 / 自定义 Agent |

```text
标准模式    功能最全，新手默认选择
PTC 模式    一次代码调用完成多步，省来回往返（社区报告多步任务可省约 20x token）
极简模式    只留两个工具，行为最可控，DeepSeek 官方 V4 评测即在此模式
创造模式    等同 shell 权限，可改活着的运行时，只建议开发插件时使用，勿处理重要业务
```

修改全局默认模式（`settings.yaml`）：

```yaml
agent-presets:
  default: standard   # 可选 standard / code / minimal / cordis
```

## 小结 {#summary}

本章走通了「启动 → 配 Key → 选 workspace → 发任务」的首次运行闭环，并认识了标准/PTC/极简/创造四种预设模式。下一章深入 Harness 的装配机制：plugin、profile、bundle、patch 与配置层叠顺序。
