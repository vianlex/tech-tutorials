---
title: 第三章 函数与模块
linkTitle: 函数与模块
description: 函数定义、参数类型、作用域、lambda 表达式以及模块与包的导入机制
weight: 43
---

# 函数与模块

函数封装可复用逻辑，模块与包则把代码组织成清晰的结构。

## 定义函数 {#def}

```python
def greet(name, greeting="Hello"):
    """文档字符串：返回一句问候语"""
    return f"{greeting}, {name}"

greet("Alice")                 # "Hello, Alice"
greet("Bob", greeting="Hi")    # "Hi, Bob"
```

## 参数类型 {#parameters}

```python
# 默认参数
def power(x, n=2):
    return x ** n

# 关键字参数：调用时显式指定，顺序可变
power(n=3, x=2)                # 8

# *args：收集多余的位置参数为元组
def sum_all(*args):
    return sum(args)
sum_all(1, 2, 3, 4)            # 10

# **kwargs：收集多余的关键字参数为字典
def show(**kwargs):
    print(kwargs)
show(name="Alice", age=25)      # {'name': 'Alice', 'age': 25}
```

## 作用域 {#scope}

```python
x = "全局"

def func():
    x = "局部"      # 局部变量，不影响全局
    print(x)
func()              # 局部
print(x)            # 全局

# 修改全局变量需用 global
counter = 0
def inc():
    global counter
    counter += 1
```

## lambda 表达式 {#lambda}

匿名、单行函数，适合简短回调：

```python
square = lambda x: x ** 2
square(5)                       # 25

nums = [3, 1, 4, 2]
sorted(nums, key=lambda n: -n)  # 降序 [4, 3, 2, 1]
```

## 模块 {#modules}

一个 `.py` 文件即一个模块：

```python
# utils.py
def add(a, b):
    return a + b

PI = 3.14159
```

```python
# main.py —— 多种导入方式
import utils                  # 导入整个模块
utils.add(1, 2)

from utils import add         # 导入特定成员
add(1, 2)

import utils as u             # 起别名
u.add(1, 2)

from utils import *           # 导入全部（不推荐，易命名冲突）
```

## 包 {#packages}

包是含 `__init__.py` 的目录：

```text
mypackage/
├── __init__.py
├── core.py
└── utils.py
```

```python
from mypackage import core
from mypackage.core import some_function
```

## __name__ == "__main__" {#main-guard}

让模块既能导入又能独立运行：

```python
def main():
    print("程序入口")

# 直接运行本文件时 __name__ 为 "__main__"，被导入时则不是
if __name__ == "__main__":
    main()
```

## 小结 {#summary}

函数通过默认/`*args`/`**kwargs` 参数灵活适配调用场景，`lambda` 处理简短逻辑；模块与包配合 `__name__` 守卫实现可复用、可运行的代码组织。下一章进入面向对象与异常、文件处理。
