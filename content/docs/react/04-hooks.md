---
title: 第四章 常用 Hooks 详解
linkTitle: 常用 Hooks 详解
description: useRef、useMemo、useCallback、useContext、useReducer、自定义 Hook 的详细实践例子
weight: 169
---

# 常用 Hooks 详解

除了 `useState` 和 `useEffect`，React 还提供了几个高频使用的 Hooks。这一章逐个讲透它们的用途、区别，并给出可落地的实践例子。

## useRef：引用 DOM 与保存可变值 {#useref}

`useRef` 返回一个可变对象 `{ current }`，**修改它不会触发重新渲染**。两大用途：引用 DOM 节点、保存不参与渲染的可变值。

### 1. 操作 DOM 元素 {#dom-ref}

```jsx
import { useRef } from 'react';

function FocusInput() {
  const inputRef = useRef(null);

  function focus() {
    inputRef.current?.focus();   // 直接操作 DOM
  }

  return (
    <div>
      <input ref={inputRef} placeholder="点按钮聚焦我" />
      <button onClick={focus}>聚焦输入框</button>
    </div>
  );
}
```

### 2. 保存可变值（不触发渲染） {#mutable-value}

```jsx
function Timer() {
  const [count, setCount] = useState(0);
  const timerRef = useRef(null);   // 保存定时器 id，不需要渲染

  function start() {
    timerRef.current = setInterval(() => {
      setCount(c => c + 1);
    }, 1000);
  }

  function stop() {
    clearInterval(timerRef.current);
  }

  return (
    <div>
      <p>{count}</p>
      <button onClick={start}>开始</button>
      <button onClick={stop}>停止</button>
    </div>
  );
}
```

### 3. 记录上一次的值 {#prev-value}

```jsx
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;   // 渲染完成后才更新
  });
  return ref.current;      // 返回上一次的值
}
```

> [!NOTE]
> `useRef` 与 `useState` 的核心区别：**改 `ref.current` 不触发渲染**，改 state 会触发渲染。所以「用于渲染展示的数据」用 state，「不用于渲染、只需持久保存」的（定时器 id、DOM 引用、上一次的值）用 ref。

## useMemo：缓存计算结果 {#usememo}

当某个**昂贵的计算**依赖某些值，且这些值没变时，`useMemo` 返回缓存的旧结果，避免重复计算。

```jsx
import { useMemo } from 'react';

function ProductList({ products, filter }) {
  // 仅当 products 或 filter 变化时才重新过滤
  const filtered = useMemo(() => {
    console.log('执行过滤计算');
    return products.filter(p => p.name.includes(filter));
  }, [products, filter]);

  return (
    <ul>
      {filtered.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  );
}
```

> [!TIP]
> `useMemo` 是「用内存换时间」：避免昂贵计算重复执行。但**不要滥用**——普通计算很快，缓存本身也有开销，反而可能更慢。只对「计算昂贵 + 依赖稳定」的场景用。

## useCallback：缓存函数引用 {#usecallback}

`useCallback` 返回一个**记忆化的函数**，依赖不变时引用不变。主要用于配合 `React.memo` 优化子组件渲染。

```jsx
import { useCallback, memo } from 'react';

// 用 memo 包裹的子组件：props 不变就不重新渲染
const TodoItem = memo(function TodoItem({ todo, onToggle }) {
  console.log('TodoItem 渲染', todo.id);
  return (
    <li onClick={() => onToggle(todo.id)}>
      {todo.title} {todo.done ? '✅' : ''}
    </li>
  );
});

function TodoList() {
  const [todos, setTodos] = useState([...]);

  // 若不用 useCallback，每次父组件渲染都会新建 onToggle，
  // 导致所有 TodoItem 都重新渲染（memo 失效）
  const handleToggle = useCallback((id) => {
    setTodos(list => list.map(t =>
      t.id === id ? { ...t, done: !t.done } : t
    ));
  }, []);   // 空依赖：函数永不变化

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem key={todo.id} todo={todo} onToggle={handleToggle} />
      ))}
    </ul>
  );
}
```

> [!NOTE]
> `useMemo` 缓存「值」，`useCallback` 缓存「函数」（本质是 `useMemo` 返回函数的特例）。核心价值在于**保持引用稳定**，配合 `memo` 阻止不必要的子组件重渲染。

## useContext：跨层级共享数据 {#usecontext}

`useContext` 让数据**跨越多层组件**传递，避免层层 props 透传（prop drilling）。

