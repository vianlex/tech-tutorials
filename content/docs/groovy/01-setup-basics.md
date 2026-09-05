---
title: 第一章 环境搭建与基础语法
linkTitle: 基础语法
description: Groovy 安装、变量、类型、GString
weight: 81
---

# 环境搭建与基础语法

## 安装 Groovy {#install}

推荐使用 SDKMAN 管理多版本 JDK 与 Groovy：

```bash
# 安装 SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# 安装 Groovy（以 4.x 为例）
sdk install groovy 4.0.22

# 验证安装
groovy --version
```

也可通过 macOS Homebrew 安装：`brew install groovy`。Groovy 4 需要 JDK 8 及以上运行环境，建议搭配 JDK 17 使用。

## 交互式环境 {#console}

Groovy 自带两种 REPL 环境，方便快速试验：

```bash
groovysh          # 命令行交互式 Shell（REPL）
groovyConsole     # 图形化控制台（Swing GUI，适合学习调试）
```

`groovyConsole` 左侧写代码、右侧看输出，按 `Ctrl+R` 运行，是入门的最佳选择。

## 第一个程序 {#hello}

Groovy 代码可以直接写在脚本里运行，无需 `main` 方法：

```groovy
// hello.groovy
println "Hello, Groovy!"   // 分号可选，println 自动换行

// 也可像 Java 一样写
class Greeter {
    static void main(String[] args) {
        println "Hello from class"
    }
}
```

运行：`groovy hello.groovy`。

## 变量与定义 {#variables}

`def` 声明动态类型变量，类型在运行时推断；也可显式标注类型：

```groovy
def name = "Alice"      // 动态类型，等价于 Object
String lang = "Groovy"  // 显式静态类型（编译期检查）
int count = 3           // 基本类型也可用

// def 并非 Object 的同义词：在 @CompileStatic 下 def 仍享有类型推断
def total = count + 2
println total           // 5

// 多变量赋值
def (a, b, c) = [1, 2, 3]
```

## 类型系统 {#types}

Groovy 兼容所有 Java 类型，并自动装箱/拆箱：

```groovy
int      i = 10        // 基本类型
Integer  j = 20        // 包装类型，与 int 互通
double   d = 3.14
boolean  flag = true
String   s = '文本'

// Groovy 的 == 调用 equals()，而非引用比较（除非是同一对象）
println new String("x") == "x"   // true
println new String("x").is("x")  // false，is() 才是引用比较
```

## 运算符 {#operators}

Groovy 提供了多个 Java 没有的便捷运算符：

```groovy
def name = null

// 安全导航运算符：调用链中任一环节为 null 时整体返回 null
println name?.toUpperCase()      // null，不会抛 NPE

// Elvis 运算符：常见默认值写法
def display = name ?: "匿名用户"
println display                 // 匿名用户

// 太空船运算符（返回 -1/0/1，供 compareTo 使用）
println 3 <=> 5                  // -1

// 展开运算符：批量调用集合元素的方法
def list = ["a", "b", "c"]
println list*.toUpperCase()     // [A, B, C]

// 范围运算符
println (1..3)                  // [1, 2, 3]，闭区间
println (1..<3)                 // [1, 2]，左闭右开
```

## GString 插值 {#gstring}

双引号字符串支持 `${}` 插值，称为 GString；单引号则是纯字面量：

```groovy
def name = "Groovy"
def version = 4

// ${} 内可放任意表达式
def msg = "你好，${name} ${version}.x"   // 你好，Groovy 4.x
println msg

// 单行变量可省略花括号
def lang = "JVM"
println "运行在 ${lang} 上"             // 运行在 JVM 上

// 惰性求值：GString 在每次 toString 时才计算表达式
def items = ["a", "b"]
def s = "有 ${items.size()} 项"
items << "c"
println s                               // 有 3 项
```

## 小结 {#summary}

Groovy 的安装与交互环境非常轻量，语法在 Java 之上做了大量简化，并通过安全导航、Elvis、GString 等特性显著提升表达力。下一章将深入学习 Groovy 强大的集合与闭包。
