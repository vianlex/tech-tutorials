---
title: 第五章 进阶与最佳实践
linkTitle: 进阶与最佳实践
description: 推导式、生成器、装饰器入门、常用标准库、虚拟环境、调试测试与 Pythonic 实践
weight: 45
---

# 进阶与最佳实践

掌握这些进阶特性，能让代码更简洁、高效且符合社区惯例。

## 推导式 {#comprehensions}

一行生成容器，可读性优于手写循环：

```python
squares = [x**2 for x in range(10)]          # 列表推导式
evens = [x for x in range(20) if x % 2 == 0] # 带条件
d = {x: x**2 for x in range(5)}              # 字典推导式
s = {x for x in "hello"}                     # 集合推导式 {'h','e','l','o'}
```

## 生成器 {#generators}

用 `()` 延迟计算，省内存、可处理无限序列：

```python
gen = (x**2 for x in range(1_000_000))       # 生成器表达式
next(gen)                                    # 逐个取值

def count_up():
    n = 0
    while True:
        yield n                              # yield 暂停并返回
        n += 1
for i in count_up():
    if i > 3: break
    print(i)                                 # 0 1 2 3
```

## 装饰器入门 {#decorators}

在不改原函数的基础上扩展行为：

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}，参数 {args}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(1, 2)        # 打印日志并返回 3
```

## 常用标准库 {#stdlib}

```python
from datetime import datetime
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))     # 日期时间格式化

import json
data = {"name": "Alice", "age": 25}
text = json.dumps(data, ensure_ascii=False)  # 序列化
obj = json.loads(text)                        # 反序列化

import re
re.findall(r"\d+", "订单号 123 和 456")       # ['123', '456']

from pathlib import Path
p = Path("data") / "file.txt"                 # 跨平台路径拼接
p.exists(); p.read_text(encoding="utf-8")     # 存在判断/读取文本
```

## 虚拟环境与 pip {#venv}

隔离项目依赖，是工程化基础：

```bash
python -m venv venv            # 创建虚拟环境

# 激活（Windows）
venv\Scripts\activate
# 激活（macOS/Linux）
source venv/bin/activate

pip install requests           # 安装依赖
pip freeze > requirements.txt  # 导出依赖清单
pip install -r requirements.txt
```

## 调试与测试简介 {#debug-test}

```python
# 断言：条件不满足立即抛 AssertionError
assert 2 + 2 == 4, "数学出错了"

# 用内置 pdb 或 IDE 断点调试
import pdb; pdb.set_trace()

# 简单单元测试（标准库 unittest）
import unittest
class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
```

## Pythonic 最佳实践 {#best-practices}

- 用推导式、`enumerate`、`zip` 替代手写下标循环
- 优先 `f-string` 格式化、优先 `pathlib` 处理路径
- 用 `with` 管理资源、用异常而非返回错误码
- 命名清晰（`snake_case` 函数/变量、`CapWords` 类）
- 用 `if __name__ == "__main__"` 隔离可执行入口
- 保持函数短小单一职责，写必要的文档字符串

## 小结 {#summary}

推导式、生成器、装饰器让 Python 代码简洁而强大；善用标准库、`venv` 与测试则保障工程质量。遵循 Pythonic 惯例，持续动手实践，是掌握 Python 的关键。
