---
title: 第四章 DOM 与事件
linkTitle: DOM 与事件
description: DOM 树与节点类型、元素选择与属性操作、增删改节点、事件三阶段与事件委托、自定义事件、回流重绘优化及防抖节流
weight: 24
---

# DOM 与事件

DOM（Document Object Model）是浏览器把 HTML 解析成的树形结构，JavaScript 通过 DOM API 读写网页内容与处理交互。本章深入节点操作与事件机制，并关注性能优化。

## 什么是 DOM {#what-is-dom}

浏览器读取 HTML 后生成节点树，JS 操作的就是这棵树：

```text
document
 └── html
      ├── head
      └── body
           ├── div#app
           │    └── p.text
           └── button#btn
```

### 节点类型 {#node-types}

```javascript
document.nodeType;            // 9  (DOCUMENT_NODE)
document.body.nodeType;      // 1  (ELEMENT_NODE)
document.body.firstChild.nodeType; // 3 (TEXT_NODE，含空白)

// children 只返回元素节点，childNodes 含文本/注释
const els = [...document.body.children];
```

> [!NOTE]
> 布局/遍历逻辑通常用 `children`，避免被文本/注释节点干扰。

## 选择元素 {#select-elements}

```javascript
document.getElementById('app');          // 按 id（最快，O(1) 哈希）
document.querySelector('.text');         // 第一个匹配 CSS 选择器
document.querySelectorAll('p');          // 所有匹配（NodeList）
document.getElementsByClassName('item'); // 实时 HTMLCollection
```

### 选择器性能差异 {#selector-performance}

- `getElementById` 是引擎内建哈希查找，最快。
- `querySelector` 需解析 CSS 选择器，略慢但灵活。
- `getElementsByClassName`/`TagName` 返回**实时集合**：DOM 变更即时反映，遍历时边改边删要倒序，否则下标错位。

```javascript
const live = document.getElementsByClassName('item');
for (let i = live.length - 1; i >= 0; i--) live[i].remove();  // 倒序删除
```

## 修改内容与样式 {#modify}

```javascript
const el = document.querySelector('#app');
el.textContent = '新文本';          // 纯文本（安全，不解析 HTML）
el.innerHTML = '<b>加粗</b>';       // 解析 HTML（需防 XSS）
el.style.color = 'red';
el.classList.add('active');
el.classList.toggle('hidden');
```

> [!WARNING]
> `innerHTML` 拼接用户输入会引发 XSS。渲染用户内容优先用 `textContent`，或先转义。

## 属性操作 {#attributes}

### getAttribute / setAttribute {#get-set-attribute}

```javascript
const a = document.querySelector('a');
a.getAttribute('href');   // 源码原始值（字符串）
a.setAttribute('href', '/new');

// 属性(property) vs 特性(attribute)：
// - el.href 是「属性」，经浏览器规范化（补全为绝对 URL）
// - getAttribute('href') 是「特性」，返回源码原始值
```

### dataset 与 classList {#dataset-classlist}

```javascript
// <div data-user-id="7" data-role="admin">
const box = document.querySelector('div');
box.dataset.userId;   // "7"（自动驼峰）
box.dataset.role;     // "admin"
box.classList.contains('active');  // 是否包含
```

## 创建与删除元素 {#create-remove}

```javascript
const li = document.createElement('li');
li.textContent = '新项';

const ul = document.querySelector('ul');
ul.appendChild(li);                       // 追加
ul.insertBefore(li, ul.firstChild);        // 插入到参考节点前
ul.append(li.cloneNode(true));             // 深克隆后追加

li.replaceWith(document.createElement('span'));  // 替换自身
li.remove();                               // 删除
```

### DocumentFragment 批量插入优化 {#document-fragment}

逐个 `appendChild` 会触发多次回流，用 `DocumentFragment` 在内存拼好再一次性插入，只触发一次：

```javascript
const frag = document.createDocumentFragment();
for (let i = 0; i < 1000; i++) {
    const node = document.createElement('li');
    node.textContent = `项 ${i}`;
    frag.appendChild(node);     // 仍在内存，不触发回流
}
ul.appendChild(frag);           // 一次性插入，仅一次回流
```

## 事件处理 {#events}

### addEventListener 与第三参数 {#add-event-listener}

```javascript
const btn = document.querySelector('#btn');
btn.addEventListener('click', (e) => console.log('点击', e.target));

// 第三参数可以是布尔（捕获阶段）或选项对象：
btn.addEventListener('click', handler, {
    capture: true,   // 捕获阶段触发
    once: true,      // 触发一次后自动移除
    passive: true    // 声明不调用 preventDefault，提升滚动性能
});
```

> [!TIP]
> 对 `scroll`/`touchmove` 高频事件设 `passive: true`，浏览器可提前优化避免卡顿。

### 事件对象 {#event-object}

