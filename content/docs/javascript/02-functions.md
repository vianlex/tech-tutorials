---
title: 第二章 函数与作用域
linkTitle: 函数与作用域
description: JavaScript 函数声明、闭包、this 绑定与作用域链
weight: 22
---

# 函数与作用域

## 函数声明 {#function-declaration}

```javascript
// 函数声明
function add(a, b) {
    return a + b;
}

// 函数表达式
const multiply = function(a, b) {
    return a * b;
};

// 箭头函数
const subtract = (a, b) => a - b;
```

## 作用域 {#scope}

JavaScript 有**函数作用域**和**块级作用域**（`let`/`const`）：

```javascript
let global = '全局';

function outer() {
    let local = '函数局部';
    if (true) {
        let block = '块级';
        console.log(block); // 可访问
    }
    // console.log(block);  // ❌ 块级变量在块外不可访问
    console.log(local);     // ✅ 可访问
}
```

## 闭包 {#closure}

**闭包**是函数记住其定义时所在作用域的能力：

```javascript
function createCounter() {
    let count = 0;          // 被内部函数引用
    return function() {
        return ++count;     // 访问外部变量
    };
}

const counter = createCounter();
counter(); // 1
counter(); // 2
counter(); // 3  ← count 状态被保留
```

闭包常用于：数据私有化、工厂函数、柯里化。

## this 关键字 {#this}

`this` 的值取决于**调用方式**，而非定义位置：

```javascript
const user = {
    name: 'Alice',
    greet() {
        console.log(`Hello, ${this.name}`);
    }
};

user.greet();            // "Hello, Alice"  ← this 指向 user

const fn = user.greet;
fn();                    // "Hello, undefined" ← this 丢失
```

> [!TIP]
> 箭头函数**不绑定自己的 `this`**，它继承外层作用域的 `this`，常用于回调中保持上下文。

## 小结 {#summary}

函数是 JavaScript 的一等公民，闭包和作用域是理解异步、模块化的前提。下一章学习 ES6+ 的现代特性。
