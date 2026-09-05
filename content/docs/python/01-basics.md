---
title: 第一章 基础语法与类型
linkTitle: 基础语法
description: Python 变量、数据类型、控制流与函数定义
weight: 41
---

# 基础语法与类型

## 变量与类型 {#variables}

Python 是**动态类型**语言，变量无需声明类型：

```python
name = "Alice"      # str
age = 25            # int
height = 1.75       # float
is_student = True   # bool
nothing = None      # NoneType
```

## 基本类型 {#types}

```python
# 数字
x = 10          # int
y = 3.14        # float
z = 1 + 2j      # complex

# 字符串（单引号或双引号均可）
s1 = 'hello'
s2 = "world"
s3 = """多行
字符串"""

# 布尔值
True / False
```

## 字符串操作 {#strings}

```python
name = "Python"
name.upper()        # "PYTHON"
name.lower()        # "python"
name.replace("P", "J")  # "Jython"

# f-string 格式化（Python 3.6+）
version = 3.12
print(f"当前 Python 版本是 {version}")

# 切片
name[0]     # "P"
name[1:4]   # "yth"
name[::-1]  # "nohtyP" 反转
```

## 控制流 {#control-flow}

```python
# 条件（注意缩进，用冒号）
score = 85
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# 循环
for i in range(5):
    print(i)

for item in [1, 2, 3]:
    print(item)

# while
count = 0
while count < 3:
    print(count)
    count += 1
```

## 函数 {#functions}

```python
def greet(name, greeting="Hello"):
    """文档字符串：返回问候语"""
    return f"{greeting}, {name}"

greet("Alice")                 # "Hello, Alice"
greet("Bob", greeting="Hi")    # "Hi, Bob"

# 可变参数
def sum_all(*args):
    return sum(args)

sum_all(1, 2, 3, 4)  # 10

# 关键字参数
def info(**kwargs):
    return kwargs

info(name="Alice", age=25)  # {'name': 'Alice', 'age': 25}
```

## 小结 {#summary}

Python 通过缩进组织代码块，语法简洁易读。下一章学习 Python 强大的内置数据结构。
