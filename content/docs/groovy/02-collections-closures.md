---
title: 第二章 集合与闭包
linkTitle: 集合与闭包
description: Groovy 的 List/Map、each 与 collect 的差别、闭包解析策略与常用高阶方法
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

补充坑点：

- 越界不会像 Java 那样抛异常：`list[99]` 返回 `null`，写入越界位置则自动用 `null` 填充中间元素。
- 切片 `list[0..2]` 返回**新列表**，改它不影响原列表；但 `list[0]` 直接拿引用。
- 用 `as` 强制转换类型：`[1,2,3] as Set` 得到去重集合，`[1,2,3] as int[]` 得到基本类型数组。

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

深入补充：

- `map.key` 形式要求 key 是**合法的 Groovy 标识符**；带连字符/空格的键必须用 `map["my-key"]`。`map."my-key"` 也可以。
- `map.name` 在 key 不存在时返回 `null`；若你想"取不到就给默认"，用 `map.get("name", "默认")` 或 `map.getOrDefault(...)`。
- `withDefault` 让缺失的 key 自动产生默认值（非常适合计数/分组累加）：

```groovy
def counts = [:].withDefault { 0 }
counts["a"] += 1
counts["a"] += 1
counts["b"] += 1
println counts        // [a:2, b:1]
```

- 判断 key 是否存在用 `map.containsKey("x")`；`map.x` 为 `null` 无法区分"不存在"和"值是 null"。

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

**`each` 返回原集合、`collect` 才返回新集合**——这是新手最常见的坑：

```groovy
def nums = [1, 2, 3]
def r1 = nums.each { it * 2 }     // r1 还是 [1, 2, 3]！each 不收集返回值
def r2 = nums.collect { it * 2 }  // r2 才是 [2, 4, 6]
println r1
println r2
```

**`each` 里的 `return` 只结束当前这次闭包迭代**，不是结束整个方法：

```groovy
def nums = [1, 2, 3, 4]
nums.each {
    if (it == 2) return          // 仅跳过 2 这一次迭代，循环继续
    println it                    // 打印 1, 3, 4
}
// 想"找到就中断"请用 find/findResult，或改用 for 循环 + break
```

如果想在遍历中提前中止，`each` 做不到，应使用 `find`（返回第一个匹配项）或用传统 `for`/`while` 循环。

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

补充方法：

- `collectEntries`：把元素收集成 Map（闭包返回 `[k, v]` 或 `(k, v)`）：

```groovy
def words = ["a", "bb", "ccc"]
def byLen = words.collectEntries { [it, it.size()] }
println byLen        // [a:1, bb:2, ccc:3]
```

- `grep`：按类型/正则/闭包过滤，比 `findAll` 更"声明式"：

```groovy
println [1, "a", 2, "b"].grep(Integer)          // [1, 2]（按类型）
println ["apple", "bat", "banana"].grep(~/.a/)  // [apple, banana]（按正则）
```

- `findResults`：类似 `collect` + 过滤，闭包返回 `null` 的项会被丢弃：

```groovy
def r = [1, 2, 3, 4].findResults { it % 2 == 0 ? it * 10 : null }
println r            // [20, 40]
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

深入补充：

- `min`/`max` 可带闭包作为比较器：`words.max { it.length() }` 返回最长的串。
- `sum`/`count` 可带闭包：`[1,2,3].sum()` 求和为 6；`[1,2,3,null].count { it }` 统计非 null。
- `sort` 默认**原地修改**并返回同一列表；要保留原列表用 `sorted()`（Groovy 4）或 `list.toList().sort()`。`sort { ... }` 用闭包排序。
- `inject`（即 `foldLeft`）还能做任意折叠，初始值类型决定结果类型：

```groovy
def freq = ["a","b","a"].inject([:].withDefault{0}) { m, w -> m[w]++; m }
println freq        // [a:2, b:1]
```

- 组合类：`eachPermutation`（全排列）、`combinations`（笛卡尔积），适合小数据枚举：

```groovy
println [[1,2],[3,4]].combinations()   // [[1, 3], [1, 4], [2, 3], [2, 4]]
```

## `with` 与对象上下文 {#with}

`with(Closure)` 在**对象自身作为 delegate** 的上下文中执行闭包，用来连续调用同一对象的属性/方法，省去重复写对象名：

```groovy
class Person {
    String name
    int age
    void say() { println "$name, $age" }
}

def p = new Person()
p.with {
    name = "Alice"     // 等价于 p.name = ...
    age = 25
    say()
}
```

注意：`with` 默认 `delegate` 是该对象、`resolveStrategy` 为 `OWNER_FIRST`，所以若闭包里引用了外部同名变量，会优先用外部变量——这是隐性 bug 来源，写 `with` 块时变量名要避免与外部冲突。`inject` 配合 `with` 也很常见：

```groovy
def s = [1,2,3].inject(new StringBuilder(), { sb, n -> sb.append(n); sb }).toString()
println s        // 123
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

补充细节：

- 闭包是 `groovy.lang.Closure` 的实例，有 `call()` 方法，`greet("Alice")` 实际调用 `greet.call("Alice")`。
- 闭包能访问其**定义处**的局部变量（捕获），且被捕获的变量可被闭包修改（Java 的 lambda 要求 final，Groovy 不需要）。
- 闭包可作为"代码块"优雅地实现回调、策略模式。

