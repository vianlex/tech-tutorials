---
title: 第一章 基础语法与类型
linkTitle: 基础语法
description: JavaScript 变量声明、变量提升与暂时性死区、数据类型、类型转换、相等性与常用内置方法
weight: 21
---

# 基础语法与类型

JavaScript 是**动态类型、弱类型**的脚本语言：变量在声明时不需要指定类型，同一个变量可在运行时被赋予不同类型的值；同时运算符会在需要时自动进行类型转换。理解这套「宽松」规则背后的原理，是写出正确代码的第一步。

## 变量声明 {#variables}

ES6 之前只有 `var`，ES2015 之后引入 `let` 和 `const`。现代工程基本只使用 `let` 与 `const`，`var` 因「变量提升」带来的隐蔽 bug 已被弃用。

| 关键字 | 作用域 | 可重复声明 | 可重新赋值 | 是否提升 | 暂时性死区 |
|--------|--------|-----------|-----------|---------|-----------|
| `var` | 函数作用域 | 是 | 是 | 是（初始化 undefined） | 无 |
| `let` | 块级作用域 | 否 | 是 | 是（不初始化） | 有 |
| `const` | 块级作用域 | 否 | 否（引用不变） | 是（不初始化） | 有 |

```javascript
let name = 'Alice';   // 可重新赋值
const PI = 3.14159;   // 常量，不可重新绑定（但对象内部属性可改）
PI = 3;               // ❌ TypeError: Assignment to constant variable

const obj = { a: 1 };
obj.a = 2;            // ✅ 允许，const 只禁止重新绑定，不禁止修改内部
obj = {};             // ❌ 报错
```

> [!NOTE]
> `const` 保证的是**绑定不变**（变量名始终指向同一内存地址），不是**值不可变**。需深层不可变可配合 `Object.freeze()`（只冻结一层）。

## 变量提升与暂时性死区 {#hoisting-tdz}

「提升（hoisting）」是引擎在**编译阶段**把变量和函数声明移到作用域顶部的行为。

### var 的提升 {#var-hoisting}

`var` 声明会被提升且**初始化为 `undefined`**：

```javascript
console.log(a);  // undefined（不报错，a 已被提升）
var a = 10;
console.log(a);  // 10
```

### let / const 的提升与 TDZ {#let-tdz}

`let`/`const` 同样提升，但**不初始化**。从作用域开始到声明语句执行前的区域称为「暂时性死区（TDZ）」，访问会抛错：

```javascript
console.log(b);  // ❌ ReferenceError: Cannot access 'b' before initialization
let b = 20;

typeof x;        // ❌ ReferenceError（x 处于 TDZ，连 typeof 都会抛错）
let x = 1;
```

### 函数声明提升 {#function-hoisting}

函数**声明**会被整体提升（含函数体），可在声明前调用；函数**表达式**不会：

```javascript
foo();  // "hello"（声明被完整提升）
function foo() { console.log('hello'); }

bar();  // ❌ TypeError: bar is not a function
var bar = function() { console.log('hi'); };
```

## 数据类型 {#types}

### 七种原始类型 {#primitive-types}

```javascript
let num    = 42;                  // number（双精度浮点数）
let big    = 9007199254740991n;   // bigint（任意精度整数）
let str    = 'hello';             // string
let bool   = true;               // boolean
let undef  = undefined;           // undefined
let empty  = null;               // null
let sym    = Symbol('id');        // symbol
```

原始类型按值存储、不可变；任何「修改」其实是创建新值。

### 浮点精度与 BigInt {#number-precision}

`number` 遵循 IEEE 754 双精度，存在经典精度问题：

```javascript
0.1 + 0.2;            // 0.30000000000000004
0.1 + 0.2 === 0.3;    // false

// 安全整数范围 ±(2^53 - 1)
9007199254740991 + 2; // 9007199254740992 ❗（精度丢失）

// 解决：误差比较 / BigInt / 整数「分」存储
Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON;  // true
9007199254740991n + 2n;                      // 9007199254740993n
```

### Symbol 用途 {#symbol-use}

`Symbol` 创建全局唯一值，常用于避免属性名冲突，或定义语言内部行为（知名符号）：

```javascript
const KEY = Symbol('description');
const obj = { [KEY]: '隐藏数据' };  // 不会被普通遍历拿到
```

### NaN 与 Infinity {#nan-infinity}

```javascript
typeof NaN;            // "number"（仍是数字类型）
NaN === NaN;           // false ❗（NaN 不等于任何值，包括自己）
Number.isNaN(NaN);     // true（推荐）
isNaN('abc');          // true（先转类型，已不推荐）

1 / 0;                 // Infinity
Number.isFinite(1 / 0); // false
```

> [!TIP]
> 永远用 `Number.isNaN()` 而非全局 `isNaN()`，前者不会先强制类型转换。

### 引用类型 {#reference-types}

```javascript
const a = { v: 1 };
const b = a;        // 赋值是复制「引用地址」，a、b 指向同一内存
b.v = 2;
console.log(a.v);   // 2（a 也被改变）
```

## 类型判断 {#type-check}

`typeof` 判断原始类型，但有历史遗留坑：

```javascript
typeof 42;            // "number"
typeof 'hello';       // "string"
typeof null;          // "object"  ← 历史遗留坑
typeof [];            // "object"
typeof function(){};  // "function"
```

> [!WARNING]
> `typeof null` 返回 `"object"` 是历史遗留问题。判断 `null` 应用 `value === null`；判断数组用 `Array.isArray(arr)`。

