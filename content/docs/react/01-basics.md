---
title: 第一章 基础与 JSX
linkTitle: 基础与 JSX
description: 组件与函数组件、JSX 语法规则、props 传参与解构、条件渲染、列表渲染与 key、组件组合
weight: 166
---

# 基础与 JSX

React 用**组件**构建 UI，用 **JSX** 描述界面结构，用 **props** 在组件间传递数据。这是 React 的三大基石，先从这里建立心智模型。

## 组件与 JSX {#component-jsx}

React 中，UI 由一个个「组件」拼装而成。现代 React 以**函数组件**为主流：

```jsx
// 一个最简单的函数组件：接收 props，返回 JSX
function Welcome(props) {
  return <h1>你好，{props.name}</h1>;
}

// 箭头函数写法（更常见）
const Welcome = ({ name }) => <h1>你好，{name}</h1>;

// 使用组件
<Welcome name="Alice" />
```

> [!NOTE]
> 组件名必须**大写字母开头**（`Welcome` 而非 `welcome`）。小写会被当作普通 HTML 标签处理。这是 React 区分「组件」与「原生标签」的约定。

## JSX 语法规则 {#jsx-rules}

JSX 是「写在 JS 里的类 HTML 语法」，会被编译成 `React.createElement` 调用。它有几条必须记住的规则：

### 1. 必须有一个根元素（或 Fragment） {#root-element}

```jsx
// ❌ 错误：多个根元素
return <h1>标题</h1><p>内容</p>;

// ✅ 用 Fragment（空标签）包裹，不产生多余 DOM
return (
  <>
    <h1>标题</h1>
    <p>内容</p>
  </>
);
```

### 2. 用 {} 嵌入 JavaScript 表达式 {#expression}

```jsx
const name = 'Alice';
const user = { age: 18 };

<div>
  <p>{name}</p>                    {/* 嵌入变量 */}
  <p>{user.age >= 18 ? '成年' : '未成年'}</p>  {/* 三元表达式 */}
  <p>{[1, 2, 3].map(n => n * 2)}</p>           {/* 表达式求值 */}
</div>
```

### 3. 属性名用驼峰、class 改 className {#attribute}

```jsx
// HTML 的 class → className；for → htmlFor；onclick → onClick
<div className="card" onClick={handleClick}>
  <label htmlFor="name">姓名</label>
  <input id="name" />
</div>
```

### 4. style 用对象 {#style}

```jsx
<div style={{ color: 'red', fontSize: 20 }}>
  {/* fontSize 驼峰；数值默认 px */}
</div>
```

### 5. 注释写法 {#comment}

```jsx
{/* 这是 JSX 注释，必须包在大括号里 */}
```

## props：向子组件传数据 {#props}

props 是父组件传给子组件的**只读数据**，子组件不能修改它：

```jsx
function UserCard({ name, age, avatar }) {   // 解构 props
  return (
    <div className="card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <p>年龄：{age}</p>
    </div>
  );
}

// 父组件传值
<UserCard name="Alice" age={18} avatar="/a.png" />
```

### 默认值 {#default-props}

```jsx
function UserCard({ name = '匿名', age = 0 }) {
  return <p>{name}，{age} 岁</p>;
}
```

### children：插槽内容 {#children}

`props.children` 表示组件标签之间的内容，用于布局类组件：

```jsx
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div>{children}</div>   {/* 这里放传入的内容 */}
    </div>
  );
}

<Card title="公告">
  <p>这是一段自定义内容</p>
  <button>了解详情</button>
</Card>
```

## 条件渲染 {#conditional}

React 没有 `v-if`/`ng-if`，用 JS 原生语法实现条件渲染：

```jsx
// 1. 三元表达式
{isLoggedIn ? <UserPanel /> : <LoginButton />}

// 2. 逻辑与 &&（条件为真才渲染后面）
{unreadCount > 0 && <span className="badge">{unreadCount}</span>}

// 3. 提前 return
function Greeting({ name }) {
  if (!name) return <p>请先登录</p>;
  return <h1>欢迎，{name}</h1>;
}
```

> [!WARNING]
> `&&` 的陷阱：当左侧是 `0` 或 `''` 等假值时，会**渲染出 `0` 或空字符串**。例如 `{count && <p>...</p>}` 在 `count===0` 时会显示一个 `0`。稳妥写法用三元 `{count > 0 && ...}` 或 `{count ? ... : null}`。

## 列表渲染与 key {#list-key}

用 `map` 渲染列表，每个元素需唯一的 `key`：

```jsx
const users = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' },
];

function UserList() {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>   // key 用稳定的唯一 id
      ))}
    </ul>
  );
}
```

> [!TIP]
> **key 的作用**：帮助 React 识别哪些元素变了，从而高效复用/更新 DOM。key 必须是**稳定且唯一**的（如 id），**绝不要用数组下标 `index`**——列表增删/排序时下标会错位，导致状态错乱。

## 小结 {#summary}

本章掌握了 React 的三大基石：函数组件、JSX 语法规则（根元素、`{}` 表达式、驼峰属性、className）、props 传参与 children 插槽，以及条件渲染和列表渲染的 key 原则。这些是写任何 React 界面的基础。下一章进入核心——用 `useState` 管理组件状态、处理用户事件。
