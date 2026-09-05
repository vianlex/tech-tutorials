---
title: JavaScript 模块的导入与导出：一文讲透 ESM 与 CommonJS
linkTitle: JS 导入与导出模块
date: 2026-09-05
description: 从导出语法、导入语法到 ESM 与 CommonJS 的本质区别、动态导入与 tree-shaking，系统讲清 JavaScript 模块化的来龙去脉。
authors: [vianlex]
tags: [JavaScript, 模块化, ESM, CommonJS]
---

JavaScript 发展早期，代码只能靠 `<script>` 标签一股脑塞进页面，全局变量满天飞、命名冲突、依赖顺序全靠手动排序。直到模块化方案出现，才真正解决了「代码如何组织与复用」的问题。今天这篇文章，把 JS 的导入导出讲透。

## 为什么需要模块

在模块出现之前，两个 `.js` 文件只能靠全局变量通信：

```html
<script src="a.js"></script>  <!-- a.js 里定义 var name = "Alice" -->
<script src="b.js"></script>  <!-- b.js 里使用 name，靠全局作用域共享 -->
```

问题很明显：变量污染全局、互相覆盖、依赖关系隐晦、无法按需加载。模块化用「导入/导出」划清了边界——**默认所有变量私有，只导出你想暴露的，导入你需要的**。

## 两种模块体系

目前并存两套主流标准：

| | CommonJS | ES Modules (ESM) |
| --- | --- | --- |
| 出现背景 | Node.js 早期默认方案 | ES6 正式规范，现代标准 |
| 导出语法 | `module.exports` / `exports.x` | `export` / `export default` |
| 导入语法 | `require()` | `import` |
| 加载时机 | 运行时同步加载 | 编译时确定依赖（静态） |
| 作用 | 主要服务端 Node | 浏览器原生 + Node 现代版本 |

一句话：**CommonJS 是 Node 的历史默认，ESM 是当前和未来的标准**。新项目优先用 ESM。

## ESM 导出

### 命名导出（named export）

导出多个具名成员，可以在声明处直接加 `export`：

```javascript
// math.js
export const PI = 3.14159;
export function add(a, b) { return a + b; }
export class Circle { /* ... */ }
```

也可以先声明、最后统一导出：

```javascript
// math.js
const PI = 3.14159;
function add(a, b) { return a + b; }

export { PI, add };          // 统一导出
export { add as plus };      // 导出时重命名
```

### 默认导出（default export）

每个模块只能有一个默认导出，导入时可以任意命名：

```javascript
// user.js
export default function getUser() { return { name: "Alice" }; }

// 或先声明再默认导出
function getUser() { return { name: "Alice" }; }
export default getUser;
```

命名导出与默认导出可以同时存在：

```javascript
// utils.js
export default function main() { /* ... */ }
export const version = "1.0.0";
```

## ESM 导入

### 导入命名成员

```javascript
import { PI, add } from "./math.js";
import { add as plus } from "./math.js";   // 导入时重命名
```

### 导入默认成员

```javascript
import getUser from "./user.js";   // 名字随便起，对应 default
```

### 混合导入

```javascript
import main, { version } from "./utils.js";
```

### 整体导入（namespace import）

```javascript
import * as math from "./math.js";
math.PI;
math.add(1, 2);
```

### 副作用导入

只执行模块、不导入任何成员（比如注册全局 polyfill）：

```javascript
import "./polyfill.js";
```

## CommonJS 导出与导入

Node.js 的 `require` / `module.exports` 至今在大量项目中存在：

```javascript
// math.cjs
const PI = 3.14159;
function add(a, b) { return a + b; }

module.exports = { PI, add };   // 导出对象
// 或逐个挂到 exports 上：exports.PI = PI;
```

```javascript
// 导入
const math = require("./math.cjs");
math.PI;
math.add(1, 2);

// 解构导入
const { add } = require("./math.cjs");
```

关键点：`module.exports` 和 `exports` 指向同一个对象，但**直接给 `exports` 赋值会失效**，必须改 `module.exports` 或往 `exports` 上挂属性。

## 动态导入 import()

静态 `import` 必须在模块顶层，无法在条件或函数里按需加载。`import()` 返回 Promise，解决按需加载：

```javascript
// 条件加载
if (needChart) {
  const { default: Chart } = await import("./chart.js");
  Chart.render();
}

// 懒加载一个模块
button.onclick = async () => {
  const module = await import("./dialog.js");
  module.open();
};
```

`import()` 也常用于代码分割（code splitting），配合打包器把大模块拆成独立 chunk 按需下载。

## ESM 与 CommonJS 的本质区别

理解两者差异，才能避开很多坑：

**1. 静态 vs 动态**

ESM 的 `import` 是**静态结构**，编译器在运行前就能确定依赖关系，这让打包器能做 tree-shaking（摇树，删除未用代码）。CommonJS 的 `require` 是普通函数调用，可在任意位置、甚至动态拼接路径，无法静态分析。

**2. 值引用 vs 值拷贝**

这是最容易踩的坑。ESM 导入的是**值的引用（live binding）**，导出方变量变了，导入方读到的是新值；CommonJS 导入的是**值的拷贝**：

```javascript
// counter.js (ESM)
export let count = 0;
export function inc() { count++; }
```

```javascript
import { count, inc } from "./counter.js";
console.log(count);  // 0
inc();
console.log(count);  // 1 —— 引用绑定，能看到最新值
```

而 CommonJS 中 `require` 拿到的是导出那一刻的快照，后续变化不会同步。

**3. 顶层 this 不同**

ESM 顶层 `this` 是 `undefined`，CommonJS 顶层 `this` 指向 `module.exports`。

**4. 严格模式**

ESM 默认严格模式；CommonJS 默认非严格。

## Node.js 中的模块选择

Node.js 靠文件扩展名和 `package.json` 决定模块类型：

- `.mjs` 文件始终按 ESM 处理
- `.cjs` 文件始终按 CommonJS 处理
- `.js` 文件看最近的 `package.json` 里 `"type"` 字段：`"type": "module"` 则 ESM，缺省则 CommonJS

```json
{
  "name": "my-app",
  "type": "module"
}
```

在 ESM 模块里 `import` CommonJS 模块是可以的（Node 做了兼容），但 `require` 不能在 ESM 里用。

## 一个完整示例

```javascript
// user.js —— 默认导出 + 命名导出
export default class User {
  constructor(name) { this.name = name; }
  greet() { return `Hi, ${this.name}`; }
}

export const VERSION = "1.0.0";
```

```javascript
// main.js —— 混合导入 + 动态导入
import User, { VERSION } from "./user.js";

const alice = new User("Alice");
console.log(alice.greet());   // Hi, Alice
console.log(VERSION);         // 1.0.0

// 按需加载
const { default: Analytics } = await import("./analytics.js");
Analytics.track("page_view");
```

## 小结

- 现代项目优先用 **ESM**，掌握 `export` / `export default` / `import` / `import()` 四套语法。
- **命名导出**对应具名导入，**默认导出**对应任意命名导入，两者可并存。
- 记住 ESM 与 CommonJS 的核心差异：**静态 vs 动态、引用 vs 拷贝、顶层 this、严格模式**。
- Node.js 靠 `.mjs`/`.cjs` 和 `package.json` 的 `type` 字段区分模块体系。

理解模块化，是读懂现代前端工程（打包、tree-shaking、代码分割）的第一块基石。
