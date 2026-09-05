---
title: 第二章 数据结构与字符串
linkTitle: 数据结构与字符串
description: 列表、元组、字典、集合的核心操作与易踩坑点、切片技巧、字符串常用方法与 f-string 高级用法
weight: 42
---

# 数据结构与字符串

Python 内置四种核心数据结构与丰富的字符串方法，是日常编码的主力。选对容器、用对方法，能避免大量隐蔽 bug。

## 列表（list） {#list}

可变、有序、可重复，是最常用的容器。

```python
fruits = ["apple", "banana", "cherry"]

fruits.append("orange")     # 末尾添加单个元素
fruits.insert(0, "pear")    # 指定位置插入
fruits.remove("banana")     # 删除首个匹配项（不存在抛 ValueError）
last = fruits.pop()         # 弹出末尾元素并返回
fruits[0] = "grape"         # 按索引修改

# 切片 [start:stop:step]
nums = [0, 1, 2, 3, 4, 5]
nums[1:4]       # [1, 2, 3]
nums[::2]       # [0, 2, 4] 隔一个取一个
nums[::-1]      # [5, 4, 3, 2, 1, 0] 反转
```

### append vs extend 的区别

```python
a = [1, 2]
a.append([3, 4])     # [1, 2, [3, 4]] —— 把整个列表当成一个元素加进去
a = [1, 2]
a.extend([3, 4])     # [1, 2, 3, 4] —— 把可迭代对象的元素逐个追加
a += [5, 6]          # [1, 2, 3, 4, 5, 6]，等价于 extend
```

### sort（原地）vs sorted（返回新列表）

```python
nums = [3, 1, 4, 2]
nums.sort()          # 原地排序，返回 None，nums 变为 [1, 2, 3, 4]
new = sorted(nums)   # 返回新的已排序列表，原 nums 不变

# 都支持 key 与 reverse
words = ["banana", "apple", "cherry"]
sorted(words, key=len)           # 按长度排序
sorted(words, key=str.lower)     # 忽略大小写
nums.sort(reverse=True)          # 降序
```

### reverse / copy / del / count / index

```python
a = [1, 2, 3]
a.reverse()          # 原地反转，[3, 2, 1]
b = a.copy()         # 浅拷贝，等价于 a[:]
b is a              # False

a = [1, 2, 3, 2]
a.count(2)          # 2 —— 统计出现次数
a.index(2)          # 1 —— 首个匹配的索引（找不到抛 ValueError）

del a[0]            # 删除索引 0 处元素
del a[1:3]          # 删除切片
```

### 坑：列表乘法是「浅拷贝」

`[x] * n` 复制的是**引用**，嵌套可变对象会共享同一份：

```python
# 反例
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)       # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] 全部被改！

# 正确写法：用推导式生成独立子列表
matrix = [[0 for _ in range(3)] for _ in range(3)]
matrix[0][0] = 1
print(matrix)       # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

## 元组（tuple） {#tuple}

不可变、有序，适合表示固定结构、作为字典键。

```python
point = (3, 4)
x, y = point    # 解包
print(x, y)     # 3 4

single = (1,)   # 单元素元组必须加逗号，否则 (1) 只是加了括号的数字

# 嵌套元组解包
t = (1, (2, 3))
a, (b, c) = t   # a=1, b=2, c=3
```

### 命名元组 namedtuple

让元组像带字段名的小对象，且内存比类小：

```python
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
p.x             # 3
p.y             # 4
p.x = 5         # AttributeError！namedtuple 仍不可变

# 作为字典键（元组可哈希，前提是元素都可哈希）
d = {(1, 2): "a", (3, 4): "b"}
d[(1, 2)]       # "a"
```

## 字典（dict） {#dict}

键值对，键必须可哈希（如 str、int、tuple、frozenset）。Python 3.7+ 字典**保持插入顺序**。

```python
user = {"name": "Alice", "age": 25}

user["city"] = "Beijing"        # 添加/修改
value = user.get("email", "无") # 安全取值，带默认值
user.pop("city")                # 删除并返回值（键不存在抛 KeyError）
```

### setdefault 的妙用

避免「先判断是否存在再初始化」的重复代码：

```python
# 把单词按首字母分组
words = ["apple", "banana", "avocado", "blueberry"]
groups = {}
for w in words:
    groups.setdefault(w[0], []).append(w)
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry']}
# setdefault(key, default)：key 存在返回值，不存在则设为 default 并返回
```

### collections.defaultdict

比 `setdefault` 更优雅，访问缺失键时自动调用工厂函数生成默认值：

```python
from collections import defaultdict
groups = defaultdict(list)      # 缺失键自动用 list() 生成 []
for w in words:
    groups[w[0]].append(w)

