---
title: 第三章 面向对象
linkTitle: 面向对象
description: Groovy 的类、属性机制、常用 AST 注解、方法指针与静态编译的取舍
weight: 83
---

# 面向对象

## 类与 POGO {#class}

Groovy 的类（POGO，Plain Old Groovy Object）会自动生成字段的 getter/setter，并支持命名参数构造：

```groovy
class Person {
    String name
    int age
}

// 自动属性访问，无需手写 getter/setter
def p = new Person(name: "Alice", age: 25)
println p.name            // Alice
p.age = 26               // 实际调用 setter

// 也可像 Java 一样写构造器
class Point {
    int x, y
    Point(int x, int y) { this.x = x; this.y = y }
}
```

## 属性（property）机制 {#property}

理解 Groovy 的"字段"与"属性"差异，是写好 Groovy 类的关键：

- **未加访问修饰符的字段就是 property**：Groovy 自动生成 `private` 字段 + `public` getter/setter，`p.name` 实际调 `getName()`。
- **`public` 字段**：不会生成 getter/setter，直接是公开字段（不推荐，失去封装）。
- **`private`/`protected` 字段**：只是普通字段，没有自动 getter；从外部 `obj.field` 会报 `MissingPropertyException`，除非有自定义 getter。
- `@PackageScope`：把自动生成的 getter/setter 或字段限制在包内可见，适合"内部字段但不想暴露 setter"的场景。

```groovy
import groovy.transform.PackageScope

class Account {
    String id                      // property：有 getId()/setId()
    @PackageScope String secret    // 包内可见字段，不生成 public getter
    private BigDecimal balance     // 私有字段，外部无法直接访问

    BigDecimal getBalance() { balance.setScale(2) }  // 自定义 getter 控制返回形态
}

def a = new Account(id: "A1")
a.id = "A2"                 // 调 setId(...)
println a.id                // A2
// a.secret = "x"          // 包外编译报错
// a.balance = 10          // 报错：无 setBalance
```

坑点：`p.name = x` 永远调 setter（即使你以为在直接赋值字段）；这意味着**在 setter 里调用 `this.name = ...` 会无限递归**——应写 `this.@name = ...`（用 `@` 强制访问字段）或在 setter 里直接写底层字段。

```groovy
class Box {
    String name
    void setName(String n) {
        // this.name = n  // 错误：递归调用 setName
        this.@name = n    // 正确：直接写字段
    }
}
```

## 构造器与不可变对象 {#constructors}

通过 AST 注解可自动生成多种构造器：

```groovy
import groovy.transform.*

@TupleConstructor          // 按字段顺序生成构造器
@Canonical                 // 同时生成 toString/equals/hashCode
class Book {
    String title
    String author
}

def b = new Book("Groovy 入门", "Bob")   // 顺序构造
println b.toString()                     // Book(Groovy 入门, Bob)

@Immutable               // 生成不可变对象（字段 final）
class Config {
    String host
    int port
}
def c = new Config("localhost", 8080)
// c.host = "x"  // 报错：不可变
```

## 常用 AST 注解深入 {#ast-annotations}

Groovy 的 AST 转换是"编译期生成样板代码"的武器，开发中高频使用：

### `@ToString` / `@EqualsAndHashCode` {#to-string}

```groovy
import groovy.transform.*

@ToString(excludes = 'password', includeNames = true)   // 排除敏感字段、打印字段名
@EqualsAndHashCode(includes = 'id')                     // 仅用 id 判断相等
class User {
    int id
    String name
    String password
}
def u = new User(id: 1, name: "Alice", password: "x")
println u          // User(id:1, name:Alice)
```

要点：`includeNames=true` 让 `toString` 带上字段名，调试更友好；`@EqualsAndHashCode` 默认包含**所有属性**，若类含可变字段会导致把它放进 `HashSet` 后修改字段就找不到——集合/Map 的 key 务必用不可变字段或 `@Immutable`。

