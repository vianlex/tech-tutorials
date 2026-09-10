---
title: 第五章 进阶与最佳实践
linkTitle: 进阶与最佳实践
description: PTC 模式、Python SDK、自定义 preset、headless 批处理与实践建议
weight: 135
---

# 进阶与最佳实践

## PTC 模式（Programmatic Tool Calling） {#ptc}

PTC（内部键名 `code`）在标准模式基础上，把工具集打包成一个 TypeScript SDK，让模型**写一段 TypeScript 程序**，在 `run_code` 一次调用里组合多轮工具调用，中间数据留在 worker 线程，只把摘要返回模型上下文。

```text
传统模式   每调一个工具 = 一次往返（5 步 = 5 次）
PTC 模式   模型写一段代码，1 次调用完成多步（社区报告多步任务省约 20x token）
```

适合多步骤、重复操作多的任务（数据库迁移、大型项目多文件修改）。代价是模型的第一个产出变成一段「可读、可审计的程序」。逻辑不清晰时生成的代码容易出错，先用标准模式理清再切 PTC 更稳。

```bash
# 会话内切换：输入框左侧模式选择器 → 选 PTC / Code
# 新建会话生效
```

## Python SDK {#python-sdk}

把 dsh 的 Agent 能力嵌入 Python 脚本，无需 Web 页面交互，适合 CI / 批处理自动化。

```bash
# 克隆仓库并准备虚拟环境
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 安装 SDK（wheel 内含 Node-runtime，无需另装 Node）
pip install deepseek-harness-sdk

# 模型密钥（SDK 会继承 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL）
export DEEPSEEK_API_KEY="你的密钥"
```

最小化调用示例（可直接嵌业务脚本）：

```python
from deepseek_harness import DeepSeekHarness

def run_agent_task():
    with DeepSeekHarness(
        provider="deepseek-official",
        model="deepseek-v4-flash",
        cwd="/tmp/demo_workspace",          # 工作区
        session_root="/tmp/dsh_session_log" # 会话存储
    ) as agent:
        result = agent.run("读取当前目录代码文件，统计 py 文件行数")
        print("Agent 输出结果:")
        print(result.get("final_response"))
        print(f"缓存命中率: {result.get('usage', {}).get('cache_hit_rate', 0):.1%}")

if __name__ == "__main__":
    run_agent_task()
```

跑仓库自带的示例脚本：

```bash
python python/sdk/examples/minimal.py \
  --workspace /你的独立工作区绝对路径 \
  --dsh-home /会话存储目录绝对路径 \
  --session-id demo-001 \
  "扫描目录结构，梳理项目文件清单"
```

> 重要：Python SDK **不读** `~/.dsh`，必须显式传 `dsh_home` / `session_root`。当前 SDK 为 Python 3.10+，支持 Linux x64/arm64 与 macOS 14+ arm64，暂无原生 Windows wheel——Windows 上建议走 npm 路线。

## 自定义 agent preset {#preset}

preset = 一个会话里 agent 运行的插件组装（工具、提示词、能力）。两种做法：

1. 复制一份内置预设改成自己的；
2. 用**创造模式（cordis）**让 Agent 帮你创建。

```text
创造模式 = 标准模式 + 运行时检查 + 内存插件实验 + preset 创作引导
（等同 shell 权限，可改活着的运行时，只建议开发插件/新预设时使用）
```

创建并保存后，自定义 preset 落到：

```text
$DSH_HOME/.agent-presets/        # 下次启动时可直接加载
```

全局默认模式也可在 `settings.yaml` 锁定：

```yaml
agent-presets:
  default: standard   # standard / code / minimal / cordis
```

## headless 无头 / 批处理 {#headless}

`headless` profile 做一次性 runner，适合写进脚本自动化：

```bash
# 单条任务，打印最终答案并以退出码 0 结束（不受 Web UI 假死影响）
dsh --profile headless "fix the failing test in this repo"

# 用环境变量预注入 key 的脚本写法
export DEEPSEEK_API_KEY="sk-xxx"
dsh --profile headless "读取目录文件，统计所有 py 文件行数"
```

> `dsh` 启动器只解析自己的 flag（`--profile`、`--patch` 等），其后的内容会交给被启动的 profile——这是常见的首次踩坑点。

## 实践建议 {#tips}

```text
1. Git 护体        工作区务必用 Git 管理，Agent 可能改/删文件，Git 是最好的保险
2. 小任务起步      先发一句简单任务，确认 key / workspace / 沙箱都正常再上真实工作
3. 模式选型        日常用标准；多步批量用 PTC；基准测试用极简；开发插件用创造
4. 凭据备份        ~/.dsh/.credentials.yaml 值得备份，重输 key 是社区最高频的 setup 抱怨
5. 端口暴露        Web UI 默认只监听 127.0.0.1，且官方禁止 --host 0.0.0.0（防 RCE 外泄）
6. 排查装配        dsh --profile web --dump-config 看清真实插件树，比猜更快
7. 隔离持久化      二次开发用 export DSH_HOME=... 隔离，避免污染默认的 ~/.dsh
```

## 小结 {#summary}

本章覆盖了 PTC 代码编排、Python SDK 程序化调用、自定义 agent preset、headless 批处理，以及一组实践建议。至此你已走通「装 → 配 → 跑 → 写插件 → 加载 → 批处理」的完整闭环，可以开始用 dsh 组装属于自己的 Agent 了。
