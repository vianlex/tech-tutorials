---
title: 第四章 面向对象与异常
linkTitle: 面向对象与异常
description: 类与实例、__slots__、类方法/静态方法、@property、名称改写、继承与 MRO、@dataclass、特殊方法、异常体系、上下文管理器与文件读写
weight: 44
---

# 面向对象与异常

面向对象把数据与行为封装为类，异常处理则让程序在出错时依然稳健。本章深入日常开发最常用的 OOP 细节与异常机制。

## 类与实例 {#class}

```python
class Dog:
    species = "Canis familiaris"   # 类属性，所有实例共享

    def __init__(self, name, age): # 构造方法
        self.name = name           # 实例属性
        self.age = age

    def bark(self):                # 实例方法，第一个参数是 self
        return f"{self.name} says woof!"

dog = Dog("Rex", 3)
print(dog.bark())                 # "Rex says woof!"
print(dog.species)                # "Canis familiaris"
```

### __slots__ 省内存

默认实例用 `__dict__` 存储属性（灵活但占内存）。`__slots__` 用固定槽位替代，省内存、禁止随意添加属性，适合大量实例的场景。

```python
class Point:
    __slots__ = ("x", "y")        # 只允许这两个属性
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
p.z = 3          # AttributeError：不允许添加 slots 之外的属性
# 注意：有 __slots__ 的类不再有 __dict__，也无法动态挂属性
```

### @classmethod 与 @staticmethod

```python
class User:
    count = 0

    def __init__(self, name):
        self.name = name
        User.count += 1

    @classmethod
    def from_config(cls, cfg):     # 第一个参数是类本身 cls，可被子类继承
        return cls(cfg["name"])

    @staticmethod
    def is_valid_name(name):       # 与普通函数无异，只是逻辑上归属类，无 cls/self
        return bool(name) and name[0].isalpha()

# 调用
u = User.from_config({"name": "Alice"})
User.is_valid_name("Bob")          # True
```

- `@classmethod`：需要访问类（构造其他实例、操作类属性）时用，参数是 `cls`。
- `@staticmethod`：与类相关但不需要 `self`/`cls` 时用，纯逻辑工具方法。

### @property 的 setter/deleter

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance          # 单下划线表示受保护（约定，非强制）

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value >= 0:
            self._balance = value
        else:
            raise ValueError("余额不能为负")

    @balance.deleter
    def balance(self):
        del self._balance

acc = BankAccount(100)
acc.balance = 150                  # 通过 setter 修改
print(acc.balance)                # 150
del acc.balance                    # 调用 deleter
```

### 私有属性与名称改写（name mangling）

单下划线 `_x` 只是约定（外部仍可访问）；双下划线 `__x` 会触发**名称改写**，防止子类意外覆盖。

```python
class Base:
    def __init__(self):
        self.__secret = 42        # 名称改写为 _Base__secret

b = Base()
# b.__secret                    # AttributeError
b._Base__secret                 # 42（改写后的真实名字，仍可强制访问）

# 用途：避免子类定义同名属性时冲突
class Sub(Base):
    def __init__(self):
        super().__init__()
        self.__secret = 99       # 实际是 _Sub__secret，与父类的 _Base__secret 不冲突
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

### super() 与 MRO

```python
class A:
    def greet(self):
        return "A"

class B(A):
    def greet(self):
        return "B -> " + super().greet()

B().greet()      # "B -> A"

# 多继承的方法解析顺序（MRO）：按 C3 线性化，子类优先、从左到右
class X: pass
class Y: pass
class Z(X, Y): pass
Z.__mro__        # (Z, X, Y, object) —— 调用方法时按此顺序查找
# 用 super() 能保证 MRO 链上的每个类只被调用一次（协作式多重继承的关键）
```

### isinstance / issubclass

```python
cat = Cat("Kitty")
isinstance(cat, Cat)        # True
isinstance(cat, Animal)     # True（子类实例也是父类类型）
isinstance(cat, Dog)        # False
issubclass(Cat, Animal)     # True
```

## 数据类 @dataclass {#dataclass}

Python 3.7+ 的 `@dataclass` 自动生成 `__init__`/`__repr__`/`__eq__` 等样板代码。

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: int
    y: int
    tags: list = field(default_factory=list)   # 用工厂函数避免可变默认值坑
    # 不要写 tags: list = [] ！那会是所有实例共享的可变默认

p1 = Point(1, 2)
p2 = Point(1, 2)
p1 == p2            # True（自动生成 __eq__）
p1                  # Point(x=1, y=2, tags=[])

# frozen=True 使实例不可变（类似命名元组，但仍是类）
@dataclass(frozen=True)
class Const:
    val: int
# Const(1).val = 2   # FrozenInstanceError
```

> 为什么用 `field(default_factory=list)` 而非 `tags: list = []`？原因同第一章可变默认参数陷阱——默认参数只求值一次，所有实例会共享同一个列表。用工厂函数，每次实例化都新建一个列表。

## 特殊方法（魔法方法） {#magic-methods}

`__init__`/`__str__`/`__repr__` 让自定义类型像内置类型一样自然。

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):           # print()、str() 使用，给人看
        return f"Point({self.x}, {self.y})"

    def __repr__(self):          # 调试/交互式使用，给开发者看（理想应可重建对象）
        return f"Point({self.x!r}, {self.y!r})"

    def __eq__(self, other):     # 支持 == 比较
        return self.x == other.x and self.y == other.y

    def __len__(self):           # len(obj)
        return 2

    def __getitem__(self, idx):  # obj[idx]
        return (self.x, self.y)[idx]

    def __contains__(self, item):# item in obj
        return item in (self.x, self.y)

    def __iter__(self):          # 可迭代
        yield self.x
        yield self.y

    def __call__(self):          # 实例可像函数一样调用
        return f"called: {self.x},{self.y}"

p1 = Point(1, 2)
print(p1)                        # Point(1, 2)
print(p1 == Point(1, 2))         # True
print(len(p1))                   # 2
print(p1[0])                     # 1
print(1 in p1)                   # True
list(p1)                         # [1, 2]
p1()                             # "called: 1,2"
```