```jsx
import { createContext, useContext, useState } from 'react';

// 1. 创建 Context
const ThemeContext = createContext('light');

// 2. 在顶层用 Provider 提供值
function App() {
  const [theme, setTheme] = useState('light');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Page />
    </ThemeContext.Provider>
  );
}

// 3. 任意深度的子组件直接消费
function ThemedButton() {
  const { theme, setTheme } = useContext(ThemeContext);
  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      当前主题：{theme}
    </button>
  );
}
```

> [!TIP]
> Context 适合「全局但变化不频繁」的数据：主题、语言、当前登录用户。**不要**用 Context 传递高频变化的共享状态（如频繁更新的表单数据），那会引发大范围重渲染，此时更适合状态管理库（Redux/Zustand）。

## useReducer：复杂状态逻辑 {#usereducer}

当状态更新逻辑复杂、或一次更新涉及多个子状态时，`useReducer` 比一堆 `useState` 更清晰。

```jsx
import { useReducer } from 'react';

// 1. 定义 reducer：接收当前状态和动作，返回新状态
function todoReducer(state, action) {
  switch (action.type) {
    case 'add':
      return [...state, { id: Date.now(), title: action.title, done: false }];
    case 'toggle':
      return state.map(t => t.id === action.id ? { ...t, done: !t.done } : t);
    case 'remove':
      return state.filter(t => t.id !== action.id);
    default:
      return state;
  }
}

function TodoApp() {
  const [todos, dispatch] = useReducer(todoReducer, []);

  function addTodo(e) {
    e.preventDefault();
    const title = e.target.elements.todo.value;
    dispatch({ type: 'add', title });   // 派发动作
  }

  return (
    <div>
      <form onSubmit={addTodo}>
        <input name="todo" />
        <button>添加</button>
      </form>
      <ul>
        {todos.map(t => (
          <li key={t.id}>
            <span onClick={() => dispatch({ type: 'toggle', id: t.id })}>
              {t.done ? '✅' : '⬜'} {t.title}
            </span>
            <button onClick={() => dispatch({ type: 'remove', id: t.id })}>删除</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

> [!TIP]
> 何时用 `useReducer` 而非 `useState`：①多个状态互相依赖、一起变化；②更新逻辑复杂（多种 action）；③状态结构是数组/对象且操作多样。简单独立的布尔值/字符串用 `useState` 即可。

## 自定义 Hook：复用逻辑 {#custom-hook}

把重复的「状态 + 副作用」逻辑抽成自定义 Hook，是 React 最强大的复用手段。

```jsx
// 1. 自定义 Hook：useLocalStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// 2. 使用
function App() {
  const [name, setName] = useLocalStorage('name', '匿名');
  return (
    <input value={name} onChange={e => setName(e.target.value)} />
  );
}
```

再一个常用例子——防抖输入：

```jsx
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);   // 每次变化都重置计时
  }, [value, delay]);

  return debounced;
}

// 搜索框：输入停顿 300ms 后才真正搜索
function Search() {
  const [keyword, setKeyword] = useState('');
  const debounced = useDebounce(keyword, 300);

  useEffect(() => {
    if (debounced) fetchResults(debounced);
  }, [debounced]);

  return <input value={keyword} onChange={e => setKeyword(e.target.value)} />;
}
```

> [!NOTE]
> 自定义 Hook 的命名必须以 `use` 开头（否则 React 不把它当 Hook 处理）。它内部可以使用其他 Hook，本质是把「组件里可复用的状态逻辑」提取成函数。

## Hooks 使用规则 {#rules}

两条铁律（违反会导致状态错乱）：

1. **只在顶层调用**——不要在条件、循环、嵌套函数里调用 Hook。
2. **只在 React 函数中调用**——函数组件或自定义 Hook 内，不要在普通 JS 函数里调用。

```jsx
// ❌ 条件调用 Hook（违反规则）
if (someCondition) {
  const [x, setX] = useState(0);
}

// ✅ 把条件放进 Hook 内部
const [x, setX] = useState(someCondition ? 0 : 1);
```

> [!TIP]
> React 靠「Hook 的调用顺序」来关联状态，条件调用会打乱顺序导致状态错位。这也是为什么要把条件逻辑放在 Hook 内部，而不是用它包裹 Hook 调用。

## 小结 {#summary}

本章详解了六个高频 Hook 及自定义 Hook：`useRef`（DOM 引用 + 可变值）、`useMemo`（缓存计算）、`useCallback`（缓存函数配合 memo）、`useContext`（跨层共享）、`useReducer`（复杂状态）、自定义 Hook（复用逻辑），并强调了「只在顶层调用」的铁律。这些 Hooks 组合起来能覆盖绝大多数日常开发场景。下一章进入进阶主题与 React 19 新特性。
