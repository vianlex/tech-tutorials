---
title: 第二章 接口与类型别名
linkTitle: 接口与类型别名
description: interface 与 type 的区别与选择、可选属性、只读属性、函数类型、索引签名、接口继承与交叉
weight: 172
---

# 接口与类型别名

TypeScript 用**接口（interface）**和**类型别名（type alias）**来定义「对象的形状」。两者大部分场景可互换，但有微妙区别。理解它们，才能写出清晰的类型定义。

## interface 接口 {#interface}

接口描述对象的**结构**——有哪些属性、什么类型：

```typescript
interface User {
  name: string;
  age: number;
  email?: string;          // 可选属性
}

const alice: User = { name: 'Alice', age: 18 };           // ✅ email 可省略
const bob: User = { name: 'Bob', age: 20, email: 'b@x.com' };
```

### 可选属性 {#optional}

用 `?` 标记可选，访问时类型为 `类型 | undefined`：

```typescript
interface Config {
  url: string;
  timeout?: number;   // 可选
}

function init(cfg: Config) {
  // 访问可选属性需要处理 undefined
  const t = cfg.timeout ?? 3000;
}
```

### 只读属性 {#readonly}

`readonly` 标记的属性只能在创建时赋值，之后不可修改：

```typescript
interface Point {
  readonly x: number;
  readonly y: number;
}

const p: Point = { x: 1, y: 2 };
// p.x = 3;   // ❌ 报错：Cannot assign to 'x' because it is a read-only property
```

> [!NOTE]
> `readonly` 是**编译期**约束，运行时并不冻结。它适用于「创建后不应改变」的字段（如 id、创建时间）。需要真冻结用 `Object.freeze`。也可用 `Readonly<T>` 工具类型整体只读（见第四章）。

### 函数类型 {#function-signature}

接口可以描述函数（含参数和返回值）：

```typescript
interface AddFn {
  (a: number, b: number): number;   // 调用签名
}

const add: AddFn = (a, b) => a + b;
```

函数类型的另一种写法（更常见）：

```typescript
// 类型别名描述函数
type Add = (a: number, b: number) => number;

// 或内联标注
function add(a: number, b: number): number { return a + b; }
```

### 索引签名 {#index-signature}

描述「拥有任意数量的某类型键」的对象（如字典、配置映射）：

```typescript
interface Dictionary {
  [key: string]: string;   // 任意字符串键，值为 string
}

const dict: Dictionary = {
  name: 'Alice',
  city: '北京',
};

// 数字索引签名（数组-like）
interface StringArray {
  [index: number]: string;
}
```

## type 类型别名 {#type-alias}

`type` 给类型起别名，可表示**任何类型**（不仅对象）：

```typescript
type ID = string | number;              // 联合类型别名
type Point = { x: number; y: number };  // 对象类型
type Callback = (data: string) => void; // 函数类型
type Tuple = [string, number];          // 元组
```

## interface vs type 的区别 {#interface-vs-type}

这是高频面试题，也是日常选择的关键：

| 维度 | interface | type |
|------|-----------|------|
| 声明合并 | ✓ 同名自动合并 | ✗ 重复报错 |
| 继承 | `extends` | `&`（交叉） |
| 可表示的类型 | 对象/函数 | **任意**（联合、元组、字面量等） |
| 扩展第三方库 | ✓ 适合 | 较难 |

### 1. 声明合并（interface 独有） {#declaration-merging}

```typescript
interface User {
  name: string;
}
interface User {   // 同名接口会合并
  age: number;
}

const u: User = { name: 'Alice', age: 18 };   // 两个属性都有
```

### 2. 继承与交叉 {#extend-intersect}

```typescript
// interface 用 extends
interface Animal { name: string; }
interface Dog extends Animal { bark(): void; }

// type 用交叉 &
type Animal2 = { name: string };
type Dog2 = Animal2 & { bark(): void };
```

> [!TIP]
> **选择建议**：
> - 定义**对象形状**、需要**扩展/合并** → 用 `interface`。
> - 定义**联合类型、元组、函数签名**等非对象类型 → 用 `type`。
> - 团队统一约定一个优先即可（很多团队「默认 interface，特殊用 type」）。关键是一致性，不必纠结。

## 接口的继承与组合 {#extend}

```typescript
interface Person {
  name: string;
}

interface Employee extends Person {
  id: number;
  department: string;
}

const emp: Employee = { name: 'Alice', id: 1, department: '工程部' };

// 继承多个接口
interface Manager extends Person, Employee {
  level: number;
}
```

## 描述可复用的类型 {#reusable}

```typescript
// 通用 API 响应类型（常用写法）
interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface User { id: number; name: string; }
type UserResponse = ApiResponse<User>;

async function fetchUser(): Promise<UserResponse> {
  // ...
  return { code: 0, message: 'ok', data: { id: 1, name: 'Alice' } };
}
```

## 小结 {#summary}

本章掌握了 TS 的两大类型定义工具：`interface`（可选属性、只读、函数签名、索引签名、继承、声明合并）和 `type`（可表示任意类型）。核心区别：**interface 可声明合并、适合对象与扩展；type 更灵活、可表示联合/元组**。选择时以团队一致性和场景为准。下一章学习联合类型与类型收窄——这是让类型「精确」的关键。
