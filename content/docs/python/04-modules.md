---
title: 第四章 模块、包与异常
linkTitle: 模块与异常
description: 导入机制、异常处理与上下文管理器
weight: 44
---

# 模块、包与异常

## 模块 {#modules}

一个 `.py` 文件就是一个模块：

```python
# utils.py
def add(a, b):
    return a + b

PI = 3.14159
```

```python
# main.py —— 导入方式
import utils               # 导入整个模块
utils.add(1, 2)

from utils import add      # 导入特定函数
add(1, 2)

from utils import *        # 导入所有（不推荐）
import utils as u          # 起别名
```

## 包 {#packages}

包是包含 `__init__.py` 的目录：

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

## 异常处理 {#exceptions}

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print("除数不能为零", e)
except (ValueError, TypeError) as e:
    print("类型或值错误", e)
except Exception as e:
    print("其他异常", e)
else:
    print("没有异常时执行", result)
finally:
    print("总是执行")
```

### 自定义异常 {#custom-exception}

```python
class InvalidAgeError(ValueError):
    pass

def set_age(age):
    if age < 0:
        raise InvalidAgeError("年龄不能为负")
    return age
```

## 上下文管理器 {#context-manager}

`with` 语句自动管理资源（如文件关闭）：

```python
# 打开文件，自动关闭
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 自定义上下文管理器
class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.cost = time.time() - self.start
        print(f"耗时 {self.cost:.2f}s")

with Timer():
    # 需要计时的代码
    time.sleep(1)
```

> [!TIP]
> 用 `with` 管理文件、数据库连接、锁等资源，避免忘记关闭导致泄漏。

## 小结 {#summary}

模块和包组织代码，异常处理让程序健壮，上下文管理器优雅地管理资源。下一章学习标准库与生态。