```javascript
btn.addEventListener('click', (e) => {
    e.target;            // 实际触发元素
    e.currentTarget;     // 绑定监听的元素
    e.clientX;           // 视口坐标
    e.preventDefault();   // 阻止默认行为
    e.stopPropagation();  // 阻止冒泡
});
```

### 捕获与冒泡三阶段 {#capture-bubble}

事件流分三阶段：**捕获**（window 向下到目标）→ **目标**（到达实际元素）→ **冒泡**（目标向上回 window）。

```javascript
document.querySelector('#outer').addEventListener('click', () => {
    console.log('outer 捕获');
}, true);   // 捕获阶段（外层先触发）
document.querySelector('#inner').addEventListener('click', () => {
    console.log('inner 冒泡');
}, false);  // 冒泡阶段（默认，内层先触发）
```

### stopPropagation vs preventDefault {#stop-vs-prevent}

- `stopPropagation()`：阻止事件继续在 DOM 树传播（不影响默认行为）。
- `preventDefault()`：阻止浏览器对该事件的默认动作（不影响传播）。

## 事件委托 {#delegation}

事件委托利用**冒泡**：把子元素监听统一挂到**父元素**，既减少监听器数量，又自动处理动态新增子元素。

```javascript
document.querySelector('ul').addEventListener('click', (e) => {
    if (e.target.tagName === 'LI') {
        console.log('点击了列表项：', e.target.textContent);
    }
});
```

### 精确匹配：closest / matches {#closest-matches}

当子元素内部还有嵌套时，`e.target` 未必是期望的 `LI`，用 `closest` 更稳健：

```javascript
document.querySelector('ul').addEventListener('click', (e) => {
    const li = e.target.closest('li.item');  // 向上找最近匹配（含自身）
    if (!li) return;                         // 点到了非 li 区域，忽略
    console.log('item', li.dataset.id);
});
```

> [!TIP]
> 委托监听器要注册在稳定的父容器上，不要注册在会频繁重渲染的子元素上。

## 自定义事件 {#custom-events}

组件间可用 `CustomEvent` 通信（配合 `dispatchEvent`）：

```javascript
const evt = new CustomEvent('score-changed', {
    detail: { score: 100 },   // 自定义数据放 detail
    bubbles: true             // 是否冒泡
});
document.querySelector('#game').dispatchEvent(evt);

document.addEventListener('score-changed', (e) => {
    console.log('新分数', e.detail.score);  // 100
});
```

## 回流与重绘 {#reflow-repaint}

- **回流（reflow）**：几何属性（尺寸、位置）改变，需重算布局，代价高。
- **重绘（repaint）**：仅外观（颜色、背景）改变，布局不变，代价较低。

### 触发回流与批量优化 {#trigger-reflow}

```javascript
// 以下触发回流，应尽量减少或批量
el.style.width = '100px';
el.offsetHeight;   // 读取布局属性会强制同步回流

// 正解：先批量写，最后统一读
items.forEach(it => list.appendChild(it));
const total = list.offsetHeight;  // 仅一次读
```

### requestAnimationFrame {#raf}

把回调安排到**下一次重绘前**执行，适合动画与高频 DOM 更新，避免掉帧：

```javascript
function animate() {
    box.style.transform = `translateX(${x}px)`;
    x += 2;
    if (x < 300) requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

## 防抖与节流 {#debounce-throttle}

高频事件（输入、滚动、resize）需限流，否则严重消耗性能。

### 防抖 debounce {#debounce}

「事件停止触发 wait 毫秒后才执行」——适合搜索联想、表单校验（只关心最后一次）。

```javascript
function debounce(fn, wait = 300) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), wait);
    };
}
input.addEventListener('input', debounce((e) => {
    console.log('搜索：', e.target.value);
}, 400));
```

### 节流 throttle {#throttle}

「每隔 wait 毫秒最多执行一次」——适合滚动加载、拖拽（既要响应又要限频）。

```javascript
function throttle(fn, wait = 300) {
    let last = 0;
    return function (...args) {
        const now = Date.now();
        if (now - last >= wait) { last = now; fn.apply(this, args); }
    };
}
window.addEventListener('scroll', throttle(() => {
    console.log('滚动位置', window.scrollY);
}, 200));
```

> [!NOTE]
> 防抖关注「停顿」，节流关注「频率」；需立即响应首次用节流，需等用户「最终态」用防抖。

## 小结 {#summary}

本章深入了 DOM 树与节点类型、选择器性能差异、属性与 dataset 操作、节点增删改与 `DocumentFragment` 批量优化，并系统讲解事件三阶段、事件委托（`closest` 精确匹配）、自定义事件，以及回流/重绘与 `requestAnimationFrame` 优化。防抖与节流的完整实现可直接用于高频交互。下一章进入异步编程与 Promise，理解事件循环是掌握这一切的关键。
