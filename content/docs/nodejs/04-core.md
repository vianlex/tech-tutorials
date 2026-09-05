---
title: 第四章 核心模块实战
linkTitle: 核心模块
description: fs、path、http、stream、events 核心模块实战
weight: 54
---

# 核心模块实战

## fs 文件系统 {#fs}

`fs` 模块提供文件读写，推荐 `promises` 版本的异步 API：

```js
import { readFile, writeFile } from "node:fs/promises";

// 异步读取
const data = await readFile("input.txt", "utf8");
console.log(data);

// 异步写入（覆盖）
await writeFile("output.txt", "Hello Node.js");

// 追加内容
await writeFile("output.txt", "\n第二行", { flag: "a" });

// 检查文件是否存在
import { existsSync } from "node:fs";
console.log(existsSync("output.txt")); // true
```

## path 路径处理 {#path}

`path` 模块跨平台处理路径，避免手动拼接分隔符：

```js
import path from "node:path";

const full = path.join(__dirname, "data", "config.json");
console.log(full);

console.log(path.basename(full));   // config.json
console.log(path.dirname(full));    // .../data
console.log(path.extname(full));     // .json

// 解析为绝对路径
console.log(path.resolve("logs", "app.log"));

// 提取目录与文件名（无扩展名）
console.log(path.parse(full).name);  // config
```

> [!IMPORTANT]
> 永远用 `path.join` / `path.resolve` 拼路径，不要用字符串 `+ "/"` 拼接，否则在 Windows 上会出错。

## http 创建服务 {#http}

用内置 `http` 模块即可创建 Web 服务，无需任何框架：

```js
import http from "node:http";

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ message: "Hello from Node.js" }));
});

server.listen(3000, () => {
  console.log("服务已启动：http://localhost:3000");
});
```

根据路由返回不同内容：

```js
const server = http.createServer((req, res) => {
  if (req.url === "/") {
    res.end("首页");
  } else if (req.url === "/api") {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ ok: true }));
  } else {
    res.statusCode = 404;
    res.end("Not Found");
  }
});
```

## stream 流 {#stream}

`stream` 适合处理大文件，边读边写，避免一次性占用内存：

```js
import { createReadStream, createWriteStream } from "node:fs";
import { pipeline } from "node:stream/promises";

// 管道：把读流接到写流
await pipeline(
  createReadStream("big.txt"),
  createWriteStream("copy.txt")
);
console.log("复制完成");
```

可读流逐块处理：

```js
const rs = createReadStream("big.txt", { encoding: "utf8" });
rs.on("data", (chunk) => console.log("收到块：", chunk.length));
rs.on("end", () => console.log("读取完成"));
```

## events 事件模块 {#events}

`EventEmitter` 是 Node.js 事件驱动的基础，许多核心模块都继承它：

```js
import { EventEmitter } from "node:events";

class Chat extends EventEmitter {}

const chat = new Chat();

// 监听事件
chat.on("message", (text) => {
  console.log("收到消息：", text);
});

// 触发事件
chat.emit("message", "你好呀");

// 只监听一次
chat.once("join", (user) => console.log(user, "加入了"));
chat.emit("join", "Alice"); // 触发
chat.emit("join", "Bob");   // 不再触发
```

> [!TIP]
> 自定义类继承 `EventEmitter` 可快速实现发布/订阅模式，解耦模块之间的通信。

## 小结 {#summary}

fs/path/http/stream/events 是 Node.js 最核心的内置能力，覆盖文件、路径、网络、流式处理与事件驱动。下一章用 Express 进行 Web 开发实战。
