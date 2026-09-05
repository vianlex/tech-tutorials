---
title: 第四章 元编程与高级特性
linkTitle: 元编程与高级特性
description: ExpandoMetaClass、MOP、AST 转换注解、XML/JSON 处理与反序列化注意点
weight: 84
---

# 元编程与高级特性

## ExpandoMetaClass {#expando}

通过 `metaClass` 可在运行时为类动态添加方法、属性：

```groovy
// 为 String 动态添加一个 swapCase 方法
String.metaClass.swapCase = {
    delegate.collect {
        it.isUpperCase() ? it.toLowerCase() : it.toUpperCase()
    }.join("")
}

println "Groovy".swapCase()    // gROOVY

// 也可只给某个实例添加（不影响类本身）
def s = "hi"
s.metaClass.shout = { "!!!$delegate!!!" }
println s.shout()              // !!!hi!!!

// 全局启用 ExpandoMetaClass
ExpandoMetaClass.enableGlobally()
```

**重要注意点（高频坑）**：

- **线程安全**：`metaClass` 修改是**全局生效**的，多线程下对同一个类的 `metaClass` 并发修改需要同步；且一旦改了 JDK 核心类（如 `String`），会影响整个 JVM 中所有使用该类的地方——在库代码里修改核心类 `metaClass` 极其危险，会污染所有使用者。
- **性能开销**：每次方法调用都要经过 MOP 查找，比静态编译/普通调用慢；大量使用动态元类会明显拖累性能。
- **与 `@CompileStatic` 冲突**：静态编译后调用在编译期就绑定了目标，运行时 `metaClass` 注入的方法根本不会被找到。
- **`enableGlobally()` 的副作用**：它允许给**任何**类（包括 JDK 类）追加方法，但也会让某些原本会抛 `MissingMethodException` 的地方变成"静默新增"。建议在应用启动早期一次性完成注入，避免在请求处理中途动态修改。
- 替代方案：若只是给"自己的类"加行为，优先考虑 `trait` 或 `@Category`/`@Mixin`，比污染全局 `metaClass` 更安全可控。

## methodMissing 与 propertyMissing {#missing}

拦截不存在的方法/属性调用，实现动态行为：

```groovy
class Dynamic {
    def methodMissing(String name, def args) {
        "你调用了不存在的方法 $name，参数：${args}"
    }
    def propertyMissing(String name) {
        "读取了动态属性 $name"
    }
}

def d = new Dynamic()
println d.foo(1, 2)        // 你调用了不存在的方法 foo，参数：[1, 2]
println d.bar              // 读取了动态属性 bar
```

**实际应用场景**：

- **动态 API 客户端 / 动态代理**：把方法名映射成 HTTP 请求，例如 `client.users.list()` 自动转成 `GET /users`。
- **DSL 兜底**：未知属性/方法返回合理的默认值（如配置对象、查询构造器）。
- 常见套路是 `methodMissing` 里**动态生成并缓存真实方法**（用 `metaClass."$name" = {...}`），这样下次调用直接命中缓存、不再走 `methodMissing`，兼顾灵活与性能。

```groovy
class ApiClient {
    def methodMissing(String name, args) {
        // 第一次调用时动态注册，以后直接命中
        def impl = { Object[] a -> "调用 ${name}，参数 ${a}" }
        ApiClient.metaClass."$name" = impl
        impl(args)
    }
}
```

**`respondsTo` / `hasProperty`**：在反射式调用前判断能力，避免盲目调用触发 `MissingMethodException`：

```groovy
def obj = "hello"
println obj.respondsTo("toUpperCase")   // true
println obj.respondsTo("foo")           // false
println obj.hasProperty("bytes")        // true
```

## MOP 元对象协议 {#mop}

Groovy 通过 Meta Object Protocol 统一调度方法调用，可整体替换 MetaClass：

