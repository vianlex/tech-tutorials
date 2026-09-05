---
title: 第五章 Web 开发与工程实践
linkTitle: Web 与工程
description: Express 快速上手、中间件、REST API、调试与部署简介
weight: 55
---

# Web 开发与工程实践

## Express 快速上手 {#express}

Express 是最流行的 Node.js Web 框架，先安装：

```bash
npm install express
```

最简服务：

```js
import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.send("Hello Express!");
});

app.listen(3000, () => {
  console.log("服务运行在 http://localhost:3000");
});
```

解析 JSON 请求体需要内置中间件：

```js
app.use(express.json()); // 解析 application/json
app.use(express.urlencoded({ extended: true })); // 解析表单
```

## 中间件 {#middleware}

中间件是「请求-响应」链上的处理函数，可修改请求、响应或结束流程：

```js
// 日志中间件
function logger(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next(); // 必须调用 next 交给下一个中间件
}

app.use(logger);

// 路由级中间件，仅匹配 /admin 前缀
app.use("/admin", (req, res, next) => {
  req.isAdmin = true;
  next();
});
```

错误处理中间件接收四个参数：

```js
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "服务器内部错误" });
});
```

> [!TIP]
> 中间件顺序很重要：先注册通用中间件，再注册路由，最后注册错误处理中间件。

## 构建 REST API {#rest-api}

一个完整的用户 CRUD 示例：

```js
const users = [];
let nextId = 1;

// 新增
app.post("/users", (req, res) => {
  const user = { id: nextId++, ...req.body };
  users.push(user);
  res.status(201).json(user);
});

// 查询列表
app.get("/users", (req, res) => {
  res.json(users);
});

// 查询单个
app.get("/users/:id", (req, res) => {
  const user = users.find((u) => u.id === +req.params.id);
  if (!user) return res.status(404).json({ error: "未找到" });
  res.json(user);
});

// 更新
app.put("/users/:id", (req, res) => {
  const user = users.find((u) => u.id === +req.params.id);
  if (!user) return res.status(404).json({ error: "未找到" });
  Object.assign(user, req.body);
  res.json(user);
});

// 删除
app.delete("/users/:id", (req, res) => {
  const idx = users.findIndex((u) => u.id === +req.params.id);
  if (idx === -1) return res.status(404).json({ error: "未找到" });
  users.splice(idx, 1);
  res.status(204).end();
});
```

## 调试与部署简介 {#deploy}

用内置 inspector 调试：

```bash
node --inspect index.js          # 监听 9229 端口，用 Chrome DevTools 连接
node --inspect-brk index.js      # 在首行断住
```

调试环境变量与生产配置：

```js
const port = process.env.PORT || 3000;
const isProd = process.env.NODE_ENV === "production";
app.listen(port, () => console.log(`监听 ${port}，生产模式：${isProd}`));
```

进程守卫（如 PM2）保证服务常驻：

```bash
npm install -g pm2
pm2 start index.js --name my-app   # 启动
pm2 logs my-app                    # 查看日志
pm2 restart my-app                 # 重启
```

容器化部署示例（片段）：

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
```

> [!IMPORTANT]
> 生产环境应使用 `npm ci` 安装、设置 `NODE_ENV=production`，并通过 PM2 或容器编排工具保证进程存活与零停机重启。

## 小结 {#summary}

Express 中间件与路由让你快速构建 REST API，配合 `--inspect` 调试、PM2 或 Docker 部署即可上线。至此 Node.js 教程完结，建议动手做一个完整项目巩固所学。
