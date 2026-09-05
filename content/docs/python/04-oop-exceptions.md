---
title: 第四章 面向对象与异常
linkTitle: 面向对象与异常
description: 类与实例、继承、特殊方法、@property，以及异常处理、上下文管理器与文件读写
weight: 44
---

# 面向对象与异常

面向对象把数据与行为封装为类，异常处理则让程序在出错时依然稳健。

## 类与实例 {#class}

```python
class Dog:
    species = "Canis familiaris"   # 类属性，所有实例共享

    def __init__(self, name, age): # 构造方法
        self.name = name           # 实例属性
        self.age = age

    def bark(self):                # 实例方法
        return f"{self.name} says woof!"

dog = Dog("Rex", 3)
print(dog.bark())                 # "Rex says woof!"
print(dog.species)                # "Canis familiaris"
```

## 继承 {#inheritance}

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        raise NotImplementedError

class Cat(Animal):
    def speak(self):
        return f"{self.name} says meow"

# 多态：同一调用，不同行为
for a in [Cat("Kitty"), Dog("Rex")]:
    print(a.speak())
```

## 特殊方法 {#magic-methods}

`__init__`/`__str__`/`__repr__` 让自定义类型像内置类型一样自然：

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):           # print()、str() 使用，给人看
        return f"Point({self.x}, {self.y})"

    def __repr__(self):          # 调试/交互式使用，给开发者看
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):     # 支持 == 比较
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
print(p1)                        # Point(1, 2)
print(p1 == Point(1, 2))         # True
```

## @property {#property}

将方法变为只读（或受控）属性，隐藏内部实现：

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance          # 单下划线表示受保护

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value >= 0:
            self._balance = value

acc = BankAccount(100)
acc.balance = 150                  # 通过 setter 修改
print(acc.balance)                 # 150
```

## 异常处理 {#exceptions}

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print("除数不能为零", e)
except (ValueError, TypeError) as e:
    print("值或类型错误", e)
except Exception as e:             # 兜底，放在最后
    print("其他异常", e)
else:
    print("无异常时执行", result)  # 仅在 try 成功时运行
finally:
    print("无论是否异常都会执行")   # 常用于清理
```

## 主动抛出异常 {#raise}

```python
class InvalidAgeError(ValueError):
    pass

def set_age(age):
    if age < 0:
        raise InvalidAgeError("年龄不能为负")
    return age

# 常见内置异常：ValueError / TypeError / KeyError / IndexError / FileNotFoundError
```

## with 与文件读写 {#file-io}

`with` 上下文管理器自动关闭文件，避免资源泄漏：

```python
# 写入
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("你好，Python\n")

# 读取
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()            # 读全部
    # 或逐行：for line in f: print(line)
```

## 小结 {#summary}

类与继承、特殊方法、`@property` 让自定义类型既灵活又自然；`try/except/finally` 与 `with` 则保证程序健壮、资源安全。下一章学习推导式、生成器、装饰器与最佳实践。
