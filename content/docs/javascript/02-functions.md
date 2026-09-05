---
title: 第二章 函数与作用域
linkTitle: 函数与作用域
description: 函数声明与表达式、参数机制、作用域链与词法作用域、闭包原理与内存、this 绑定规则及高阶函数
weight: 22
---

# 函数与作用域

函数是 JavaScript 的基石。本章从「函数是一等公民」出发，逐步拆解参数传递、作用域链、闭包以及 `this` 绑定这些易混淆的主题。

## 函数声明 {#function-declaration}

多种定义方式在**提升行为**和**使用场景**上不同：

```javascript
// 1) 函数声明：整体提升，可在定义前调用
function add(a, b) { return a + b; }

// 2) 函数表达式：遵循变量提升/TDZ 规则，须赋值后才可用
const multiply = function(a, b) { return a * b; };

// 3) 箭头函数：更简洁，且不绑定自己的 this/arguments/super
const subtract = (a, b) => a - b;
```

## 一等公民 {#first-class}

「函数是一等公民」意味着函数可像普通值一样：赋值给变量、作为参数传递、作为返回值、挂在对象上。

```javascript
const greet = (name) => `Hi ${name}`;        // 赋值
[1, 2, 3].forEach(function log(n) { console.log(n); }); // 作为参数
function makeAdder(x) { return (y) => x + y; } // 作为返回值（工厂）
const add10 = makeAdder(10);
add10(5);  // 15
```

这是「高阶函数」「闭包」「回调」的基础。

## 参数机制 {#parameters}

### 默认参数 {#default-parameters}

```javascript
function greet(name = 'World', prefix = 'Hello') {
    return `${prefix}, ${name}`;
}
greet();              // "Hello, World"
greet('Alice');       // "Hello, Alice"

// 默认参数有「自己的作用域」，会形成临时 TDZ
function bad(x = y, y = 1) { return [x, y]; }
// bad();  // ❌ ReferenceError（x 的默认值引用了尚未初始化的 y）
```

### rest 参数与 arguments {#rest-arguments}

```javascript
// rest 参数：把剩余实参收集为真正的数组
function sum(...numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3, 4);     // 10

// 旧式 arguments 是类数组（非真数组），箭头函数没有它
function legacy() { return [...arguments]; }
```

### 参数按值传递 {#pass-by-value}

JS 所有参数都是**按值传递**；传入对象时「值」是**引用地址**（按共享引用）。修改对象属性会反映到外部，但重新赋值形参不影响外部：

```javascript
function mutate(o) { o.value = 99; }      // 改同一对象 → 外部可见
const obj = { value: 1 };
mutate(obj);
console.log(obj.value);   // 99

function reassign(o) { o = { value: 2 }; } // 重新绑定形参 → 不影响外部
reassign(obj);
console.log(obj.value);   // 99（仍是原对象）
```

## 作用域 {#scope}

### 词法作用域 {#lexical-scope}

JS 采用**词法（静态）作用域**：变量可访问性由**代码书写位置**决定，而非调用位置。

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

### 作用域链 {#scope-chain}

查找变量时沿「当前 → 外层 → … → 全局」逐级向上，这条链路即**作用域链**。

### 经典循环闭包陷阱 {#loop-closure}

`var` 无块级作用域，循环里所有 `setTimeout` 共享同一个 `i`，输出全是 5：

```javascript
// 反例：用 var，i 是函数作用域，循环结束 i=5
for (var i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 0); // 5 5 5 5 5
}
// 解法 1：改用 let（每次迭代新建块级绑定）
for (let i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 0); // 0 1 2 3 4
}
// 解法 2：IIFE 传参
for (var j = 0; j < 5; j++) {
    (function(k) { setTimeout(() => console.log(k), 0); })(j);
}
```

## 闭包 {#closure}

### 原理 {#closure-principle}

**闭包**是函数与其**词法环境的组合**——函数「记住」定义时所在作用域的变量，即使外层函数已执行完，这些变量仍可被内部函数访问。

```javascript
function createCounter() {
    let count = 0;
    return function() { return ++count; };
}
const counter = createCounter();
counter(); // 1
counter(); // 2
counter(); // 3  ← count 状态被保留
```

本质是：内部函数持有指向外部变量对象的引用，使该对象不被垃圾回收。

### IIFE 与模块模式 {#iife-module}

ES Module 出现前，IIFE 常用作「私有成员」：

```javascript
const counter = (function() {
    let count = 0;                       // 私有，外部不可直接访问
    return { inc() { return ++count; }, get() { return count; } };
})();
counter.inc();   // 1
```