> 约定：`__repr__` 应尽量返回能重建对象的字符串；`__str__` 缺失时 Python 会回退到 `__repr__`。

## 异常处理 {#exceptions}

### 异常继承体系

```text
BaseException
├── KeyboardInterrupt   # Ctrl+C，通常不应捕获
├── SystemExit         # sys.exit() 触发
└── Exception          # 绝大多数业务异常都继承它
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── IndexError
    ├── FileNotFoundError
    └── RuntimeError
```

> 捕获时尽量捕获**具体的**异常，而不是笼统地 `except Exception`，否则可能掩盖真正的 bug（如把 `KeyboardInterrupt` 也吃掉，导致程序无法中断）。

### try / except / else / finally 完整语义

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print("除数不能为零", e)
except (ValueError, TypeError) as e:   # 多个异常合并捕获
    print("值或类型错误", e)
except Exception as e:                 # 兜底，必须放最后
    print("其他异常", e)
else:
    print("无异常时执行", result)       # 仅在 try 成功（无异常）时运行
finally:
    print("无论是否异常都会执行")        # 常用于清理资源，即使发生异常也执行
```

### 捕获顺序：具体的在前

```python
try:
    int("abc")
except ValueError:        # 先捕获具体异常
    print("转换失败")
# except Exception 必须放在更具体的之后，否则前面永远命中不到
```

### raise ... from 链式异常

保留原始异常上下文，便于调试：

```python
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        raise RuntimeError("配置加载失败") from e   # 链上保留原始 OSError

# 若不想保留上下文，用 raise ... from None
```

### 自定义异常最佳实践

```python
class InvalidAgeError(ValueError):
    """年龄非法时抛出，继承语义最接近的官方异常。"""
    pass

def set_age(age):
    if age < 0:
        raise InvalidAgeError("年龄不能为负")
    return age
```

- 继承最贴切的内置异常（如校验失败继承 `ValueError`）；
- 名字以 `Error` 结尾；
- 保持异常类「轻」——不要塞入复杂逻辑。

## with 与上下文管理器 {#context-manager}

`with` 的底层是对象的 `__enter__` / `__exit__` 方法，保证「进入时获取资源、退出时一定释放」。

```python
class MyResource:
    def __enter__(self):
        print("获取资源")
        return self              # with ... as 拿到的就是它的返回值
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")
        return False             # 返回 False（或 None）则异常继续向外抛；True 则吞掉异常

with MyResource() as r:
    print("使用中")
# 输出：获取资源 -> 使用中 -> 释放资源
```

### contextlib.contextmanager 简化

用生成器 + 装饰器，几行实现上下文管理器：

```python
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    yield                        # yield 之前是 __enter__，之后是 __exit__
    print(f"</{name}>")

with tag("div"):
    print("内容")
# <div> 内容 </div>

# ExitStack：动态管理多个上下文
from contextlib import ExitStack
with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in ["a.txt", "b.txt"]]
```

## 文件读写 {#file-io}

`with open(...) as f` 自动关闭文件，避免资源泄漏。

```python
# 写入
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("你好，Python\n")
    f.writelines(["第一行\n", "第二行\n"])

# 读取
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()            # 读全部
    # 或逐行：for line in f: print(line)
    f.seek(0)                     # 移动指针到开头
    first = f.readline()          # 读一行（含换行符）
    lines = f.readlines()         # 读全部行，返回列表

# 打开模式
# r 读（默认）  w 写（截断）  a 追加  x 新建（已存在则报错）
# b 二进制（rb/wb）  + 读写（r+/w+）
with open("img.png", "rb") as f:
    data = f.read()
f.tell()                          # 当前指针位置（字节数）
```

### json 读写

```python
import json
data = {"name": "Alice", "age": 25}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)   # ensure_ascii=False 保留中文

with open("data.json", "r", encoding="utf-8") as f:
    obj = json.load(f)             # 反序列化
```

### pathlib 替代 os.path

```python
from pathlib import Path
p = Path("data") / "file.txt"      # 跨平台路径拼接（推荐）
p.exists()                         # 是否存在
p.read_text(encoding="utf-8")      # 读取文本
p.write_text("hi", encoding="utf-8")
p.name, p.suffix, p.parent         # 文件名 / 后缀 / 父目录
list(Path(".").glob("*.py"))        # 当前目录所有 .py 文件
# 比 os.path.join / os.listdir 更直观、可移植
```

## 小结 {#summary}

本章深入了 OOP 的实用细节：`__slots__` 省内存、`@classmethod`/`@staticmethod` 的分工、`@property` 的 setter/deleter、双下划线名称改写、`super()` 与 MRO 多继承、`@dataclass` 自动生成样板（用 `field(default_factory=...)` 规避可变默认坑）；异常部分讲清了继承体系、`except` 捕获顺序、`raise ... from` 链式异常与自定义异常；上下文管理器与 `pathlib`/`json` 文件操作也一并覆盖。下一章学习推导式、生成器、装饰器应用与最佳实践。
