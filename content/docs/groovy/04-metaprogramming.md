---
title: 第四章 元编程与高级特性
linkTitle: 元编程与高级特性
description: ExpandoMetaClass、MOP、AST 转换与 XML/JSON 处理
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

## 常用 AST 注解 {#ast-list}

| 注解 | 作用 |
|------|------|
| `@Delegate` | 将某字段的方法委托出去 |
| `@Immutable` | 生成不可变对象 |
| `@Canonical` | toString/equals/hashCode 一体 |
| `@TupleConstructor` | 顺序构造器 |
| `@Memoized` | 方法结果缓存 |
| `@Singleton` | 单例 |
| `@Synchronized` | 方法同步锁 |
| `@Builder` | 建造者模式 |

## @Delegate 委托 {#delegate-ast}

把被委托对象的方法"提升"到当前类：

```groovy
import groovy.transform.Delegate

class Employee {
    @Delegate Date hireDate = new Date()   // 直接拥有 Date 的方法
    String name

    // 现在 employee.format(...) 等 Date 方法可直接使用
}

def e = new Employee(name: "Alice")
println e.time                // 委托调用 Date.time
```

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

## 小结 {#summary}

元编程与 AST 转换是 Groovy 的精华，让你用极少的代码获得强大的扩展与自动化能力，GPath 与 XML/JSON 处理则让数据解析异常顺手。最后一章将把这些特性应用到真实工程场景。
