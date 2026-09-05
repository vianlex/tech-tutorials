---
title: 第一章 环境搭建与基础语法
linkTitle: 基础语法
description: Groovy 安装、变量、类型、GString 以及与 Java 的关键差异与常见坑
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

Groovy 4 的重要变化：默认 GString 行为调整、引入 `RecordType`/`@RecordType` 实验特性、Parrot 解析器成为默认（支持 Java 风格的 `switch` 表达式、`var` 等）。本章示例均以 Groovy 4.x 为准。

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

注意 Groovy 脚本里的变量声明区分**脚本作用域**与 `binding`：未用 `def`/`类型` 声明的变量会进入 `binding`，可在嵌入执行（如 `GroovyShell`）时跨脚本共享，这也是一个容易混淆的点。

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

坑点：`def` 在动态（非 `@CompileStatic`）语境下是 `Object`，因此方法返回值类型会被擦除——若你写了 `def foo()` 返回 `List`，调用方拿到的是 `Object`，IDE 的自动补全和类型检查都会失效。在库代码中尽量显式标注返回类型。

## 类型系统与缺省导入 {#types}

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

**缺省导入（新手常困惑为什么不用 import 就能用 `List`/`Map`/`Date`）**：Groovy 自动导入以下包，无需手动 import：

- `java.lang.*`（默认）
- `java.util.*`（`List`、`Map`、`ArrayList`、`LinkedHashMap`、`Date` 等都在这里）
- `java.io.*`、`java.net.*`
- `groovy.lang.*`、`groovy.util.*`
- `java.math.BigDecimal`、`java.math.BigInteger`

因此直接写 `new Date()`、`List x = []`、`Map m = [:]` 都不会报"找不到符号"。

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

**`?.`、`?.()`、Elvis `?:` 的边界**：Elvis 判断的是 **Groovy truth**（是否为"真值"），而非是否为 `null`。这是高频踩坑点：

```groovy
// 以下都会走默认值分支，因为 false / "" / 0 在布尔上下文中都是 false
println (false ?: "默认")        // 默认
println ("" ?: "默认")           // 默认
println (0 ?: "默认")            // 默认

// 若你确实只想在 null 时给默认值，要显式判断 null
def x = false
println (x != null ? x : "默认") // false
```

方法级安全导航 `?.()` 同理：`obj?.method()` 在 `obj` 为 null 时返回 null 而不调用。

## Groovy truth（真值判定） {#groovy-truth}

这是 Groovy 与 Java 最大的差异之一，也是日常最易出错的地方。在 Java 中，只有 `boolean` 能用于 `if`/`while` 条件；而 Groovy 中**任意对象**都能放进布尔上下文，并按照"Groovy truth"规则求值。

| 值 | 在布尔上下文中的结果 | 说明 |
|----|----------------------|------|
| `true` / 非 0 的整数、非 0 的 `BigDecimal` | `true` | |
| `false` | `false` | |
| `null` | `false` | |
| 空字符串 `""` / `''` | `false` | **反直觉点** |
| 非空字符串 | `true` | |
| 空集合 `[]`、`[:]` | `false` | **反直觉点**：空 List/Map 是 false |
| 非空集合 | `true` | |
| `0` / `0.0` | `false` | **反直觉点** |
| `Boolean`/`java.lang.Object` 实现了 `asBoolean()` 的自定义类 | 取决于实现 | 可自定义真值规则 |

```groovy
// 反直觉示例：空集合在条件里是 false
def list = []
if (list) {
    println "有数据"
} else {
    println "空集合，进入 else"   // 会打印这一行
}

// 与 Java 对照：Java 里写 if(list) 直接编译报错（要求 boolean）
// 因此从 Java 转到 Groovy 时，常误以为空集合会被当作 true

// 自定义真值：重写 asBoolean()
class Box {
    def value
    boolean asBoolean() { value != null }
}
def b = new Box(value: null)
println b ? "有" : "无"           // 无
```

实战建议：`if (list)` 检查非空没问题，但**不要**用它来判断"列表不为 null 且非空"之外的语义；若需区分 `null` 与空集合，应显式写 `list != null && !list.isEmpty()`。

## 字符串类型全景 {#strings}

Groovy 提供 5 种字符串字面量，各有用途：

```groovy
// 1) 单引号：纯字面量，不支持插值，与 Java 的 "String" 行为一致
def s1 = 'Groovy 是 JVM 语言'        // 真正的 String，性能最好

// 2) 双引号：GString，支持 ${} 插值
def lang = 'Groovy'
def s2 = "Hello, ${lang}"           // Hello, Groovy

// 3) 三引号：多行字符串，保留换行与缩进，可单/双引号
def s3 = '''第一行
第二行
  第三行（缩进会保留）'''
def s4 = """多行也能插值：${lang}"""

// 4) 斜杠字符串 /.../：正则友好，无需转义反斜杠
def path = /C:\Users\Alice\file.txt/   // 反斜杠原样保留
def re = ~/^\d{3}-\d{4}$/              // /.../ 还可用作正则字面量（前面加 ~）

// 5) 美元斜杠字符串 $/.../$：避免 ${} 与自身的 } 冲突，适合模板
def tpl = $/Hello ${name}, 金额：${amount}/$
```

选择建议：不需要插值用单引号（避免误触发 GString）；写正则路径用斜杠串；写大量 SQL/HTML 模板用三引号或美元斜杠串。

## GString 插值的坑 {#gstring}

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

**GString 与 `String` 不相等**（高频坑）：GString 在用于 `Map` 的 key、`switch` 的 case、`contains` 比对时，由于**没有** `equals(String)` 的对称实现，会出现反直觉结果：

