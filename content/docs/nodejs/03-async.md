---
title: 第三章 异步编程与事件循环
linkTitle: 异步编程
description: 回调、Promise、async/await 与事件循环机制
weight: 53
---

# 异步编程与事件循环

Node.js 采用**单线程 + 事件循环**模型处理高并发 I/O，一切都围绕异步非阻塞展开。

## 回调函数 {#callback}

最基础的异步写法是通过回调函数在任务完成时通知：

```js
const fs = require("fs");

// 异步读取文件，完成后执行回调
fs.readFile("data.txt", "utf8", (err, data) => {
  if (err) {
    console.error("读取失败：", err);
    return;
  }
  console.log(data);
});
```

回调嵌套过多会导致「回调地狱」，难以维护：

```js
// 不推荐：层层嵌套
fs.readFile("a.txt", (err, a) => {
  fs.readFile("b.txt", (err2, b) => {
    fs.readFile("c.txt", (err3, c) => {
      console.log(a, b, c);
    });
  });
});
```

## Promise {#promise}

`Promise` 表示一个异步操作的最终结果，有三种状态：pending / fulfilled / rejected：

```js
function readFilePromise(path) {
  return new Promise((resolve, reject) => {
    fs.readFile(path, "utf8", (err, data) => {
      if (err) reject(err);
      else resolve(data);
    });
  });
}

readFilePromise("data.txt")
  .then((data) => console.log(data))
  .catch((err) => console.error(err));
```

`Promise.all` 并发等待多个任务，`Promise.race` 取最先完成的一个：

```js
Promise.all([
  readFilePromise("a.txt"),
  readFilePromise("b.txt"),
]).then(([a, b]) => console.log(a, b));
```

## async/await {#async-await}

`async/await` 是建立在 Promise 之上的语法糖，让异步代码像同步一样易读：

```js
async function main() {
  try {
    const a = await readFilePromise("a.txt");
    const b = await readFilePromise("b.txt");
    console.log(a, b);
  } catch (err) {
    console.error("出错了：", err);
  }
}

main();
```

并发执行以缩短耗时：

```js
async function main() {
  const [a, b] = await Promise.all([
    readFilePromise("a.txt"),
    readFilePromise("b.txt"),
  ]);
  console.log(a, b);
}
```

## 事件循环机制 {#event-loop}

事件循环按固定阶段顺序处理回调，简化模型如下：

```text
   ┌───────────────────────────┐
┌─>│  timers（setTimeout 等）   │
│  ├───────────────────────────┤
│  │ pending callbacks          │
│  ├───────────────────────────┤
│  │ idle / prepare             │
│  ├───────────────────────────┤
│  │ poll（I/O 回调）            │
│  ├───────────────────────────┤
│  │ check（setImmediate）       │
│  ├───────────────────────────┤
│  │ close callbacks            │
└──┴───────────────────────────┘
```

`process.nextTick` 与 `Promise` 微任务优先于定时器宏任务执行：

```js
console.log("1"); // 同步代码先执行

setTimeout(() => console.log("2"), 0); // 宏任务

Promise.resolve().then(() => console.log("3")); // 微任务

process.nextTick(() => console.log("4")); // 先于微任务

console.log("5");
// 输出顺序：1 5 4 3 2
```

> [!TIP]
> 理解「同步 → nextTick → 微任务 → 宏任务」的执行顺序，是排查异步 bug 的关键。

## 小结 {#summary}

回调、Promise 与 async/await 逐步演进使异步代码更清晰，而事件循环决定了它们的执行时序。下一章用核心模块进行实战。
