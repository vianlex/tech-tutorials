---
title: 第二章 状态与事件
linkTitle: 状态与事件
description: useState 详解、状态不可变与更新、事件处理、受控组件、状态提升、对象与数组状态更新
weight: 167
---

# 状态与事件

React 的界面是「状态驱动的」：数据（state）变了，UI 自动重新渲染。`useState` 是管理组件内部状态的核心 Hook，事件处理则是让用户与界面交互的入口。

## useState 详解 {#usestate}

`useState` 返回一个数组：`[当前值, 更新函数]`。调用更新函数会触发组件重新渲染。

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);   // 初始值 0

  return (
    <div>
      <p>当前计数：{count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  );
}
```

### 更新函数的两种写法 {#setter-forms}

```jsx
// 1. 直接传新值
setCount(count + 1);

// 2. 传函数（基于上一个值计算，推荐用于依赖旧值的场景）
setCount(prev => prev + 1);
```

> [!WARNING]
> **关键区别**：直接传值用的是「闭包里捕获的旧值」，连续多次调用会互相覆盖；传函数则总是基于最新值。连续更新、或在异步回调里更新时，务必用函数式更新：

```jsx
// ❌ 三个都基于同一个旧 count，最终只 +1
setCount(count + 1);
setCount(count + 1);
setCount(count + 1);

// ✅ 依次基于最新值，最终 +3
setCount(c => c + 1);
setCount(c => c + 1);
setCount(c => c + 1);
```

### 状态是不可变的 {#immutable}

不要直接修改 state 对象/数组，而要用「创建新对象/数组」的方式更新：

```jsx
const [user, setUser] = useState({ name: 'Alice', age: 18 });

// ❌ 直接改属性，React 检测不到变化，不会重新渲染
user.age = 19;

// ✅ 用展开运算符创建新对象
setUser({ ...user, age: 19 });
```

```jsx
const [todos, setTodos] = useState([]);

// 添加
setTodos([...todos, newTodo]);
// 删除
setTodos(todos.filter(t => t.id !== id));
// 修改
setTodos(todos.map(t => t.id === id ? { ...t, done: true } : t));
```

> [!NOTE]
> React 用 `Object.is` 比较新旧 state 判断是否更新。直接改原对象/数组（引用没变）不会触发渲染——这就是「不可变更新」的原因。

## 事件处理 {#events}

React 的事件是「合成事件」，用驼峰命名，传入处理函数：

```jsx
function ClickDemo() {
  function handleClick() {
    console.log('点击了按钮');
  }

  function handleChange(e) {
    console.log('输入值', e.target.value);   // e 是合成事件对象
  }

  return (
    <>
      <button onClick={handleClick}>点击</button>
      <input onChange={handleChange} />
    </>
  );
}
```

### 传参 {#event-args}

```jsx
// 用箭头函数包裹，传入额外参数
<button onClick={() => handleDelete(item.id)}>删除</button>

// 或事件对象 + 参数
<button onClick={(e) => handleDelete(e, item.id)}>删除</button>
```

### 阻止默认行为 {#prevent-default}

```jsx
function Form() {
  function handleSubmit(e) {
    e.preventDefault();   // 阻止表单默认跳转刷新
    // 处理提交...
  }
  return <form onSubmit={handleSubmit}>...</form>;
}
```

## 受控组件 {#controlled}

「受控组件」指表单元素的值**由 React state 控制**，而不是由 DOM 自身管理。这是 React 处理表单的标准方式：

```jsx
function NameForm() {
  const [name, setName] = useState('');

  return (
    <div>
      <input
        value={name}                      // 值来自 state
        onChange={(e) => setName(e.target.value)}  // 输入时更新 state
      />
      <p>你输入的是：{name}</p>
    </div>
  );
}
```

常用受控元素：

```jsx
// 文本域
const [text, setText] = useState('');
<textarea value={text} onChange={e => setText(e.target.value)} />

// 复选框
const [checked, setChecked] = useState(false);
<input type="checkbox" checked={checked} onChange={e => setChecked(e.target.checked)} />

// 下拉框
const [city, setCity] = useState('');
<select value={city} onChange={e => setCity(e.target.value)}>
  <option value="">请选择</option>
  <option value="bj">北京</option>
  <option value="sh">上海</option>
</select>
```

> [!TIP]
> 受控组件让「表单数据」与「组件状态」保持单一数据源，便于实时校验、联动、提交。与之相对的「非受控组件」用 `useRef` 直接读 DOM（见第四章），适合不需要实时响应的场景。

## 状态提升 {#lifting-state}

当**多个组件需要共享同一份状态**时，把状态「提升」到它们最近的共同父组件，通过 props 下发：

```jsx
function TemperatureInput({ value, onChange }) {
  return <input value={value} onChange={e => onChange(e.target.value)} />;
}

function App() {
  const [temp, setTemp] = useState('');   // 状态提升到父组件

  return (
    <div>
      {/* 两个输入框共享同一份 temp */}
      <TemperatureInput value={temp} onChange={setTemp} />
      <TemperatureInput value={temp} onChange={setTemp} />
      <p>当前温度：{temp}℃</p>
    </div>
  );
}
```

> [!NOTE]
> 状态提升是 React 的核心理念：**数据单向向下流动**。共享状态放父组件，子组件通过 props 读值、通过回调通知父组件更新。当状态需要跨更多层级共享时，再考虑 Context（见第四章）或状态管理库。

## 小结 {#summary}

本章掌握了 React 状态管理的核心：`useState` 的两种更新写法（直接传值 vs 函数式）、状态的不可变更新（展开运算符）、事件处理与传参、受控组件模式，以及「状态提升」的共享状态思路。记住两条铁律：**状态不可变更新**、**连续更新用函数式**。下一章学习如何用 `useEffect` 处理副作用（数据获取、订阅、DOM 操作）。
