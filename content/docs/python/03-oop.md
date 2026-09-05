---
title: 第三章 面向对象编程
linkTitle: 面向对象
description: Python 类、继承、封装与特殊方法
weight: 43
---

# 面向对象编程

## 定义类 {#class}

```python
class Dog:
    # 类属性（所有实例共享）
    species = "Canis familiaris"

    # 构造方法
    def __init__(self, name, age):
        self.name = name   # 实例属性
        self.age = age

    # 实例方法
    def bark(self):
        return f"{self.name} says woof!"

dog = Dog("Rex", 3)
print(dog.bark())       # "Rex says woof!"
print(dog.species)      # "Canis familiaris"
```

## 封装 {#encapsulation}

Python 用命名约定（而非强制）表示私有属性：

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance      # 单下划线：约定为受保护
        self.__secret = "hidden"     # 双下划线：名称改写

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

account = BankAccount(100)
account.deposit(50)
print(account.balance)   # 150（通过 property 访问）
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

class Dog(Animal):
    def speak(self):
        return f"{self.name} says woof"

# 多态：不同对象调用同一方法，行为不同
for a in [Cat("Kitty"), Dog("Rex")]:
    print(a.speak())
```

## 特殊方法（魔术方法） {#magic-methods}

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"Point({self.x}, {self.y})"   # 给人看

    def __repr__(self):
        return f"Point({self.x}, {self.y})"   # 给调试看

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1 == p2)       # True
print(p1 + Point(3, 4))  # Point(4, 6)
```

## 小结 {#summary}

Python 的面向对象灵活且简洁，`@property`、魔术方法让自定义类型像内置类型一样自然。下一章学习模块与异常。
