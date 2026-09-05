---
title: 第五章 异步编程与 Promise
linkTitle: 异步编程
description: 回调、Promise、async/await 与错误处理
weight: 25
---

# 异步编程与 Promise

## 为什么需要异步 {#why-async}

JavaScript 是**单线程**的。网络请求、文件读取等耗时操作若同步执行会阻塞主线程，因此需要异步。

## 回调函数 {#callback}

```javascript
setTimeout(() => {
    console.log('1 秒后执行');
}, 1000);
```

回调的问题是**回调地狱**（层层嵌套难以维护）：

```javascript
// 反例：回调地狱
fetchUser(id, (user) => {
    fetchOrders(user.id, (orders) => {
        fetchDetails(orders[0].id, (details) => {
            // 越来越深...
        });
    });
});
```

## Promise {#promise}

Promise 代表一个**未来会完成**的异步操作，有三种状态：`pending`、`fulfilled`、`rejected`。

```javascript
const promise = new Promise((resolve, reject) => {
    setTimeout(() => {
        resolve('成功');
        // reject(new Error('失败'));
    }, 1000);
});

promise
    .then((result) => console.log(result))  // 成功
    .catch((err) => console.error(err))     // 失败
    .finally(() => console.log('结束'));    // 无论成败
```

## Promise 链式调用 {#chaining}

```javascript
fetchUser(id)
    .then((user) => fetchOrders(user.id))
    .then((orders) => fetchDetails(orders[0].id))
    .then((details) => console.log(details))
    .catch((err) => console.error('任一环节失败', err));
```

## 常用静态方法 {#static-methods}

```javascript
Promise.all([p1, p2, p3]);        // 全部成功才成功
Promise.allSettled([p1, p2]);     // 等全部结束，返回各自状态
Promise.race([p1, p2]);           // 第一个完成的决定结果
Promise.any([p1, p2]);            // 第一个成功的决定结果
```

## async / await {#async-await}

`async/await` 是 Promise 的语法糖，让异步代码看起来像同步：

```javascript
async function loadUserData(id) {
    try {
        const user = await fetchUser(id);      // 等待 Promise 完成
        const orders = await fetchOrders(user.id);
        const details = await fetchDetails(orders[0].id);
        return details;
    } catch (err) {
        console.error('加载失败', err);
        throw err;
    }
}
```

> [!TIP]
> `async` 函数总是返回 Promise；`await` 只能在 `async` 函数内使用。

## 小结 {#summary}

从回调到 Promise 再到 async/await，是现代 JavaScript 处理异步的主流演进路径。优先使用 `async/await` 编写清晰、可维护的异步代码。
