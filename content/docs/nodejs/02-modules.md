---
title: 第二章 模块系统与 npm
linkTitle: 模块与 npm
description: CommonJS/ESM、package.json、常用命令、依赖管理
weight: 52
---

# 模块系统与 npm

## CommonJS 模块 {#commonjs}

Node.js 早期使用 **CommonJS** 规范，通过 `require` 导入、`module.exports` 导出：

```js
// math.js：导出
function add(a, b) {
  return a + b;
}
module.exports = { add };
```

```js
// app.js：导入
const { add } = require("./math");
console.log(add(2, 3)); // 5
```

`module.exports` 与 `exports` 指向同一对象，但给 `exports` 直接赋值会断开引用：

```js
exports.add = add;          // 有效
// exports = { add };       // 失效：覆盖了引用
module.exports = { add };   // 推荐写法
```

## ES Module (ESM) {#esm}

Node.js 现代推荐 **ESM**（浏览器同款语法），需在 `package.json` 设置 `"type": "module"` 或文件用 `.mjs` 后缀：

```js
// math.mjs
export function add(a, b) {
  return a + b;
}

export const PI = 3.14159;
```

```js
// app.mjs
import { add, PI } from "./math.mjs";
console.log(add(2, 3), PI);
```

默认导出与重命名导入：

```js
// 默认导出
export default function greet(name) {
  return `你好, ${name}`;
}

// 导入时可重命名
import greet, { add as plus } from "./math.mjs";
```

> [!IMPORTANT]
> ESM 使用静态导入，顶层不能使用 `require`。CommonJS 与 ESM 混用时，可在 `package.json` 用 `imports` 字段或双扩展名区分。

## package.json {#package-json}

`package.json` 是项目的清单文件，描述元信息与依赖：

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "type": "module",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "node --watch index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  },
  "devDependencies": {
    "eslint": "^8.57.0"
  }
}
```

## npm 常用命令 {#npm-commands}

```bash
npm init -y              # 快速生成 package.json
npm install express      # 安装并写入 dependencies
npm install -D eslint    # 安装开发依赖（devDependencies）
npm install             # 根据 package.json 安装所有依赖
npm uninstall lodash     # 卸载依赖
npm run dev             # 运行自定义脚本
npm update              # 更新依赖到允许的最新版本
```

> [!TIP]
> 推荐开启 `npm ci` 用于 CI 环境，它严格依据 `package-lock.json` 安装，速度更快且结果可复现。

## 依赖管理 {#dependencies}

`package-lock.json` 锁定依赖树，应提交到版本库以保证可复现：

```bash
npm ci          # 删除 node_modules 后按 lock 文件精确安装
npm outdated    # 检查过时的依赖
npm audit       # 检查安全漏洞
npm audit fix   # 自动修复可安全升级的漏洞
```

语义化版本号（SemVer）：`^4.18.2` 允许次版本和补丁更新，`~4.18.2` 仅允许补丁更新，`4.18.2` 锁定精确版本。

## 小结 {#summary}

CommonJS 与 ESM 是两套模块方案，新项目建议用 ESM；`package.json` 与 `package-lock.json` 共同管理依赖。下一章深入异步编程与事件循环。