### `@Canonical` {#canonical}

`@Canonical` = `@ToString` + `@EqualsAndHashCode` + `@TupleConstructor` 三合一，默认就带顺序构造器和合理的 `toString/equals/hashCode`。注意它仍受字段顺序/包含字段影响，子类需显式处理。

### `@Builder` {#builder}

建造者模式，适合多参数构造：

```groovy
import groovy.transform.builder.Builder
import groovy.transform.builder.SimpleStrategy

@Builder(builderStrategy = SimpleStrategy)
class Request {
    String url
    String method = "GET"     // 默认值
    Map headers
}
def r = new Request().url("http://x").method("POST").build()
```

**`@Builder.Default` 的坑**（Groovy 4 相关）：在 builder 里设置的字段默认值，若同时用 `@Builder`，默认值的初始化可能不被 builder 正确带入——使用 `SimpleStrategy` 或显式在 builder 方法里处理默认值更稳妥。简单场景推荐直接用命名参数构造 `new Request(url: "http://x")`，少踩坑。

### 日志注解 `@Slf4j` / `@Log4j2` / `@Log` {#logging}

```groovy
import groovy.util.logging.Slf4j

@Slf4j
class Service {
    void run() {
        log.info("启动")        // 自动注入名为 log 的日志器
    }
}
```

`@Slf4j` 注入 SLF4J（`log` 字段），`@Log4j2` 注入 Log4j2，`@Log` 注入 `java.util.logging`。无需手写 `private static final Logger log = ...`，是消除样板代码最高频的注解之一。

### `@AutoClone` / `@AutoExternalizable` {#auto-clone}

```groovy
import groovy.transform.AutoClone

@AutoClone
class Node {
    String label
    Node next      // 默认浅拷贝；要深拷贝需配合样式参数
}
```

`@AutoClone` 自动实现 `Cloneable` + `clone()`；含嵌套对象时需要指定拷贝策略（如 `@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)`）以避免共享引用。

## trait 特性 {#trait}

`trait` 是可复用、可带默认实现的接口，支持多重组合：

```groovy
trait Loggable {
    void log(String msg) {
        println "[LOG] ${new Date()} $msg"
    }
}

trait Identifiable {
    String id
}

class Service implements Loggable, Identifiable {
    void run() {
        log("服务启动，id=$id")   // 复用 trait 的默认方法
    }
}

def s = new Service(id: "svc-1")
s.run()
```

补充：`trait` 可以有状态（字段）、`abstract` 方法（强制实现类提供）、`static` 方法，还能用 `trait T implements I` 实现接口。多个 trait 方法冲突时需显式 `override`。它是比继承更灵活的"Mixin"方案。

## 运算符重载 {#operators}

通过实现特定方法名即可重载运算符：

```groovy
class Vector {
    int x, y
    Vector plus(Vector v) { new Vector(x: x + v.x, y: y + v.y) }   // +
    Vector multiply(int n) { new Vector(x: x * n, y: y * n) }      // *
    Vector leftShift(int n) { new Vector(x: x << n, y: y << n) }   // <<
    int getAt(int i) { i == 0 ? x : y }                            // []
    String toString() { "($x, $y)" }
}

def a = new Vector(x: 1, y: 2)
def b = new Vector(x: 3, y: 4)
println a + b            // (4, 6)
println a * 3            // (3, 6)
println a[0]             // 1

// 常用重载方法：minus(-) compareTo(<=>) 等
```

## 常见重载方法 {#operator-methods}

| 运算符 | 对应方法 | 说明 |
|--------|----------|------|
| `+` | `plus` | 加法 |
| `-` | `minus` | 减法 |
| `*` | `multiply` | 乘法 |
| `<<` | `leftShift` | 追加 |
| `[]` | `getAt` / `putAt` | 下标读写 |
| `<=>` | `compareTo` | 比较 |
| `as` | `asType` | 类型转换 |