# 其他工厂：int（计数）、set 等
counter = defaultdict(int)
for ch in "hello":
    counter[ch] += 1            # 缺失时默认为 0
```

### Counter 计数

```python
from collections import Counter
c = Counter("banana")
c["a"]          # 3
c.most_common(2)    # [('a', 3), ('n', 2)] 出现最多的 2 个
```

### 字典合并

```python
a = {"x": 1}
b = {"y": 2}

# 写法一：解包（Python 3.5+）
merged = {**a, **b}        # {'x': 1, 'y': 2}

# 写法二：| 运算符（Python 3.9+，更新用 |=）
merged = a | b             # {'x': 1, 'y': 2}
a |= b                     # 原地合并到 a

# 冲突时后者覆盖前者
{"x": 1} | {"x": 2}        # {'x': 2}
```

### 遍历时修改字典的坑

```python
# 反例：遍历时直接增删键会抛 RuntimeError
d = {"a": 1, "b": 2}
for k in d:
    if d[k] == 1:
        d["c"] = 3         # RuntimeError: 字典在遍历时改变大小

# 正确：遍历键的副本
for k in list(d.keys()):
    if d[k] == 1:
        d["c"] = 3

# 或先收集要删的键
to_del = [k for k, v in d.items() if v == 1]
for k in to_del:
    del d[k]
```

## 集合（set） {#set}

无序、不重复，适合去重与集合运算。元素必须可哈希。

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b    # 并集 {1,2,3,4,5,6}
a & b    # 交集 {3,4}
a - b    # 差集 {1,2}
a ^ b    # 对称差 {1,2,5,6}
a.add(5); a.remove(5)      # 增删（remove 不存在抛 KeyError，discard 不抛）
a.discard(999)             # 不存在也安全
```

### frozenset 与去重保序

```python
# frozenset 是不可变集合，可哈希，可作字典键 / 集合元素
fs = frozenset([1, 2, 3])
d = {fs: "value"}

# 集合推导式
s = {x*x for x in range(5)}    # {0, 1, 4, 9, 16}

# 去重但保留首次出现顺序（Python 3.7+ dict 保序，可借此去重）
seq = [3, 1, 3, 2, 1]
dedup = list(dict.fromkeys(seq))   # [3, 1, 2]
# 更直观（顺序依赖 dict 保序）：list(set(...)) 顺序不保证
```

## 切片深入 {#slicing}

切片不仅用于读取，还能**赋值**和生成 `slice` 对象。

```python
a = [0, 1, 2, 3, 4, 5]
a[1:3] = [10, 20]      # 切片赋值：替换区间 [1:3)
# a -> [0, 10, 20, 3, 4, 5]

a[1:4] = []            # 删除区间 [1:4)
a[2:2] = [99]          # 在索引 2 处插入

# slice 对象可复用
step2 = slice(0, 10, 2)
nums = list(range(10))
nums[step2]            # [0, 2, 4, 6, 8]

# 切片越界不报错，自动截断
a = [1, 2, 3]
a[1:100]               # [2, 3]
```

## 字符串常用方法 {#string-methods}

字符串**不可变**，所有「修改」方法都返回新字符串。

```python
s = "  Hello, Python!  "
s.strip()            # 去两端空白 "Hello, Python!"
s.lstrip(); s.rstrip()   # 只去左/右
s.upper()            # 大写
s.lower()            # 小写
s.replace("Python", "World")  # 替换（可指定次数 s.replace(a,b,1)）
s.split(",")         # 分割 -> ["  Hello", " Python!  "]
",".join(["a", "b"]) # 拼接 -> "a,b"

# 字符串不可变：不能直接 s[0] = "h"
new = "P" + s[1:]    # 拼接得到新字符串
```

### 更多字符串方法细节