```groovy
// 自定义 MetaClass 拦截调用
class TraceMetaClass extends groovy.lang.DelegatingMetaClass {
    TraceMetaClass(Class cls) { super(cls) }
    Object invokeMethod(Object obj, String name, Object[] args) {
        println "调用方法: $name"
        return super.invokeMethod(obj, name, args)
    }
}

// 注册到全局元类注册表
def registry = groovy.lang.MetaClassRegistryHolder.getMetaClassRegistry()
// 通过 groovy.lang.MetaClassRegistry 可绑定自定义 MetaClass
```

说明：`MOP` 是 Groovy 动态能力的底层机制。日常开发一般**不直接写 `DelegatingMetaClass`**，而是用 `metaClass` 快捷语法或 AST 转换；只有在需要全局统一拦截/埋点/审计时才下沉到 MOP 层。

## AST 转换注解 {#ast}

AST 转换（编译期字节码改写）能自动生成大量样板代码：

```groovy
import groovy.transform.*

@ToString
@EqualsAndHashCode
@TupleConstructor
@Sortable                       // 生成 Comparable
class User {
    String name
    int age
}

def u1 = new User("Alice", 25)
def u2 = new User("Bob", 30)
println u1 <=> u2               // 按 age 比较：-1
```

## 更多常用 AST 注解 {#ast-list}

| 注解 | 作用 | 注意点 |
|------|------|--------|
| `@Delegate` | 将某字段的方法委托出去 | 存在同名方法时可能产生冲突/覆盖 |
| `@Immutable` | 生成不可变对象 | 集合字段会被防御性拷贝 |
| `@Canonical` | toString/equals/hashCode 一体 | = ToString+EqualsAndHashCode+TupleConstructor |
| `@TupleConstructor` | 顺序构造器 | 默认要求所有字段参与 |
| `@Memoized` | 方法结果缓存 | 默认无界缓存；**线程安全但仅限纯函数** |
| `@Singleton` | 单例 | `lazy=true` 才线程安全 |
| `@Synchronized` | 方法同步锁 | 锁在私有字段上（比 `synchronized` 方法更细粒度） |
| `@Builder` | 建造者模式 | 默认值处理需小心（见第三章） |
| `@WithReadLock` / `@WithWriteLock` | 读写锁包裹方法 | 需要 `@CompileStatic` 或字段存在；基于 `ReentrantReadWriteLock` |
| `@Newify` | 允许 `new` 省略或 `Foo[...]`/`Foo(...)` 构造语法糖 | 提升 DSL 可读性 |
| `@AutoImplement` | 自动实现接口/抽象类 | 用 `Closure` 或默认实现兜底未实现方法 |

补充几个实战高频点：

- **`@Memoized` 的线程安全**：方法本身线程安全（内部用 `ConcurrentHashMap` 缓存），但**缓存会无限增长**（除非用 `maxCacheSize`）；且**被缓存的方法必须是无副作用的纯函数**，否则并发下读到陈旧结果会很难排查。
- **`@Synchronized`**：锁对象是一个自动生成的 `private` 字段（而非 `this`），避免了外部代码用同一对象当锁导致的死锁，比 Java 的 `synchronized` 方法更优。
- **`@WithReadLock`/`@WithWriteLock`**：适合读多写少的共享状态，需配合 `@CompileStatic` 或确保字段存在；写锁会互斥所有读写。

## 自定义 AST 转换（一句话定位） {#custom-ast}

若内置 AST 注解仍不满足，可实现 `@GroovyASTTransformation`（实现 `ASTTransformation` 接口，在编译期直接修改抽象语法树）来编写自己的编译期转换。它属于"进阶扩展点"，多数业务开发用内置注解即可，这里仅作定位，不展开实现细节。

## GPath 表达式 {#gpath}

GPath 用点路径从嵌套结构中快速抽取数据：

```groovy
def data = [
    people: [
        [name: "Alice", age: 25],
        [name: "Bob", age: 17],
        [name: "Carol", age: 30]
    ]
]

// 直接沿路径取值，无需层层判空
def adults = data.people.findAll { it.age >= 18 }
println adults.name           // [Alice, Carol]（属性投影）
```

补充：`*.` 展开运算符在 GPath 投影里同样适用——`list*.name` 等价于 `list.collect { it.name }`，是处理嵌套 List/Map 的利器。

## XML 处理 {#xml}

