---
title: 第三章 函数与模块
linkTitle: 函数与模块
description: 函数定义、参数类型（位置/关键字/仅位置/仅关键字）、作用域 LEGB、lambda、装饰器进阶与模块导入机制
weight: 43
---

# 函数与模块

函数封装可复用逻辑，模块与包则把代码组织成清晰的结构。本章深入参数规则、作用域、装饰器和导入机制这些日常开发高频且易错的部分。

## 定义函数 {#def}

```python
def greet(name, greeting="Hello"):
    """文档字符串：返回一句问候语"""
    return f"{greeting}, {name}"

greet("Alice")                 # "Hello, Alice"
greet("Bob", greeting="Hi")    # "Hi, Bob"
```

## 参数类型 {#parameters}

Python 的参数体系非常灵活，但有严格的**顺序规则**：位置参数 → 仅位置参数(`/`) → 普通参数 → `*args`/可变参数 → 仅关键字参数(`*`) → `**kwargs`。

```python
# 完整示例（从左到右顺序不可乱）
def func(pos1, pos2, /, pos_or_kw, *, kw1, kw2):
    print(pos1, pos2, pos_or_kw, kw1, kw2)

# pos1, pos2 是仅位置参数（/ 之前），只能用位置传
# pos_or_kw 位置或关键字均可
# kw1, kw2 是仅关键字参数（* 之后），必须用关键字传
func(1, 2, 3, kw1=4, kw2=5)
func(1, 2, pos_or_kw=3, kw1=4, kw2=5)

# 仅位置参数 /（Python 3.8+，如内置函数 sorted(seq, /, ...)）
def add(x, y, /):
    return x + y
add(1, 2)          # OK
# add(x=1, y=2)    # TypeError：x, y 是仅位置参数

# 仅关键字参数 *（* 之后的参数必须关键字传入）
def make(x, *, y=0):
    return x + y
make(1, y=2)       # 3
# make(1, 2)       # TypeError
```

### 默认参数只求值一次（可变默认参数坑）

与第一章提到的陷阱一致：默认参数在**函数定义时**求值并绑定，多次调用共享同一对象。

```python
# 反例
def append_to(elem, target=[]):
    target.append(elem)
    return target
append_to(1)   # [1]
append_to(2)   # [1, 2]  —— 共享同一个列表！

# 正确写法：用 None 占位 + 内部初始化
def append_to(elem, target=None):
    if target is None:
        target = []
    target.append(elem)
    return target
```

## 解包传参 {#unpacking-args}

调用函数时用 `*` 展开序列、`**` 展开字典：

```python
def f(a, b, c):
    return a + b + c

args = (1, 2, 3)
f(*args)               # 6，等价于 f(1, 2, 3)

data = {"a": 1, "b": 2, "c": 3}
f(**data)              # 6

# * 也可用于把剩余位置参数收拢
def g(a, *rest):
    print(a, rest)
g(1, 2, 3, 4)         # 1 (2, 3, 4)

# 注意：同一调用中 *args 和 **kwargs 的出现顺序与数量要匹配参数
# f(*(1,2), *(3,)) 合法；f(*(1,2,3,4)) 会报参数过多
```

## 作用域：LEGB 规则 {#scope}

Python 查找变量按 **L**ocal → **E**nclosing（闭包外层）→ **G**lobal → **B**uiltin 顺序。

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

# 修改闭包外层变量需用 nonlocal
def outer():
    count = 0
    def inner():
        nonlocal count
        count += 1
        return count
    return inner

f = outer()
f()                 # 1
f()                 # 2
```

> 经验法则：尽量**避免**用 `global`/`nonlocal` 修改外层状态，优先用返回值或类属性传递状态，可维护性更好。

## 函数是对象 {#functions-as-objects}

在 Python 中函数是**一等公民**，可赋值、存入容器、作为参数传递：

```python
def add(a, b):
    return a + b

# 赋值给变量（注意不带括号，否则是调用结果）
op = add
op(1, 2)            # 3

# 放进字典做「分派表」
ops = {"+": add, "-": lambda a, b: a - b}
ops["+"](5, 3)     # 8

# 作为参数（回调/高阶函数）
def apply(fn, x, y):
    return fn(x, y)
apply(add, 2, 3)    # 5
```

## 装饰器进阶 {#decorators-advanced}

装饰器是「接收函数、返回函数」的高阶函数，用于横切关注点（日志、计时、鉴权等）。

### functools.wraps 保留元信息

```python
from functools import wraps

