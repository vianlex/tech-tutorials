---
title: 第四章 插件开发入门
linkTitle: 插件开发入门
description: apply(ctx)/inject/ctx.effect、三种写法、defineTool 与加载三步闭环
weight: 134
---

# 插件开发入门

## 一个插件 = 一个 TypeScript 模块 {#basic}

最小插件就导出一个 `apply(ctx)` 函数。dsh 加载插件时调用 `apply` 并传入 `ctx`，你通过 `ctx` 注册能力。

```typescript
// scratch-plugin/src/hello.ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello-plugin'

export function apply(ctx: Context) {
  console.log('[hello-plugin] plugin loaded!')
}
```

## 三种写法 {#three-forms}

```typescript
// 1) 函数形式：大多数场景够用
export function apply(ctx: Context) { /* ... */ }

// 2) 对象形式
export default {
  name: 'my-plugin',
  inject: ['tools'],
  apply(ctx: Context) { /* ... */ },
}

// 3) 类形式：当你要提供一个 service 给其他插件消费时
import { Service, type Context } from '@deepseek-ai/cordis'
export default class MyService extends Service {
  static inject = ['tools']
  constructor(ctx: Context) {
    super(ctx, 'myService')
  }
}
```

## 声明依赖：inject {#inject}

插件要用某个 service（如 `tools`、`llm`），在 `inject` 里声明。Cordis 会等依赖全部就绪再加载你的插件，所以 `apply` 里不用判空。

```typescript
import type { Context } from '@deepseek-ai/cordis'

export const name = 'my-tool-plugin'
export const inject = ['tools']

export function apply(ctx: Context) {
  // 到这里 ctx.tools 一定已就绪
  ctx.tools.register(/* ... */)
}
```

## 自动清理：ctx.effect {#effect}

凡经 `ctx` 注册的东西（事件监听、工具、定时器），插件卸载时都会自动清理——不用手动 `removeListener` 或 `clearInterval`。需要显式释放资源（如网络连接）时，用 `ctx.effect` 返回 disposer：

```typescript
import type { Context } from '@deepseek-ai/cordis'

export function apply(ctx: Context) {
  ctx.effect(() => {
    const timer = setInterval(() => console.log('heartbeat'), 5000)
    // 插件卸载时执行
    return () => clearInterval(timer)
  })
}
```

## 用 defineTool 写工具 {#define-tool}

工具是「模型能看到的插件」。一个最小工具长这样（从 `@deepseek-ai/dsh-tools` 导入 `defineTool`）：

```typescript
// scratch-plugin/src/greet-tool.ts
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'greet-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'greet',
    description: 'Greet someone by name.',
    parameters: {
      name: { type: 'string', required: true, description: 'The name to greet' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      return `Hello, ${args.name}!`
    },
  }))
}
```

带异步 I/O 的经典例子——注意 `exec.signal` 被直接透传给底层调用：

```typescript
import { readFile } from 'node:fs/promises'
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'read-file-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'read_file',
    description: 'Read a file from disk.',
    parameters: {
      path: { type: 'string', required: true, description: 'Absolute path' },
      limit: { type: 'number' }, // 非必填
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args, exec) {
      return readFile(args.path, { encoding: 'utf8', signal: exec.signal })
    },
  }))
}
```

`parameters` 一个 schema 干三件事：推断 `execute` 里 `args` 的 TS 类型、在 `execute` 运行前校验模型生成的参数、自动注入 system prompt 让模型知道有这个工具。

## execute 的五条契约 {#execute-contract}

写 `execute` 前必读（官方 tool authoring reference 写死）：

```text
1. args 已校验     execute 里拿到的参数一定已按 parameters schema 校验过
2. 返回 canonical JSON   返回一个 JSON 值（不是内容块），别让调用方去散文里解析
3. 仅基础设施故障才 throw   非理想业务结果（如进程非零退出）放进返回值里表达，
                          抛错或返回非法值 = isError
4. 尊重 exec.signal   用它取消进行中的工作（上面 readFile 直接透传）
5. 长任务走 ctx.jobs.start   前台 execute 别跑长任务，改用后台 job
```

UI 卡片与 `output.render` 必须是 `args`（加结果）的纯函数，不能做 I/O。工具注册是 effect 式的：插件卸载，工具自动注销，不留孤儿状态。

## 加载三步闭环 {#load-loop}

光有 `apply(ctx)` 不行，dsh 还得知道插件文件在哪。最小闭环三步：

```bash
# 第一步：落插件文件（绝对路径）
mkdir -p scratch-plugin/src
# 把上面的 greet-tool.ts 存到 scratch-plugin/src/greet-tool.ts

# 第二步：写 cordis.patch.yml（用绝对路径，往插件树插入一行）
cat > cordis.patch.yml << 'EOF'
- insert:
  - id: greet-tool
    name: '/absolute/path/to/scratch-plugin/src/greet-tool.ts'
EOF

# 第三步：启动并验证是否就位
pnpm dsh web
dsh --profile web --dump-config | grep greet-tool
```

也可用 `dsh plugin` 命令管理（实质是写入对应 profile 的 patch）：

```bash
# 安装插件（npm 包 / GitHub 归档 / 本地路径）
dsh plugin --profile web add @dsh-external/dsh-vision-toolkit
dsh plugin --profile web add https://github.com/omdsh-dev/dsh-custom-tool/archive/refs/heads/main.tar.gz
dsh plugin --profile web add file:/path/to/your-plugin

# 更新 / 移除
dsh plugin --profile web update
dsh plugin --profile web remove @dsh-external/dsh-vision-toolkit
```

> 安装/更新/移除插件后需重启 Web 服务（`Ctrl+C` 后重新 `dsh web`），仅刷新浏览器通常不够。

## 小结 {#summary}

本章从 `apply(ctx)` 讲到 `inject` 依赖声明、`ctx.effect` 自动清理，并用 `defineTool` 写了一个可调用工具，最后用「落文件 → 写 patch → 启动验证」三步闭环把它加载进运行时。下一章进阶：PTC 模式、Python SDK、自定义 preset 与 headless 批处理。
