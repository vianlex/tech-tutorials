---
title: 第一章 基础与控制流
linkTitle: 基础与控制流
description: Python 变量、类型、运算符、输入输出、条件与循环控制流，以及日常开发最高频的语法细节、行为差异与常见坑
weight: 41
---

# 基础与控制流

Python 以缩进划分代码块，语法简洁易读，是入门编程的良好选择。但简洁之下藏着不少**容易踩坑的行为差异**，本章在保留基础结构的同时，重点补充日常开发中最常用的语法细节和坑点。

## 变量与类型 {#variables}

Python 是**动态类型**语言，变量无需声明类型，赋值即创建。理解「变量是名字，对象是值」这一点至关重要：变量只是绑定到对象的**标签**，而非对象本身。

```python
name = "Alice"      # str 字符串
age = 25            # int 整数
height = 1.75       # float 浮点
is_student = True   # bool 布尔
nothing = None      # NoneType 空值

# 查看类型与转换
type(age)           # <class 'int'>
float(age)          # 25.0
str(age)            # "25"

# 同一对象可以有多个名字（别名）
a = [1, 2, 3]
b = a               # b 和 a 指向同一个列表对象
b.append(4)
print(a)            # [1, 2, 3, 4] —— 改 b 也改了 a！
```

> 坑点提示：`b = a` 是「绑定同一个对象」，不是「复制」。需要独立副本时用 `b = a.copy()`（列表）或 `b = a[:]`（切片）或 `import copy; b = copy.deepcopy(a)`（嵌套深拷贝）。详见下文「可变对象的默认参数陷阱」。

## 基本类型 {#types}

```python
# 数字
x = 10          # int（整数，Python 3 中 int 无大小上限）
y = 3.14        # float
z = 1 + 2j      # complex 复数

# 字符串：单引号、双引号等价，三引号表示多行
s1 = 'hello'
s2 = "hello"    # 与 s1 完全相同
s3 = """多行
字符串"""

# 布尔值参与运算时 True=1, False=0
True + True     # 2
True * 10       # 10

# 注意：bool 是 int 的子类
isinstance(True, int)   # True
```

## 运算符 {#operators}

### 算术与整除的细节

```python
a = 7 // 2      # 3  整除（向下取整）
b = 7 % 2       # 1  取余
c = 2 ** 10     # 1024 幂

# 坑：// 是「向下取整」而非「向零取整」，负数时要注意
-7 // 2         # -4，不是 -3！（向下取整：-3.5 → -4）
-7 % 2          # 1（Python 的 % 与 // 保持一致：a == (a//b)*b + a%b）

# divmod 同时取商和余数，常见于分页、时间换算
divmod(7, 2)    # (3, 1)
divmod(100, 60) # (1, 40) —— 100 秒 = 1 分 40 秒
```

### 浮点精度陷阱

```python
0.1 + 0.2       # 0.30000000000000004，而非 0.3
0.1 + 0.2 == 0.3    # False！

# 解法一：使用 decimal（金融/精度敏感场景）
from decimal import Decimal
Decimal("0.1") + Decimal("0.2")   # Decimal('0.3')

# 解法二：比较时用误差容限
abs(0.1 + 0.2 - 0.3) < 1e-9       # True
```

### 比较与身份：`is` 与 `==`

```python
# == 比较「值」是否相等，is 比较「是否为同一个对象」（身份，id 相同）
a = [1, 2, 3]
b = [1, 2, 3]
a == b          # True  —— 值相等
a is b          # False —— 不是同一个对象

# 坑：小整数缓存（-5 ~ 256）会让 is 有时为 True
x = 256
y = 256
x is y          # True  —— 因为 256 在缓存区间内，复用同一对象
m = 257
n = 257
m is n          # False —— 超出缓存区间，两个独立对象

# 坑：字符串 intern（字符串驻留）也让 is 不可靠
s1 = "hello"
s2 = "hello"
s1 is s2        # True  —— 短字符串被自动 intern
s3 = "hello world!"
s4 = "hello world!"
s3 is s4        # 不一定！依赖实现，不可依赖
```

> 经验法则：**永远用 `==` 比较值，只在判断「是否是 None / 单例」时用 `is`**（如 `x is None`），不要用 `is` 比较数字或字符串。

### 真值判定与逻辑短路

```python
# 以下都视为「假」：False、None、0、0.0、""、[]、()、{}、set()
bool(0)         # False
bool("")        # False
bool([])        # False
bool(None)      # False

# and / or 返回的是「实际的操作数」，不是布尔值
3 and 5         # 5  —— 返回最后一个被求值的值
0 or "default"  # "default" —— 返回第一个真值
"" or "x"       # "x"

# 利用短路做默认值
name = user_input or "匿名"     # 当 user_input 为空/None 时用默认值

# 短路也常用于防止错误
x = None
x and x.get("key")              # None，不会因 x 为 None 而报错
```

## 输入输出 {#io}

```python
name = input("请输入你的名字：")   # 读取用户输入，永远返回 str
age = int(input("年龄："))        # 需要数值时手动转换，转换失败会抛 ValueError

print("你好", name)               # 默认以空格分隔、换行结尾
print("a", "b", sep="-", end="") # 自定义分隔符与结尾，输出: a-b

# 用 f-string 拼接输出（推荐）
age = 25
print(f"{name} 今年 {age} 岁")
```

## 条件语句 {#if}

