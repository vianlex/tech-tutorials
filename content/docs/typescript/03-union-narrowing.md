---
title: 第三章 联合、交叉与类型收窄
linkTitle: 联合、交叉与收窄
description: 联合类型与交叉类型、字面量类型、类型收窄（typeof/in/instanceof）、可辨识联合、类型断言
weight: 173
---

# 联合、交叉与类型收窄

TS 强大之处在于能把类型描述得非常**精确**。联合类型（union）表示「或」，交叉类型（intersection）表示「且」，类型收窄（narrowing）则让编译器在代码分支里自动缩小类型范围。

## 联合类型 union {#union}

用 `|` 表示「多个类型之一」：

```typescript
let id: string | number;
id = 'abc';
id = 123;
// id = true;   // ❌ 报错

// 函数参数用联合类型
function formatId(id: string | number): string {
  return String(id);
}
```

访问联合类型的成员时，只能用**所有成员共有的属性/方法**：

```typescript
function printLength(x: string | number) {
  // x.length;  // ❌ number 没有 length
  if (typeof x === 'string') {
    console.log(x.length);   // ✅ 收窄后可用
  }
}
```

## 交叉类型 intersection {#intersection}

用 `&` 表示「同时满足多个类型」：

```typescript
interface Name { name: string; }
interface Age { age: number; }

type Person = Name & Age;   // 同时有 name 和 age

const p: Person = { name: 'Alice', age: 18 };
```

## 字面量类型 {#literal-types}

类型可以是**具体的值**，配合联合类型实现「枚举式」约束：

```typescript
type Direction = 'up' | 'down' | 'left' | 'right';
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Status = 'success' | 'error' | 'pending';

let dir: Direction = 'up';
// dir = 'forward';   // ❌ 不在联合里

function request(method: HttpMethod, url: string) { /* ... */ }
request('GET', '/api/users');   // ✅
request('get', '/api/users');   // ❌ 大小写不符
```

```typescript
// 数字字面量
type Dice = 1 | 2 | 3 | 4 | 5 | 6;
```

## 类型收窄 narrowing {#narrowing}

类型收窄指：TS 根据**控制流分析**，在分支里自动缩小联合类型。它是「精确类型」的关键。

### typeof 收窄 {#typeof-narrowing}

```typescript
function padLeft(value: string | number) {
  if (typeof value === 'string') {
    return '0'.repeat(4 - value.length) + value;   // 这里是 string
  }
  return value.toFixed(2);   // 这里是 number
}
```

### in 收窄 {#in-narrowing}

用 `in` 判断对象是否有某属性：

```typescript
interface Fish { swim(): void; }
interface Bird { fly(): void; }

function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim();   // 收窄为 Fish
  } else {
    animal.fly();    // 收窄为 Bird
  }
}
```

### instanceof 收窄 {#instanceof-narrowing}

```typescript
function parseDate(input: Date | string) {
  if (input instanceof Date) {
    return input.getFullYear();   // Date
  }
  return new Date(input).getFullYear();   // string
}
```

### 真值收窄 {#truthiness-narrowing}

```typescript
function print(message?: string) {
  if (message) {
    console.log(message.toUpperCase());   // 排除了 undefined/空串
  }
}
```

> [!TIP]
> 类型收窄是 TS 的「智能」体现：你写 `if (typeof x === 'string')`，编译器就自动知道分支里 `x` 是 `string`。善用收窄，就能避免大量类型断言，写出更安全、更清晰的代码。

## 可辨识联合 discriminated union {#discriminated-union}

这是**最强大的类型建模模式**：给联合类型的每个成员加一个共同的「判别属性」（通常是字面量类型的 `type`/`kind`），TS 就能精确收窄。

```typescript
// 三种状态，用 type 字段判别
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'square'; size: number }
  | { kind: 'rectangle'; width: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;        // 这里能访问 radius
    case 'square':
      return shape.size ** 2;                    // 这里能访问 size
    case 'rectangle':
      return shape.width * shape.height;         // 这里能访问 width/height
  }
}
```

> [!NOTE]
> 可辨识联合是「前端状态机、Redux action、API 响应」等的标准建模方式。核心技巧：①每个成员有唯一的 `kind` 判别字段；②用 `switch`/`if` 收窄；③TS 保证每个分支里只暴露对应成员的类型（不会误访问其他成员的属性）。

### 结合 switch 穷尽检查 {#exhaustive-check}

```typescript
function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'square': return shape.size ** 2;
    case 'rectangle': return shape.width * shape.height;
    default: {
      // 穷尽检查：若漏了某个 case，这里会编译报错
      const _exhaustive: never = shape;
      return _exhaustive;
    }
  }
}
```

## 类型断言 type assertion {#assertion}

当你比编译器更确定类型时，用 `as` 断言：

```typescript
// 从 DOM 拿元素，TS 只知道是 HTMLElement
const canvas = document.getElementById('canvas') as HTMLCanvasElement;
canvas.getContext('2d');
```

```typescript
// 双重断言（慎用，any 的变体）
const value = (someValue as unknown) as string;
```

> [!WARNING]
> 类型断言**不是类型转换**，它只告诉编译器「相信我」，运行时不做任何事。断言错误会导致运行时 bug。**能收窄就收窄，尽量少用断言**。`as unknown as X` 双重断言尤其危险，只在极少数跨边界场景（如对接第三方库）使用。

## 非空断言 ! {#non-null-assertion}

`!` 告诉编译器「这个值一定不是 null/undefined」：

```typescript
function getValue(): string | undefined {
  return Math.random() > 0.5 ? 'x' : undefined;
}

const v = getValue()!;   // 断言非空
console.log(v.toUpperCase());
```

> [!TIP]
> `!` 应谨慎使用——它「绕过」了空值检查。优先用可选链 `?.` 和空值合并 `??` 安全处理：

```typescript
const v = getValue();
console.log(v?.toUpperCase() ?? '默认值');
```

## 小结 {#summary}

本章掌握了让类型「精确」的三板斧：联合类型（`|`）、交叉类型（`&`）、字面量类型，以及 TS 的智能类型收窄（`typeof`/`in`/`instanceof`/真值），重点是可辨识联合这一强大建模模式。类型断言（`as`）和非空断言（`!`）是「逃生舱」，能不用就不用。下一章学习泛型与工具类型——让类型「复用」起来。
