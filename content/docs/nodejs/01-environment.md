---
title: 第一章 环境搭建与基础
linkTitle: 环境搭建
description: Node.js 安装、第一个程序、REPL、全局对象与 process
weight: 51
---

# 环境搭建与基础

## 安装 Node.js {#install}

推荐使用 **nvm**（Node 版本管理器）安装，方便切换多版本：

```bash
# macOS / Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# 安装并切换到最新的 LTS（长期支持版）
nvm install --lts
nvm use --lts

# Windows 用户使用 nvm-windows
nvm install 20.11.0
nvm use 20.11.0
```

验证安装：

```bash
node -v   # 例如 v20.11.0
npm -v    # 例如 10.2.4
```

> [!TIP]
> 生产环境应固定使用 LTS 版本（如 Node 20+），以获得长期安全维护。

## 第一个程序 {#hello-world}

新建 `hello.js`：

```js
// hello.js
console.log("Hello, Node.js!");
```

运行：

```bash
node hello.js
# 输出：Hello, Node.js!
```

也可以直接执行内联脚本：

```bash
node -e "console.log(1 + 2)"
# 输出：3
```

## REPL 交互环境 {#repl}

输入 `node` 进入交互式命令行，适合快速试验：

```bash
$ node
> 1 + 2
3
> const name = "Node"
undefined
> console.log(`Hi, ${name}`)
Hi, Node
> .exit
```

常用命令：`Ctrl+C` 退出当前输入，`Ctrl+D` 或 `.exit` 退出 REPL，`.help` 查看帮助。

## 全局对象与 process {#globals}

Node.js 提供若干全局对象，无需 `require` 即可使用：

```js
// __dirname / __filename：当前文件所在目录与路径
console.log(__dirname);  // /Users/you/project
console.log(__filename); // /Users/you/project/hello.js

// process：当前 Node 进程的信息与控制
console.log(process.version);   // Node 版本
console.log(process.platform);  // 运行平台：win32 / linux / darwin
console.log(process.argv);      // 命令行参数数组

// 读取环境变量
const port = process.env.PORT || 3000;
console.log("端口：", port);

// 优雅退出进程
process.exitCode = 0;
```

`global` 对象等价于浏览器里的 `window`，是全局作用域的顶层对象。

```js
global.greeting = "你好";
console.log(greeting); // 你好（不推荐污染 global）
```

## 小结 {#summary}

通过 nvm 安装 Node.js LTS 版本，用 `node` 运行脚本或进入 REPL 调试，并理解 `__dirname`、`process` 等全局对象。下一章学习模块系统与 npm 依赖管理。
