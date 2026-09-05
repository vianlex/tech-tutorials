---
title: 第一章 基础与控制流
linkTitle: 基础与控制流
description: Python 变量、数据类型、运算符、输入输出与条件循环控制流
weight: 41
---

# 基础与控制流

Python 以缩进划分代码块，语法简洁易读，是入门编程的良好选择。

## 变量与类型 {#variables}

Python 是**动态类型**语言，变量无需声明类型，赋值即创建：

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
```

## 基本类型 {#types}

```python
# 数字
x = 10          # int
y = 3.14        # float
z = 1 + 2j      # complex 复数

# 字符串：单引号、双引号等价，三引号表示多行
s1 = 'hello'
s3 = """多行
字符串"""

# 布尔值参与运算时 True=1, False=0
True + True     # 2
```

## 运算符 {#operators}

```python
# 算术
a = 7 // 2      # 3  整除
b = 7 % 2       # 1  取余
c = 2 ** 10     # 1024 幂

# 比较与逻辑
3 < 5 and 5 < 10    # True
3 < 5 or 5 > 10     # True
not (3 > 5)         # True

# 成员与身份
"a" in "cat"        # True
x = [1]; y = x; y is x   # True（同一对象）
[1] == [1]          # True（值相等但非同一对象）
```

## 输入输出 {#io}

```python
name = input("请输入你的名字：")   # 读取用户输入，返回 str
print("你好", name)

# 用 f-string 拼接输出
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

# 三元表达式
status = "成年" if age >= 18 else "未成年"
```

## 循环 {#loops}

```python
# for：遍历可迭代对象
for i in range(5):        # 0,1,2,3,4
    print(i)

for item in ["a", "b", "c"]:
    print(item)

# while：条件为真时持续
count = 0
while count < 3:
    print(count)
    count += 1
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

## 小结 {#summary}

Python 用缩进组织代码块，变量动态类型、运算符丰富直观；`if/for/while` 配合 `break/continue` 构成完整的控制流。下一章学习 Python 强大的内置数据结构和字符串处理。