补充：`putAt` 用于 `obj[i] = v` 的写操作；`call` 方法让对象可像方法一样被调用（`obj()`）；实现 `Comparable`/`<=> ` 后集合的 `sort()`、`min()`/`max()` 才正确工作。

## 方法指针 `&` 的完整用法 {#method-pointer}

除了 `ClassName::method`（Groovy 4 方法引用），经典的 `&` 方法指针有多种形态：

```groovy
class Calc {
    int square(int n) { n * n }
    static int cube(int n) { n * n * n }
}

def c = new Calc()

// 1) 实例方法指针
def sq = c.&square
println [1,2,3].collect(sq)        // [1, 4, 9]

// 2) 静态方法指针
def cb = Calc.&cube
println [1,2,3].collect(cb)        // [1, 8, 27]

// 3) 构造方法引用（Groovy 4）：ClassName::new
def pts = [[1,2],[3,4]].collect(Point::new)

// 4) 自由函数的方法指针（顶层 def 方法）
def len = this.&lengthOf
def lengthOf(s) { s.length() }
```

坑点：方法指针**绑定的是方法签名**，调用时若参数类型不匹配会抛 `MissingMethodException`；实例方法指针会**捕获实例引用**，因此闭包方式 `c.&square` 比每次 `c.square(it)` 更利于复用与传参。

## `@Singleton` 的坑 {#singleton}

```groovy
import groovy.transform.Singleton

@Singleton
class Registry {
    void register(String s) { println "注册 $s" }
}
Registry.instance.register("x")    // 通过 instance 取单例
```

注意点：

- 默认 `instance` 是**非线程安全懒加载**（`lazy=false` 时类加载即创建）。若需线程安全懒加载，用 `@Singleton(lazy = true)`（内部用 holder 模式，线程安全）。
- `@Singleton` 生成的是 `private` 构造器，不允许 `new Registry()`。
- 不要在单例里持有大量可变状态用于并发场景而不加锁；单例 ≠ 线程安全容器。

## 静态编译 {#compile-static}

动态特性会带来运行时开销，关键代码可用静态编译优化：

```groovy
import groovy.transform.CompileStatic

@CompileStatic
class MathUtil {
    int square(int n) {
        return n * n        // 编译为纯 Java 字节码，无动态分发
    }
}

// @TypeChecked 仅做类型检查，仍保留动态调度
import groovy.transform.TypeChecked

@TypeChecked
def greet(String name) {
    // name.toUpperCase()  // 类型正确
    // name.foo()          // 编译报错：不存在的方法
}
```

**关键注意点（高频坑）**：

- `@CompileStatic` 下**动态特性不可用**：`metaClass` 注入、`methodMissing`/`propertyMissing`、运行时 `ExpandoMetaClass` 修改全部失效（编译期就绑定了调用目标）。
- `@TypeChecked` 比 `@CompileStatic` 温和：只检查类型，仍保留动态调度与 MOP，性能提升有限但兼容动态特性。
- 粒度可控制到**方法级别**：类整体不静态，但单个热点方法加 `@CompileStatic`，兼顾灵活与性能。
- 静态编译时 `def` 仍会被推断为具体类型（不像动态语境推断成 `Object`），类型安全更接近 Java。

实战建议：库/框架核心算法路径用 `@CompileStatic` 提速并防手误；DSL、脚本、需要动态能力的代码保持动态。

## 小结 {#summary}

Groovy 的面向对象通过 property 机制、trait 组合和 `@ToString`/`@Builder`/`@Slf4j`/`@Singleton` 等 AST 注解几乎消除了所有样板代码，方法指针与运算符重载则让 API 更自然；而 `@CompileStatic` 与动态特性的取舍，是写高性能且可维护 Groovy 代码必须掌握的平衡术。下一章探索元编程与 AST 转换等高级特性，以及 XML/JSON 处理中的隐性坑。
