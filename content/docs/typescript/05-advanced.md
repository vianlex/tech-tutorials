---
title: 第五章 高级类型与工程实践
linkTitle: 高级类型与工程实践
description: keyof 与索引访问、映射类型、条件类型、枚举、类、tsconfig 配置与最佳实践
weight: 176
---

# 高级类型与工程实践

这一章进入 TS 的高级类型特性——`keyof`、映射类型、条件类型，它们是理解工具类型底层原理、写出「类型体操」的基础。最后落到工程实践：枚举、类、`tsconfig` 配置与最佳实践。

## keyof 与索引访问类型 {#keyof}

### keyof：取所有键名 {#keyof-operator}

```typescript
interface User {
  name: string;
  age: number;
  email: string;
}

type UserKeys = keyof User;   // "name" | "age" | "email"
```

### 索引访问类型 T[K] {#indexed-access}

```typescript
type NameType = User['name'];   // string
type AgeType = User['age'];     // number

// 组合：遍历所有键，取对应值类型
type UserValues = User[keyof User];   // string | number
```

## 映射类型 mapped types {#mapped-types}

映射类型「遍历」一个类型的所有键，生成新类型。它是工具类型的底层实现：

```typescript
// 基础语法：{ [K in 键集合]: 值类型 }
type Readonly2<T> = { readonly [K in keyof T]: T[K] };
type Partial2<T> = { [K in keyof T]?: T[K] };

interface User { name: string; age: number; }
type ReadonlyUser = Readonly2<User>;
// { readonly name: string; readonly age: number }
```

```typescript
// 用 as 重映射键名
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User { name: string; age: number; }
type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number }
```

> [!NOTE]
> 映射类型是 TS「类型体操」的核心工具：`keyof` 取键、`[K in ...]` 遍历、`as` 重映射键名、`T[K]` 取值类型。`Partial`/`Readonly`/`Pick`/`Record` 等内置工具类型，本质上都是映射类型的特例。

## 条件类型 conditional types {#conditional-types}

条件类型像「类型层面的三元表达式」：`T extends U ? X : Y`。

```typescript
// 判断 T 是否为 string
type IsString<T> = T extends string ? 'yes' : 'no';

type A = IsString<string>;   // 'yes'
type B = IsString<number>;   // 'no'
```

### 分布式条件类型 {#distributive}

当 `T` 是**裸类型参数**且为联合类型时，条件类型会**分发**到每个成员：

```typescript
type ToArray<T> = T extends any ? T[] : never;

type Result = ToArray<string | number>;
// string[] | number[]（分发到每个成员，而非 (string|number)[]）
```

### 实战：提取函数返回值 {#infer}

用 `infer` 在条件类型中「推断」类型：

```typescript
// 自己实现 ReturnType
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function getUser() { return { id: 1, name: 'Alice' }; }
type User = MyReturnType<typeof getUser>;   // { id: number; name: string }
```

```typescript
// 提取 Promise 的 resolve 类型（常用）
type Awaited2<T> = T extends Promise<infer U> ? U : T;

type Result = Awaited2<Promise<string>>;   // string
```

> [!TIP]
> 条件类型 + `infer` 是「从类型中提取信息」的利器，`ReturnType`、`Awaited`、`Parameters` 等工具类型都基于它实现。理解了它，就能读懂甚至自定义复杂类型工具。

## 枚举 enum {#enum}

枚举定义一组**命名常量**：

```typescript
// 数字枚举（默认从 0 递增）
enum Direction {
  Up,     // 0
  Down,   // 1
  Left,   // 2
  Right,  // 3
}

// 字符串枚举（更常用、可读性好）
enum Status {
  Success = 'success',
  Error = 'error',
  Pending = 'pending',
}

let s: Status = Status.Success;
```

```typescript
// 反向映射（数字枚举特有）
Direction[0];   // "Up"
```

> [!WARNING]
> `enum` 有运行时开销（会生成真实对象）且存在一些历史坑（如 `const enum` 的隔离问题）。现代很多团队**用「字面量联合类型 + const 对象」替代枚举**：

```typescript
// 替代方案（推荐）：联合类型 + as const
const Status = {
  Success: 'success',
  Error: 'error',
  Pending: 'pending',
} as const;

type Status = typeof Status[keyof typeof Status];  // 'success' | 'error' | 'pending'
```

## 类 class {#class}

TS 为 class 增加了访问修饰符、抽象类、接口实现：

```typescript
class Animal {
  public name: string;      // 默认 public
  private age: number;      // 私有，仅类内可访问
  protected weight: number; // 受保护，子类可访问
  readonly id: number;      // 只读

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
    this.id = Math.random();
  }
}

// 参数属性：构造函数参数直接声明并赋值（简写）
class Person {
  constructor(public name: string, private age: number) {}
}

// 抽象类
abstract class Shape {
  abstract area(): number;   // 子类必须实现
}

class Circle extends Shape {
  constructor(private radius: number) { super(); }
  area() { return Math.PI * this.radius ** 2; }
}
```

> [!NOTE]
> `private`/`public`/`protected` 是 TS 的**编译期**访问控制（运行时仍可绕过）。TS 还支持 ECMAScript 的 `#` 私有字段（真正的运行时私有）。类型相关的访问修饰符主要用于团队协作的约束与提示。

## tsconfig 关键配置 {#tsconfig}

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",          // 编译目标 JS 版本
    "module": "ESNext",          // 模块规范
    "moduleResolution": "bundler", // 模块解析策略
    "strict": true,              // 开启所有严格检查（强烈建议）
    "outDir": "./dist",          // 输出目录
    "rootDir": "./src",          // 源码目录
    "esModuleInterop": true,     // 兼容 CommonJS 导入
    "skipLibCheck": true,        // 跳过 .d.ts 检查（加速）
    "noUncheckedIndexedAccess": true, // 索引访问可能 undefined
    "exactOptionalPropertyTypes": true, // 严格可选属性
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

> [!TIP]
> **`strict: true` 是必开项**，它聚合了 `strictNullChecks`、`noImplicitAny` 等一系列严格检查，能捕获大量潜在 bug。新项目一定开 strict；老项目可渐进开启。

## 工程最佳实践 {#best-practices}

1. **优先 `strict: true`**：从一开始就严格，避免欠技术债。
2. **少用 `any`，多用 `unknown` + 收窄**：`any` 让类型检查失效。
3. **能推断就不注解**：函数参数和返回值显式标注，其余交给推断。
4. **用可辨识联合建模状态**：状态机、action、API 响应首选。
5. **善用工具类型**：`Partial`/`Pick`/`Omit`/`Record`/`ReturnType` 减少重复。
6. **`as const` 让字面量更精确**：`const obj = {...} as const` 保留字面量类型。
7. **类型守卫封装收窄逻辑**：复用 `is` 判断。
8. **团队统一风格**：`interface` vs `type`、`enum` vs 联合，约定并遵守。

```typescript
// as const 的妙用：让数组/对象变只读且字面量化
const colors = ['red', 'green', 'blue'] as const;
type Color = typeof colors[number];   // 'red' | 'green' | 'blue'
```

## 小结 {#summary}

本章完成了 TS 高级类型与工程实践的学习：`keyof` 与索引访问、映射类型（工具类型的底层）、条件类型与 `infer`（提取类型的利器）、枚举与类，以及 `tsconfig` 配置和最佳实践。至此五章教程结束，从基础类型、结构化类型检查，到泛型、工具类型、高级类型，覆盖了现代 TypeScript 开发的核心知识体系。记住贯穿全篇的一条主线：**TS 是结构化类型检查，它关心「形状」而非「名字」**。
