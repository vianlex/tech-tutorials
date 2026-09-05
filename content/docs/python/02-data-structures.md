---
title: 第二章 数据结构与字符串
linkTitle: 数据结构与字符串
description: 列表、元组、字典、集合的核心操作、切片技巧与字符串格式化（f-string 专题）
weight: 42
---

# 数据结构与字符串

Python 内置四种核心数据结构与丰富的字符串方法，是日常编码的主力。

## 列表（list） {#list}

可变、有序、可重复：

```python
fruits = ["apple", "banana", "cherry"]

fruits.append("orange")     # 末尾添加
fruits.insert(0, "pear")    # 指定位置插入
fruits.remove("banana")     # 删除首个匹配项
last = fruits.pop()         # 弹出末尾元素
fruits[0] = "grape"         # 按索引修改

# 切片 [start:stop:step]
nums = [0, 1, 2, 3, 4, 5]
nums[1:4]       # [1, 2, 3]
nums[::-1]      # [5, 4, 3, 2, 1, 0] 反转
```

## 元组（tuple） {#tuple}

不可变、有序，适合表示固定结构：

```python
point = (3, 4)
x, y = point    # 解包
print(x, y)     # 3 4

single = (1,)   # 单元素元组必须加逗号
```

## 字典（dict） {#dict}

键值对，键必须可哈希（如 str、int、tuple）：

```python
user = {"name": "Alice", "age": 25}

user["city"] = "Beijing"        # 添加/修改
value = user.get("email", "无") # 安全取值，带默认值
user.pop("city")                # 删除并返回

for key, value in user.items(): # 遍历键值
    print(key, value)
```

## 集合（set） {#set}

无序、不重复，适合去重与集合运算：

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b    # 并集 {1,2,3,4,5,6}
a & b    # 交集 {3,4}
a - b    # 差集 {1,2}
a ^ b    # 对称差 {1,2,5,6}
a.add(5); a.remove(5)
```

## 字符串常用方法 {#string-methods}

```python
s = "  Hello, Python!  "
s.strip()            # 去两端空白 "Hello, Python!"
s.upper()            # "  HELLO, PYTHON!  "
s.replace("Python", "World")  # 替换
s.split(",")         # ["  Hello", " Python!  "]
",".join(["a", "b"]) # "a,b"

# 字符串不可变：不能直接 s[0] = "h"，需用方法生成新串
new = "P" + s[1:]    # 拼接得到新字符串
```

## 拼接与原始字符串 {#concat-raw}

```python
# 拼接
greeting = "Hello, " + "World"     # 简单拼接
parts = ["a", "b", "c"]
"".join(parts)                      # 大量拼接时更高效

# 原始字符串：反斜杠不被转义，常用于正则与路径
path = r"C:\Users\name\file.txt"    # 反斜杠原样保留
r"\d+\.\d+"                         # 正则中无需写 \\
```

## 字符串格式化：f-string 重点 {#f-string}

Python 3.6+ 推荐，用 `f""` 在 `{}` 中直接嵌入表达式：

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

# 对齐与填充
print(f"{name:>10}")               # 右对齐，宽度10
print(f"{name:<10}")               # 左对齐
print(f"{name:^10}")               # 居中
print(f"{42:0>5}")                 # 00042 用0填充

# 转义花括号
print(f"{{这不是变量}}")            # {这不是变量}

# 3.8+ 调试语法：自动输出 变量=值
x = 10
print(f"{x=}")                      # x=10
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

掌握 list/tuple/dict/set 的差异（可变性、有序性、去重）才能选对容器；字符串不可变但方法丰富，f-string 是首选格式化方式。下一章学习函数与模块化组织代码。