## 闭包委托与解析策略 {#delegate}

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

**`owner` 与 `delegate` 的区别**：`owner` 是"定义该闭包的宿主对象"（通常是外层类或闭包，不可变）；`delegate` 是"方法/属性查找的兜底对象"（默认等于 owner，可手动改）。查找顺序由 `resolveStrategy` 控制：

| 策略 | 含义 |
|------|------|
| `OWNER_FIRST`（默认） | 先找 owner，再找 delegate |
| `DELEGATE_FIRST` | 先找 delegate，再找 owner |
| `DELEGATE_ONLY` | 只找 delegate，owner 里也没有就报错 |
| `OWNER_ONLY` | 只找 owner |

```groovy
def outer = [name: "Outer"]
def inner = [name: "Inner"]

def c = { name }          // 取 name 属性
c.delegate = inner
c.owner = outer           // 实际上 owner 由闭包定义决定，这里仅示意
c.resolveStrategy = Closure.DELEGATE_FIRST
```

这是 Gradle、Spock 等 DSL 的基石：**DSL 容器把自己的实例设为闭包 delegate**，于是你在闭包里写的 `dependencies { ... }` 实际是调用该容器的同名方法。调试 DSL 时，若报"找不到方法"，十有八九是 delegate/resolveStrategy 没设对。

## 闭包常用方法（偏函数与缓存） {#closure-methods}

```groovy
// curry / rcurry / ncurry：偏函数，固定部分参数
def add3 = { a, b, c -> a + b + c }
def inc = add3.curry(1)        // 固定第一个参数为 1 -> (b,c)->1+b+c
println inc(2, 3)              // 6
def from10 = add3.rcurry(10)   // 固定最后一个参数
println from10(1, 2)           // 13
def mid = add3.ncurry(1, 100)  // 固定中间参数
println mid(1, 2)              // 103

// memoize：自动缓存相同输入的结果（适合纯函数、递归斐波那契等）
def fib
fib = { n -> n < 2 ? n : fib(n-1) + fib(n-2) }.memoize()
println fib(30)               // 缓存后极快

// trampoline：避免深层递归栈溢出，把递归改写成"返回下一次调用"
def fact
fact = { n, acc = 1 -> n <= 1 ? acc : fact.trampoline(n - 1, n * acc) }.trampoline()
println fact(10000)           // 不会 StackOverflow
```

注意：`memoize()` 缓存是无界的（有 `memoizeAtMost`/`memoizeAtLeast`/`memoizeBetween` 可限制容量），且**只适用于无副作用的纯函数**——否则缓存会掩盖状态变化。

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

深入用法（见下一章展开）：

- `obj.&method`：绑定实例的方法指针。
- `ClassName.&staticMethod`：静态方法指针。
- `ClassName::new`（Groovy 4）：构造方法引用，可用在 `collect`/`inject` 中把数据变成对象。

```groovy
class Point { int x, y; Point(int x, int y){ this.x=x; this.y=y } }
def pts = [[1,2],[3,4]].collect(Point::new)   // 每对元素构造一个 Point
```

## `*.` 展开运算符与 `collect` 的区别 {#spread-vs-collect}

```groovy
def list = ["a", "bb"]
println list*.size()         // [1, 2]：等价于 list.collect { it.size() }
```

差别：`list*.method()` 是**语法糖**，写法更短，且当 `list` 为 `null` 时能配合安全导航 `list?*.size()` 整体返回 null；`collect` 更灵活（可写多行逻辑、`it` 改名）。性能上二者一致，按可读性选择即可。

## 安全导航在集合上的应用 {#safe-collection}

```groovy
def list = null
println list?.size()         // null（不会 NPE）

def map = null
println map?.name            // null

// 链式安全导航
def user = null
println user?.address?.city  // null
```

注意 `?.` 只在"null 短链路"上返回 null；若某环节是空集合（而非 null），`?.size()` 会返回 `0`（因为空集合不是 null，只是 Groovy truth 为 false）。

## `@Immutable` 与 `as` 强制类型转换 {#immutable-as}

```groovy
import groovy.transform.Immutable

@Immutable
class Point {
    int x, y
}
def a = new Point(1, 2)
// a.x = 5  // 报错：字段是 final

// as 强制转换
def set = [1, 2, 2, 3] as Set        // [1, 2, 3]
def arr = [1, 2, 3] as int[]         // 基本类型数组
def map = [name: "Alice"] as Map     // 显式声明
```

`@Immutable` 还会自动生成 `equals`/`hashCode`/`toString` 和 `tuple` 构造器，并且**集合/数组字段会被防御性拷贝**（深不可变），非常适合做配置/值对象。`as` 转换依赖目标类型实现 `asType` 或存在对应构造器/工厂；转不了会抛 `GroovyCastException`。

## 小结 {#summary}

集合配合闭包让 Groovy 处理数据异常简洁，但 `each` 返回原集合、`each` 里的 `return` 只结束单次迭代、`*.` 与 `collect` 的取舍、闭包 `delegate`/`resolveStrategy` 对 DSL 的决定性作用，都是日常高频且易混的点。下一章进入面向对象，了解属性机制、AST 注解与方法指针等让样板代码消失的利器。