`XmlSlurper` 与 `XmlParser` 支持 GPath 风格解析：

```groovy
def xml = '''
<library>
  <book title="Groovy 入门"><author>Bob</author></book>
  <book title="Java 进阶"><author>Carol</author></book>
</library>
'''

def lib = new XmlSlurper().parseText(xml)
lib.book.each {
    println "${it.@title} / ${it.author}"   // 属性用 @，子节点直接访问
}
```

**`XmlSlurper` vs `XmlParser` 的核心区别**（重要选择依据）：

| 特性 | `XmlSlurper` | `XmlParser` |
|------|--------------|-------------|
| 加载方式 | 懒加载（按需解析） | 一次性构建完整 DOM |
| 是否可写回 | 否（只读） | 是（可修改后序列化回 XML） |
| 内存占用 | 较低（大文件友好） | 较高 |
| 命名空间 | 默认宽松处理 | 需显式处理命名空间 |
| 适用场景 | 读取/抽取数据 | 需要增删改并重新生成 XML |

另外，`MarkupBuilder` 用于**生成** XML：

```groovy
def sw = new StringWriter()
def xml = new groovy.xml.MarkupBuilder(sw)
xml.library {
    book(title: "Groovy 入门") {
        author("Bob")
    }
}
println sw.toString()
// <library><book title='Groovy 入门'><author>Bob</author></book></library>
```

## JSON 处理 {#json}

`JsonSlurper` 解析、`JsonOutput` 输出，与 Groovy 对象无缝互转：

```groovy
import groovy.json.*

def text = '{"name":"Alice","age":25,"tags":["a","b"]}'
def obj = new JsonSlurper().parseText(text)
println obj.name              // Alice（直接映射为 Map）
println obj.tags[0]           // a

// 序列化
def out = JsonOutput.toJson([name: "Bob", age: 30])
println JsonOutput.prettyPrint(out)   // 美化输出
```

**重要细节（高频坑）**：

- **`JsonSlurper` 返回的类型**：默认解析为 `LazyMap` / `ArrayList`（惰性求值的 map/list 实现），**不是** `LinkedHashMap`/`ArrayList`。这在大多数情况下透明可用，但若你依赖具体实现类（如 `instanceof LinkedHashMap`、或放进需要 `Serializable` 的上下文）会出问题——需要时显式转换：`(Map) new JsonSlurper().parseText(text)` 或构造时指定 `type=JsonParserType.CHAR_BUFFER` 等得到常规类型。
- **JSON 与对象的转换**：用 `JsonSlurperClassic` 的解析结果赋值给强类型类，可借助 `new JsonSlurper().parseText(text) as MyClass`（需类有无参构造 + 字段匹配，或用 `@ToString`/`@Canonical`）。反向用 `JsonOutput`。也可用 `JsonSlurper` + `Map` 后手动装配。
- **`JsonBuilder` / `StreamingJsonBuilder` 生成 JSON**：

```groovy
def builder = new groovy.json.JsonBuilder()
builder.person {
    name "Alice"
    age 25
    tags "a", "b"
}
println builder.toString()
```

`StreamingJsonBuilder` 适合**流式、大体积** JSON 写出（边写边输出，内存友好）。

- **`JsonSlurper` 解析大文件的内存坑**：`parseText` 会把整个 JSON 读入内存并构建成嵌套对象，超大 JSON（数百 MB）会 OOM；应使用 `new JsonSlurper().parse(new File(...))` 配合 `JsonParserType.CHAR_BUFFER`（流式解析），或改用 `JsonSlurperClassic` + 逐段读取，必要时切分文件。

## 小结 {#summary}

元编程让 Groovy 能在运行时/编译期灵活扩展行为，但 `metaClass` 的全局污染与性能开销、`@CompileStatic` 与动态的互斥、JSON 解析返回的惰性类型与安全反序列化，都是工程化时必须警惕的边界；配合 GPath、XML/JSON 处理，Groovy 在数据解析与 DSL 上几乎无对手。最后一章把这些特性落到真实工程：Gradle、Jenkins、Spock 与脚本嵌入。