```groovy
def key = "name"
def map = [:]
map["${key}"] = 1          // key 是 GString
println map["name"]        // null！因为存入的是 GString("name")，取出用 String("name")
println map["${key}"]      // 1

// switch 里同样会失配
def x = "1"
switch (x) {
    case "${1}": println "命中"; break   // 不会命中，GString != String
    default:    println "未命中"           // 打印这一行
}

// 结论：凡是当作 key / case / 精确比较的地方，记得 toString()
def g = "${key}".toString()   // 显式转成 String 再当 key
```

另外，**GString 是惰性的**：表达式在 `toString()` 时才求值，若变量后续被修改，输出会跟着变（见上方 `items` 示例）。这在日志拼接时要小心——拼接时变量的值可能不是你"当时"期望的值。

## 方法调用省略括号的坑 {#parens}

Groovy 允许在**顶层语句/DSL** 中省略方法调用的括号，但这会引入歧义：

```groovy
// 属性访问 vs 方法调用
class Person {
    String name
    String getName() { return name }
}
def p = new Person(name: "Alice")

println p.name          // 调 getter，输出 Alice
// 注意：即使你没写 getName()，Groovy 也会为 property 自动生成 getter

// 命名参数构造的"歧义"：new 关键字后跟的 map 会被当构造参数
def q = new Person(name: "Bob")   // 等价于 new Person([name:"Bob"]) 再用 setter 填充
```

坑点清单：

- `println obj.name` 调的是 getter，若字段是 `private` 且没有 getter，会抛 `MissingPropertyException`（除非用 `@PackageScope` 或显式字段）。
- 在嵌套调用里省略括号会让优先级难以判断，例如 `foo bar 1, 2` 容易产生歧义；**涉及运算或需要清晰优先级时一定加括号**。
- 当方法返回值和属性同名时，存在读取顺序：优先字段（若有）再 getter——建议统一用 property（即让 Groovy 生成 getter），避免手动字段与 getter 混用。

## `==` 与 `is()` {#equals}

```groovy
def a = new String("x")
def b = "x"
println a == b          // true：== 调用 equals，且对 null 安全
println a.is(b)         // false：is() 才是引用（身份）比较

// null 安全的优雅写法
println a == null       // false
// 等价于 Java 的 a.equals(b) 但不会因为 a 为 null 而 NPE
```

要点：`==` 永远先判 null 再调 `equals`；比较两个对象"是不是同一个实例"才用 `is()`。

## 数值运算的坑 {#numeric}

Groovy 的数值运算与 Java 行为差异很大，务必注意：

```groovy
// 1) 整数相除返回 BigDecimal，而不是截断整数！
println 1 / 2            // 0.5（Java 里是 0）
println 3 / 2            // 1.5

// 想要整数除法请用 intdiv()
println 3.intdiv(2)      // 1

// 2) 幂运算用 **
println 2 ** 10          // 1024

// 3) Integer 溢出不会抛异常，而是自动提升为 Long（"环绕"保护）
def big = Integer.MAX_VALUE + 1
println big.class        // class java.lang.Long

// 4) 默认字面量 1 是 Integer，加了小数点才是 BigDecimal
println (1).class        // Integer
println (1.0).class      // BigDecimal

// 5) 不同数值类型运算结果类型会被"提升"
println (1 + 2.0).class  // BigDecimal
```

实战坑：做金额计算**永远用 `BigDecimal`**（不要用 `double` 防精度丢失），而 Groovy 默认的字面量小数就是 `BigDecimal`，这点比 Java 友好；但 `1/3` 这类会得到无限小数，`BigDecimal` 默认保留 10 位，超出会四舍五入，必要时用 `new BigDecimal(...).divide(..., scale, RoundingMode)` 显式控制。

## switch 的强大 {#switch}

Groovy 的 `switch` 远比 Java 灵活：case 支持类型、正则、集合、范围、闭包等。

```groovy
def x = 12
switch (x) {
    case 0:            println "零"; break
    case 1..10:        println "1~10"; break          // 范围
    case ~/^\d+$/:     println "匹配数字正则"; break   // 正则
    case [100, 200]:   println "在列表中"; break       // 集合/列表
    case Integer:      println "是 Integer 类型"; break// 类型
    case { it % 2 == 0 }: println "偶数（闭包）"; break// 闭包
    default:           println "其他"
}
// 输出：是 Integer 类型
```

注意：多个 case 同时匹配时，**从上到下取第一个命中分支**，且**类型 case 必须放在范围/值之前**，否则被范围先捕获（如上面 `Integer` 若放在 `1..10` 之后，则 `12` 这个 `Integer` 仍能被 `Integer` 命中，但数值 `5` 会被 `1..10` 先命中）。写复杂 `switch` 时把更具体的 case 放前面。

## 可选分号与可选 return {#conciseness}

```groovy
// 分号可选
println "a"; println "b"   // 等价两条语句

// 方法/闭包最后一个表达式自动作为返回值，无需 return
def doubleIt(n) { n * 2 }   // 返回 n*2
println doubleIt(3)         // 6

// 但带 return 的提前返回要明确写出
def check(n) {
    if (n < 0) return "负"
    "非负"                    // 这是返回值
}
```

注意：在闭包里 `return` 只结束**当前闭包这一次迭代**，不会结束外层方法（见下一章 `each` 的坑）。

## 小结 {#summary}

Groovy 在 Java 之上做了大量"符合直觉"的简化，但真值判定、GString 与 String 不等价、整数相除得小数、Elvis 判定真值而非 null 等差异，正是从 Java 转过来最易踩的坑；理解缺省导入、`==`/`is()`、安全导航边界能帮你少写大量样板代码。下一章将深入学习 Groovy 强大的集合与闭包，以及 `each`/`collect` 的那些易混点。
