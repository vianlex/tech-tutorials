---
title: 第四章 DOM 与事件
linkTitle: DOM 与事件
description: 使用 DOM API 操作网页元素与处理用户事件
weight: 24
---

# DOM 与事件

## 什么是 DOM {#what-is-dom}

DOM（Document Object Model）是浏览器把 HTML 解析成的树形结构，JavaScript 通过 DOM API 读写网页内容。

```text
document
 └── html
      ├── head
      └── body
           ├── div#app
           │    └── p.text
           └── button#btn
```

## 选择元素 {#select-elements}

```javascript
document.getElementById('app');                    // 按 id
document.querySelector('.text');                   // 按 CSS 选择器（第一个）
document.querySelectorAll('p');                    // 所有匹配元素
```

## 修改内容与样式 {#modify}

```javascript
const el = document.querySelector('#app');
el.textContent = '新文本';          // 纯文本
el.innerHTML = '<b>加粗</b>';       // 含 HTML（注意 XSS 风险）
el.style.color = 'red';             // 修改样式
el.classList.add('active');         // 添加 class
```

## 创建与删除元素 {#create-remove}

```javascript
// 创建
const li = document.createElement('li');
li.textContent = '新项';
document.querySelector('ul').appendChild(li);

// 删除
li.remove();
```

## 事件处理 {#events}

```javascript
const btn = document.querySelector('#btn');

// 方式一：addEventListener（推荐）
btn.addEventListener('click', (event) => {
    console.log('按钮被点击', event.target);
});

// 方式二：直接赋值（会覆盖）
btn.onclick = () => console.log('点击');
```

### 事件冒泡与委托 {#delegation}

```javascript
// 事件委托：在父元素监听子元素事件
document.querySelector('ul').addEventListener('click', (e) => {
    if (e.target.tagName === 'LI') {
        console.log('点击了列表项：', e.target.textContent);
    }
});
```

## 小结 {#summary}

DOM 操作是前端交互的基础。理解事件冒泡和委托能写出更高效的代码。下一章学习异步编程。
