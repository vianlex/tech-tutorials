---
title: 第一章 基础语法与类型
linkTitle: 基础语法
description: JavaScript 变量声明、数据类型、运算符与控制流
weight: 21
---

# 基础语法与类型

## 变量声明 {#variables}

现代 JavaScript 使用 `let` 和 `const`，避免使用 `var`：

```javascript
let name = 'Alice';   // 可重新赋值
const PI = 3.14159;   // 常量，不可重新赋值
```

| 关键字 | 作用域 | 可重复声明 | 可重新赋值 |
|--------|--------|-----------|-----------|
| `var` | 函数作用域 | 是 | 是 |
| `let` | 块级作用域 | 否 | 是 |
| `const` | 块级作用域 | 否 | 否 |

## 数据类型 {#types}

JavaScript 是**动态类型**语言，分为原始类型和引用类型：

```javascript
// 原始类型（7 种）
let num = 42;            // number
let big = 9007199254740991n; // bigint
let str = 'hello';       // string
let bool = true;         // boolean
let undef = undefined;   // undefined
let empty = null;        // null
let sym = Symbol('id');  // symbol

// 引用类型
let obj = { a: 1 };      // object
let arr = [1, 2, 3];     // array
function fn() {}          // function
```

## 类型判断 {#type-check}

```javascript
typeof 42;            // "number"
typeof 'hello';       // "string"
typeof null;          // "object"  ← 历史遗留的坑
typeof undefined;     // "undefined"
typeof [];            // "object"
typeof function(){};  // "function"
```

> [!WARNING]
> `typeof null` 返回 `"object"` 是历史遗留问题。判断 `null` 应使用 `value === null`。

## 相等性比较 {#equality}

```javascript
1 == '1';    // true  （宽松相等，会类型转换）
1 === '1';   // false （严格相等，推荐）
```

始终优先使用 `===` 和 `!==`。

## 控制流 {#control-flow}

```javascript
// 条件
if (score >= 90) {
    console.log('优秀');
} else if (score >= 60) {
    console.log('及格');
} else {
    console.log('不及格');
}

// 循环
for (let i = 0; i < 5; i++) { console.log(i); }
for (const item of arr) { console.log(item); } // 遍历值
for (const key in obj) { console.log(key); }   // 遍历键
```

## 小结 {#summary}

掌握变量声明、类型和相等性比较是写出正确 JavaScript 的基础。下一章深入函数与作用域。