def log_calls(func):
    @wraps(func)            # 关键：把原函数名、文档串复制到 wrapper
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    """加法"""
    return a + b

add.__name__      # 'add'（没有 @wraps 会显示为 'wrapper'）
add.__doc__       # '加法'
```

### 带参数的装饰器（三层嵌套）

```python
from functools import wraps

def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def hello():
    print("hi")
# 等价于 hello = repeat(3)(hello)
```

### functools.lru_cache 缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)   # 无缓存是指数级，加了缓存接近线性
```

### functools.partial 偏函数

```python
from functools import partial
from functools import partial

# 固定部分参数，生成新函数
int_base2 = partial(int, base=2)
int_base2("1010")     # 10

# 常用于给回调预设参数
def handler(prefix, msg):
    print(f"[{prefix}] {msg}")
on_error = partial(handler, "ERROR")
on_error("失败")       # [ERROR] 失败
```

## lambda 表达式 {#lambda}

匿名、单行函数，适合简短回调。**只能写单个表达式，不能包含 `return`/`if` 语句块/`for` 等**。

```python
square = lambda x: x ** 2
square(5)                       # 25

nums = [3, 1, 4, 2]
sorted(nums, key=lambda n: -n)  # 降序 [4, 3, 2, 1]

# 与 map / filter 配合（但多数场景推导式更清晰）
list(map(lambda x: x*2, [1, 2, 3]))     # [2, 4, 6]
list(filter(lambda x: x > 1, [1, 2, 3]))# [2, 3]

# 等价、更 Pythonic 的推导式
[x*2 for x in [1, 2, 3]]
[x for x in [1, 2, 3] if x > 1]
```

> 坑：在循环里用 `lambda` 捕获循环变量时，可能因为**闭包延迟绑定**拿到错误值：
> ```python
> funcs = [lambda: i for i in range(3)]
> [f() for f in funcs]              # [2, 2, 2] —— 都引用了最终的 i=2
> # 修正：用默认参数立即绑定
> funcs = [lambda i=i: i for i in range(3)]
> [f() for f in funcs]              # [0, 1, 2]
> ```

## 模块 {#modules}

一个 `.py` 文件即一个模块。导入时 Python 会搜索 `sys.path` 中的目录。

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

### 导入搜索路径与缓存

```python
import sys
sys.path        # 模块搜索路径列表，第一项通常是当前脚本目录
# 想临时加入路径：sys.path.insert(0, "某个目录")

import utils
import sys
sys.modules["utils"]   # 已导入的模块缓存在这里；重复 import 不会重新执行模块代码
```

### `__init__.py` 与包

```text
mypackage/
├── __init__.py      # 标记为包，可放初始化代码或 __all__
├── core.py
└── utils.py
```

```python
from mypackage import core
from mypackage.core import some_function

# 相对导入：在包内部使用，. 表示当前包，.. 表示上一级
# 仅在作为包导入时有效，不能作为主脚本直接运行
from . import core
from .utils import helper
```

### 循环导入与解法

```text
# 反例：a.py 导入 b，b.py 又导入 a，运行时会 ImportError
# a.py: from b import foo
# b.py: from a import bar
```

解法：
1. 把导入放到函数内部（延迟导入）；
2. 合并/重构公共代码到一个独立模块；
3. 用 `import a`（导入模块而非 `from a import x`）减少符号依赖。

## __name__ == "__main__" 的意义 {#main-guard}

让模块既能导入复用，又能独立运行：

```python
def main():
    print("程序入口")

# 直接运行本文件时 __name__ 为 "__main__"，被导入时则不是
if __name__ == "__main__":
    main()
```

- 作为脚本直接运行：`python main.py` → `__name__ == "__main__"`，执行 `main()`。
- 被其他模块 `import main` → `__name__ == "main"`，**不**执行 `main()`，只提供函数/类。

这是编写可复用、可测试代码的关键约定。

## 小结 {#summary}

本章覆盖了 Python 函数最易混淆的细节：仅位置 `/` 与仅关键字 `*` 参数、默认参数只求值一次的可变默认参数坑、LEGB 作用域与 `nonlocal`、函数作为一等对象的用法；装饰器部分补充了 `functools.wraps`（保留元信息）、带参装饰器三层结构、`lru_cache` 与 `partial`；模块部分讲清了 `sys.path`、导入缓存 `sys.modules`、相对导入与循环导入解法，以及 `if __name__ == "__main__"` 的作用。下一章进入面向对象与异常、文件处理。