### 内存泄漏风险 {#memory-leak}

闭包延长外部变量生命周期，不慎长期持有大对象会导致内存无法释放：

```javascript
function heavy() {
    const bigData = new Array(1e6).fill('*');
    return () => console.log(bigData.length); // bigData 被永久引用
}
const leak = heavy();
// 不再需要时手动解除引用：leak = null; 帮助回收
```

> [!WARNING]
> 事件监听、定时器回调里尤其注意闭包引用，卸载组件/清除定时器时记得释放引用。

## this 关键字 {#this}

`this` 在**调用时**确定，取决于**调用方式**。四条绑定规则按优先级从低到高。

### 默认绑定 {#default-binding}

独立函数调用时，`this` 指向全局对象（非严格）或 `undefined`（严格）：

```javascript
function foo() { console.log(this); }
foo();  // 严格模式: undefined；非严格: window
```

### 隐式绑定与 this 丢失 {#implicit-binding}

通过对象方法调用，`this` 指向调用者；把方法单独取出则丢失绑定：

```javascript
const user = {
    name: 'Alice',
    greet() { console.log(`Hello, ${this.name}`); }
};
user.greet();           // "Hello, Alice"
const fn = user.greet;
fn();                   // "Hello, undefined"（this 丢失）
setTimeout(user.greet, 0); // "Hello, undefined"（回调场景常见）
```

### 显式绑定 call / apply / bind {#explicit-binding}

```javascript
function show(extra) { console.log(`${this.name} - ${extra}`); }
const a = { name: 'A' }, b = { name: 'B' };
show.call(a, 'x');       // "A - x"（立即调用，参数逐个传）
show.apply(b, ['y']);    // "B - y"（立即调用，参数数组传）
const bound = show.bind(a, 'z');
bound();                 // "A - z"（bind 永久绑定，不立即执行）
```

### new 绑定与构造过程 {#new-binding}

`new Fn()` 做四件事：① 创建空对象；② 原型指向 `Fn.prototype`；③ 执行函数，`this` 指向该空对象；④ 若没返回对象则返回该对象。

```javascript
function Person(name) { this.name = name; }
const p = new Person('Tom');
console.log(p.name);   // "Tom"
```

优先级：**new > 显式 > 隐式 > 默认**。

### 箭头函数不绑定 this {#arrow-this}

箭头函数没有自己的 `this`，继承**外层词法作用域**的 `this`，且无法被 call/apply/bind 改变：

```javascript
const obj = {
    id: 1,
    bad() {
        setTimeout(function() { console.log(this.id); }, 0); // undefined
    },
    good() {
        setTimeout(() => { console.log(this.id); }, 0);      // 1
    }
};
```

## 高阶函数 {#higher-order}

接收函数为参数、或返回函数的函数称为高阶函数，让逻辑可被组合复用。

### 柯里化 {#currying}

把多参函数转为「每次接收一部分参数、返回新函数」：

```javascript
const curried = (a) => (b) => (c) => a + b + c;
curried(1)(2)(3);   // 6

// 通用柯里化（固定参数个数）
function curry(fn) {
    return function curried(...args) {
        return args.length >= fn.length
            ? fn.apply(this, args)
            : (...next) => curried.apply(this, [...args, ...next]);
    };
}
curry((a, b, c) => a + b + c)(1)(2)(3);  // 6
```

### 偏函数 {#partial-application}

「预先固定部分参数」生成参数更少的新函数（区别于柯里化的逐参收集）：

```javascript
function multiply(a, b, c) { return a * b * c; }
function partial(fn, ...preset) {
    return (...rest) => fn(...preset, ...rest);
}
partial(multiply, 2)(3, 4);  // 24
```

### 闭包应用：防抖与节流 {#debounce-throttle-fn}

（完整 DOM 版见第四章）

```javascript
function debounce(fn, wait = 300) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), wait);
    };
}
function throttle(fn, wait = 300) {
    let last = 0;
    return function(...args) {
        const now = Date.now();
        if (now - last >= wait) { last = now; fn.apply(this, args); }
    };
}
```

## 小结 {#summary}

本章从函数一等公民特性出发，拆解了参数按共享引用传递、词法作用域与作用域链、闭包内存原理与经典循环陷阱，并系统梳理 `this` 的四类绑定规则与箭头函数的词法特性。高阶函数、柯里化与偏函数展示了函数组合的强大。下一章学习 ES6+ 现代特性：解构、模板字符串、模块、class、迭代器与集合类型。
