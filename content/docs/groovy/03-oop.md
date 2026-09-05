---
title: 第三章 面向对象
linkTitle: 面向对象
description: Groovy 的类、trait、POGO 与运算符重载
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

## 小结 {#summary}

Groovy 的面向对象在 Java 之上大幅减少了样板代码，trait 提供了灵活的组合能力，运算符重载与静态编译则兼顾了表达力与性能。下一章探索元编程与 AST 转换等高级特性。