## 类型转换 {#type-conversion}

### 显式转换 {#explicit-conversion}

```javascript
Number('42');      // 42
String(42);        // "42"
Boolean(0);        // false
parseInt('10px', 10); // 10
+'42';             // 42（一元加号转数字）
!!'hello';         // true（双重取反转布尔）
```

### 隐式转换与 + 号陷阱 {#implicit-conversion}

`+` 号只要有一侧是字符串就做拼接而非加法：

```javascript
1 + 2;             // 3
1 + '2';           // "12"（数字转字符串）
1 + 2 + '3';       // "33"
'3' - 1;           // 2（其他算术运算符都转数字）
```

### 宽松相等 == 的转换规则 {#loose-equality}

```javascript
1 == '1';          // true（字符串转数字）
0 == false;        // true
'' == false;       // true
null == undefined; // true（仅此一对彼此相等）
null == 0;         // false（null 不转数字）
```

> [!WARNING]
> `==` 规则复杂且反直觉（如 `[] == false` 为 `true`）。**始终用 `===`**，仅 `== null` 同时判断 `null`/`undefined` 时可用宽松相等。

### truthy / falsy 完整列表 {#truthy-falsy}

只有以下 8 个值会隐式转为 `false`，其余皆 `true`：

```javascript
// 假值：false、undefined、null、0、-0、0n、NaN、''（空字符串）
Boolean([]);        // true（空数组是真值！）
Boolean({});        // true（空对象是真值！）
Boolean('0');       // true
Boolean('false');   // true
```

## 相等性比较 {#equality}

```javascript
1 === '1';          // false（严格相等，不转换类型）
Object.is(1, '1');  // false

// Object.is 与 === 的细微差别：
Object.is(NaN, NaN);   // true  ← === 返回 false
Object.is(+0, -0);     // false ← === 返回 true
+0 === -0;             // true

// 建议：绝大多数用 ===；需判断「是否同一 NaN / 区分 +0 和 -0」时用 Object.is
```

## 字符串与数字常用方法 {#string-number-methods}

```javascript
'  Hello  '.trim();          // "Hello"
'hElLo'.toUpperCase();        // "HELLO"
'apple,banana'.split(',');    // ["apple", "banana"]
'Hello'.includes('ell');      // true
'Hello'.slice(1, 3);          // "el"（左闭右开）
'abc'.padStart(5, '0');       // "00abc"

(3.14159).toFixed(2);         // "3.14"（返回字符串）
Math.floor(4.9);              // 4
Math.max(...[1, 5, 3]);       // 5
```

## 可选链与空值合并 {#optional-chaining}

处理深层可能缺失的属性时，用可选链 `?.` 和空值合并 `??` 替代冗长的 `&&`：

```javascript
const user = { profile: { name: 'Alice' } };
user.profile?.name;        // "Alice"
user.contact?.email;       // undefined（不会抛错）
user?.profile?.name;       // "Alice"

const port = config.port ?? 8080;  // 仅 null/undefined 时取默认
const n = 0 ?? 100;                // 0（保留 0，不像 || 会兜底）
const s = '' ?? '默认';             // ""（保留空串）

// 对比 ||
const bad = 0 || 100;      // 100 ❗（误把 0 当缺省）
```

> [!NOTE]
> `?.` 还支持函数调用 `obj.fn?.()` 与动态属性 `obj?.[key]`，在对象形态不确定时非常安全。

## 数组与对象常用方法 {#array-object-methods}

函数式数组方法是日常主力，重点掌握 `map`/`filter`/`reduce`：

```javascript
const nums = [1, 2, 3, 4, 5];

// map：映射为新数组（不改原数组）
const doubled = nums.map(n => n * 2);          // [2,4,6,8,10]

// filter：按条件过滤
const evens = nums.filter(n => n % 2 === 0);  // [2,4]

// reduce：聚合为任意结果（最强大）
const sum = nums.reduce((acc, n) => acc + n, 0);          // 15
const groups = nums.reduce((acc, n) => {
    const key = n % 2 === 0 ? 'even' : 'odd';
    (acc[key] ||= []).push(n);
    return acc;
}, {});                                             // { odd:[1,3,5], even:[2,4] }

// find / some / every
nums.find(n => n > 3);     // 4
nums.some(n => n > 4);     // true
nums.every(n => n > 0);    // true

// 展开与对象解构
const copy = [...nums];
const ext = { ...{ a: 1, b: 2 }, c: 3 };  // { a:1, b:2, c:3 }
const { a, ...rest } = ext;               // a=1, rest={ b:2, c:3 }
```

## 控制流 {#control-flow}

```javascript
// 条件
if (score >= 90) console.log('优秀');
else if (score >= 60) console.log('及格');
else console.log('不及格');

// 循环
for (let i = 0; i < 5; i++) console.log(i);
for (const item of arr) console.log(item); // 遍历值（可迭代对象）
for (const key in obj) console.log(key);   // 遍历可枚举键（含原型链，慎用）
```

## 小结 {#summary}

本章深入了变量提升与暂时性死区、七种原始类型（含浮点精度与 BigInt）、隐式/显式类型转换、宽松与严格相等的差异，以及可选链、空值合并和函数式数组方法等现代语法。这些底层规则贯穿整个语言，理解它们能避免绝大多数「莫名 bug」。下一章将深入函数与作用域、闭包与 `this` 绑定。