```python
s = "hello world"

# startswith / endswith 可接受元组（批量判断）
s.startswith(("he", "Ha"))   # True
s.endswith((".py", ".txt"))  # False

# find vs index：找不到时行为不同
s.find("xyz")     # -1（找不到返回 -1，不抛异常）
s.index("xyz")    # ValueError！找不到直接抛

# 宽度对齐与填充
"42".zfill(5)        # "00042" 左侧补 0
"hi".ljust(5, "*")   # "hi***" 右补
"hi".rjust(5, "*")   # "***hi" 左补
"hi".center(6, "-")  # "--hi--" 居中

# translate：批量字符映射（先建表，性能好）
import string
table = str.maketrans("aeiou", "12345")
"hello".translate(table)     # "h2ll4"

# casefold vs lower：casefold 更激进，适合跨语言不区分大小写比较
"ß".lower()      # "ß"
"ß".casefold()   # "ss"  —— 德语 eszett

# 判断类
"abc123".isalnum()   # True 字母数字
"123".isdigit()      # True 数字
"   ".isspace()      # True 空白
"Abc".istitle()      # True 标题化

# 按行分割（识别 \n \r \r\n，且不会在末尾多一个空串）
"a\nb\n".splitlines()    # ['a', 'b']

# 子串判断
"py" in "python"     # True
"python" * 3         # "pythonpythonpython" 字符串乘法
```

## 字符串格式化：f-string 重点 {#f-string}

Python 3.6+ 推荐，用 `f""` 在 `{}` 中直接嵌入表达式。3.12 起 `{...}` 内可直接复用外层引号。

```python
name = "Alice"
age = 25

# 基本用法
print(f"{name} 今年 {age} 岁")

# 嵌入表达式与函数调用
print(f"明年 {age + 1} 岁，姓名长度 {len(name)}")

# 格式化选项
pi = 3.14159
print(f"保留两位小数 {pi:.2f}")     # 3.14
print(f"千分位 {1234567:,}")         # 1,234,567
print(f"百分比 {0.1234:.2%}")        # 12.34%
print(f"科学计数 {12345:.2e}")       # 1.23e+04

# 对齐与填充
print(f"{name:>10}")               # 右对齐，宽度10
print(f"{name:<10}")               # 左对齐
print(f"{name:^10}")               # 居中
print(f"{42:0>5}")                 # 00042 用0填充

# 进制与格式
x = 255
print(f"{x:b}")        # 11111111  二进制
print(f"{x:#x}")       # 0xff     带前缀十六进制
print(f"{x:08b}")      # 11111111 宽度8补0

# 日期格式化（datetime 可直接在 {} 内指定格式）
from datetime import datetime
now = datetime.now()
print(f"今天 {now:%Y-%m-%d %H:%M:%S}")

# 转换标志
s = "文本"
print(f"{s!r}")       # '文本'    repr 形式
print(f"{s!s}")       # 文本      str 形式
print(f"{s!a}")       # '\u6587\u672c'  ascii 形式

# 3.8+ 调试语法：自动输出 变量=值
x = 10
print(f"{x=}")        # x=10
print(f"{x*2=}")      # x*2=20

# 嵌套引号：3.12 之前内层引号需与外层的不同
print(f"他说：'{name}'")          # 外层双引号，内层单引号
# 3.12+ 允许同名引号
# print(f"他说："{name}""")       # 仅 3.12+

# 转义花括号
print(f"{{这不是变量}}")            # {这不是变量}
```

## 拼接与原始字符串 {#concat-raw}

```python
# 拼接
greeting = "Hello, " + "World"     # 简单拼接
parts = ["a", "b", "c"]
"".join(parts)                      # 大量拼接时更高效（避免 + 反复创建新串）
# f-string 通常是最可读的拼接方式

# 原始字符串：反斜杠不被转义，常用于正则与路径
path = r"C:\Users\name\file.txt"    # 反斜杠原样保留
r"\d+\.\d+"                         # 正则中无需写 \\
# 注意：原始字符串不能以单个反斜杠结尾，r"\" 是语法错误
```

## 其他格式化方式 {#other-format}

`%` 与 `str.format()` 旧式写法，了解即可：

```python
# 旧式 % 格式化
"姓名：%s，年龄：%d" % ("Alice", 25)

# str.format()
"姓名：{}，年龄：{}".format("Alice", 25)
"姓名：{name}".format(name="Alice")
# 新项目建议统一使用 f-string，可读性更好
```

## 小结 {#summary}

本章深入了 list/tuple/dict/set 的差异与高频易踩坑点：列表乘法的浅拷贝陷阱、`sort`/`sorted` 的返回差异、`setdefault`/`defaultdict`/`Counter` 的字典妙用、遍历字典时修改的报错、切片赋值与 `slice` 对象等。字符串的 `find`/`index` 差异、`casefold` 与 `lower`、`startswith` 元组用法，以及 f-string 的 `=`、`!r`、`{:,}`、`{%Y-%m-%d}` 等高级技巧也一并覆盖。下一章学习函数与模块化组织代码。
