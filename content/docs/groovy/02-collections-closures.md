---
title: 第二章 集合与闭包
linkTitle: 集合与闭包
description: Groovy 的 List/Map 与闭包机制
weight: 82
---

# 集合与闭包

## List 列表 {#list}

Groovy 的列表基于 Java 的 `ArrayList`，字面量用方括号，并支持负索引与范围切片：

```groovy
def list = [1, 2, 3, 4]        // 默认 ArrayList

// 追加元素
list << 5                      // [1, 2, 3, 4, 5]
list.add(6)

// 负索引：从末尾倒数
println list[-1]               // 6（最后一个）
println list[-2]               // 5

// 范围切片
println list[0..2]             // [1, 2, 3]

// 展开调用集合中所有元素的方法
println list*.toString()       // ["1","2",...]
```

## Map 映射 {#map}

Map 字面量使用键值对，默认基于 `LinkedHashMap`：

```groovy
def map = [name: "Alice", age: 25, city: "Beijing"]

// 两种取值方式
println map.name               // Alice
println map["age"]             // 25

// 写入
map.email = "alice@example.com"
map["age"] = 26

// 键若用变量需加括号，否则会被当作字符串字面量
def key = "score"
def m2 = [(key): 90]           // key 变量的值作为键
println m2                     // [score: 90]
```

## 遍历与 each {#each}

`each` 是集合最常用的方法，接收一个闭包作为参数：

```groovy
def nums = [1, 2, 3]

// 单参数闭包：默认名为 it
nums.each { println it }

// 带索引遍历
nums.eachWithIndex { val, idx ->
    println "$idx -> $val"
}

// Map 遍历：参数是一个 Map.Entry
def m = [a: 1, b: 2]
m.each { k, v -> println "$k=$v" }
```

## 转换与过滤 {#transform}

`collect`、`findAll`、`find` 等是高阶函数，体现函数式风格：

```groovy
def nums = [1, 2, 3, 4, 5]

// collect：映射为新的集合
def squares = nums.collect { it * it }      // [1, 4, 9, 16, 25]

// findAll：过滤满足条件的元素
def evens = nums.findAll { it % 2 == 0 }    // [2, 4]

// find：取第一个满足条件的元素
def firstBig = nums.find { it > 3 }         // 4

// any / every：存在 / 全部判定
println nums.any { it > 4 }                 // true
println nums.every { it > 0 }               // true
```

## 聚合与分组 {#aggregate}

```groovy
def nums = [1, 2, 3, 4]

// inject：折叠（累加），初始值为 0
def sum = nums.inject(0) { acc, n -> acc + n }   // 10

// groupBy：按条件分组
def words = ["apple", "bat", "banana", "cat"]
def byLen = words.groupBy { it.size() }
// [5:[apple], 3:[bat, cat], 6:[banana]]

// 排序与去重
println nums.sort()              // 原地排序
println [3, 1, 3, 2].unique()   // [3, 1, 2]
println nums.max()               // 4
```

## 闭包语法 {#closure}

闭包是 `{ }` 包裹的代码块，本质是可赋值、可传递的对象：

```groovy
// 单参数：默认名 it
def greet = { "Hello, $it" }
println greet("Alice")           // Hello, Alice

// 显式声明参数
def add = { a, b -> a + b }
println add(2, 3)               // 5

// 默认参数
def repeat = { s, n = 2 -> s * n }
println repeat("ab")            // abab

// 闭包可赋值给变量并作为方法参数传递
def list = [1, 2, 3]
def doubler = { it * 2 }
println list.collect(doubler)   // [2, 4, 6]
```

## 闭包委托 {#delegate}

闭包有 `this`、`owner`、`delegate` 三个作用域，常用于 DSL 设计：

```groovy
class Person {
    String name
    void say(String s) { println "$name 说: $s" }
}

def p = new Person(name: "Bob")
def c = {
    say("你好")        // 通过 delegate 调用 Person 的方法
}
c.delegate = p       // 设置委托对象
c()                  // Bob 说: 你好
```

## 方法引用 {#method-reference}

Groovy 4 支持 Java 风格的方法引用，也保留了 `&` 方法指针：

```groovy
def names = ["alice", "bob"]

// Groovy 4 方法引用：类型::方法
println names.collect(String::toUpperCase)   // [ALICE, BOB]

// 方法指针：对象.&方法（兼容旧版本）
def upper = String::toUpperCase
println names.collect(upper)

// 实例方法指针作为参数
def words = ["a", "bb", "ccc"]
def len = words.collect(this.&lengthOf)
def lengthOf(s) { s.length() }
// [1, 2, 3]
```

## 小结 {#summary}

集合配合闭包让 Groovy 处理数据异常简洁，高阶函数取代了大部分手写循环。下一章进入面向对象，了解类、trait 与运算符重载等特性。