```python
score = 85
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# 三元表达式（简洁但别嵌套过深，否则可读性差）
status = "成年" if age >= 18 else "未成年"

# 条件可以是任意对象，按真值判定
items = []
if items:        # 等价于 if len(items) > 0，但更 Pythonic
    print("非空")
```

## 海象运算符 `:=` {#walrus}

Python 3.8+ 引入，可在**表达式内部**赋值，常用于避免在循环或条件里重复计算。

```python
# 场景一：避免重复调用函数
# 旧写法：取两次长度
data = [1, 2, 3]
if len(data) > 1:
    print(len(data))   # 重复 len(data)

# 海象写法：只算一次
if (n := len(data)) > 1:
    print(n)

# 场景二：while 读取到结束
while (line := f.readline()):
    print(line)

# 场景三：正则匹配后立即使用
import re
if (m := re.search(r"(\d+)", "订单号 123")):
    print(m.group(1))   # 123
```

## match 结构化模式匹配 {#match}

Python 3.10+ 引入的 `match`/`case`，类比其他语言的 `switch`，但能力更强（基于**模式**匹配）。

```python
def handle(cmd):
    match cmd.split():
        case ["quit"]:              # 精确匹配列表
            return "退出"
        case ["go", direction]:     # 捕获变量
            return f"前往 {direction}"
        case ["go", *rest]:         # *rest 捕获剩余
            return f"多余参数 {rest}"
        case ["set", name, value] if value.isdigit():  # 守卫 if
            return f"设置 {name}={value}"
        case _:                     # 通配符，等价于 default
            return "未知指令"

# 也支持「或」模式与字面量匹配
status = 200
match status:
    case 200 | 201 | 204:
        print("成功")
    case 404:
        print("未找到")
    case code if code >= 500:
        print("服务端错误")
    case _:
        print("其他")
```

## 循环 {#loops}

```python
# for：遍历可迭代对象
for i in range(5):        # 0,1,2,3,4
    print(i)

for item in ["a", "b", "c"]:
    print(item)

# range 的步长与方向
list(range(0, 10, 2))     # [0, 2, 4, 6, 8]
list(range(5, 0, -1))     # [5, 4, 3, 2, 1] 倒序

# while：条件为真时持续
count = 0
while count < 3:
    print(count)
    count += 1
```

### enumerate / zip 增强循环

```python
# enumerate：同时拿索引和值
for i, v in enumerate(["a", "b", "c"], start=1):   # 可从 1 开始
    print(i, v)            # 1 a / 2 b / 3 c

# zip：并行遍历多个序列
names = ["Alice", "Bob"]
ages = [25, 30]
for name, age in zip(names, ages):
    print(name, age)

# Python 3.10+：strict=True 要求序列等长，否则抛 ValueError
# 防止「悄悄截断」导致的隐性 bug
for name, age in zip(names, [25], strict=True):   # ValueError! 长度不一致
    pass

# 不等长时用 itertools.zip_longest 补齐
from itertools import zip_longest
list(zip_longest(names, [25], fillvalue="?"))    # [('Alice', 25), ('Bob', '?')]
```

### for...else / while...else 语义

`else` 块在**循环正常结束（没有被 break）**时执行，常用于「查找成功 vs 没找到」的场景。

```python
# 在序列中查找目标，找到就 break
def find(nums, target):
    for n in nums:
        if n == target:
            print("找到了")
            break
    else:
        # 只有「全程没 break」才执行这里
        print("没找到")

find([1, 2, 3], 2)   # 找到了
find([1, 2, 3], 9)   # 没找到
```

## break 与 continue {#break-continue}

```python
# break：提前结束整个循环
for n in range(10):
    if n == 3:
        break
    print(n)             # 0 1 2

# continue：跳过本次，进入下一轮
for n in range(5):
    if n % 2 == 0:
        continue
    print(n)             # 1 3
```

## 序列解包与变量交换 {#unpacking}

Python 的解包（unpacking）语法非常灵活，能大幅减少样板代码。

```python
# 多变量同时赋值
a, b, c = 1, 2, 3

# 经典：无需临时变量即可交换
a, b = b, a           # 右值先打包成元组，再解包给左边

# *rest 收集多余元素（只能有一个 * 收集）
first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2,3,4], last=5

# 嵌套解包
point = (3, (4, 5))
x, (y, z) = point     # x=3, y=4, z=5

# 忽略某些值，用 _ 约定
name, _, score = ("Alice", "忽略", 95)
```

## 可变对象的默认参数陷阱 {#mutable-default}

这是 Python 新手**最高频**的 bug 之一：默认参数值在**函数定义时只求值一次**，而非每次调用时。

```python
# 反例：可变默认参数被所有调用共享
def add_item(item, lst=[]):
    lst.append(item)
    return lst

add_item(1)    # [1]
add_item(2)    # [1, 2] ！第二次调用复用了同一个列表

# 正确写法：用 None 作占位，内部初始化
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst

add_item(1)    # [1]
add_item(2)    # [2] 各自独立
```

## 小结 {#summary}

本章夯实了 Python 的基础语法，并重点揭示了日常开发最容易踩的坑：`is` 与 `==` 的身份/值差异、小整数缓存与字符串 intern 的陷阱、浮点精度问题、`//` 向下取整、可变对象别名与默认参数共享、以及 `and`/`or` 短路返回真实值等。同时补充了 `:=` 海象运算符、3.10+ 的 `match` 模式匹配、`enumerate`/`zip(strict=True)`、`for...else` 语义与序列解包等高频技巧。下一章学习 Python 强大的内置数据结构与字符串处理细节。
