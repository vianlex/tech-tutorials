---
title: 第二章 数据结构
linkTitle: 数据结构
description: 列表、元组、字典、集合与推导式
weight: 42
---

# 数据结构

Python 内置四种核心数据结构，覆盖大多数场景。

## 列表（list） {#list}

可变、有序、可重复：

```python
fruits = ["apple", "banana", "cherry"]

fruits.append("orange")     # 末尾添加
fruits.insert(0, "pear")    # 指定位置插入
fruits.remove("banana")     # 删除元素
last = fruits.pop()         # 弹出末尾
fruits[0] = "grape"         # 修改

# 切片
fruits[1:3]     # 子列表
fruits[::-1]    # 反转
```

## 元组（tuple） {#tuple}

不可变、有序：

```python
point = (3, 4)
x, y = point    # 解包
print(x, y)     # 3 4

single = (1,)   # 单元素元组需要逗号
```

## 字典（dict） {#dict}

键值对，键不可变：

```python
user = {"name": "Alice", "age": 25}

user["city"] = "Beijing"    # 添加
user["age"] = 26            # 修改
value = user.get("email", "无")  # 安全取值，带默认值
user.pop("city")            # 删除

# 遍历
for key, value in user.items():
    print(key, value)
```

## 集合（set） {#set}

无序、不重复：

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b    # 并集 {1,2,3,4,5,6}
a & b    # 交集 {3,4}
a - b    # 差集 {1,2}
a ^ b    # 对称差 {1,2,5,6}

a.add(5)      # 添加
a.remove(5)   # 删除（不存在会报错）
```

## 推导式 {#comprehensions}

```python
# 列表推导式
squares = [x**2 for x in range(10)]         # [0,1,4,...,81]
evens = [x for x in range(20) if x % 2 == 0]

# 字典推导式
d = {x: x**2 for x in range(5)}             # {0:0, 1:1, 2:4, ...}

# 集合推导式
s = {x for x in "hello"}                    # {'h','e','l','o'}

# 生成器表达式（惰性求值，省内存）
gen = (x**2 for x in range(1000000))
```

## 小结 {#summary}

理解四种数据结构的特点（可变性、有序性、去重）能帮你选择正确的容器。下一章学习面向对象编程。
