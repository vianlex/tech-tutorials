---
title: 第六章 类型标注
linkTitle: 类型标注
description: Python 类型标注基础、typing 模块、泛型与运行时校验
weight: 46
---

# 类型标注

类型标注（type hints）让 Python 在不改变运行时行为的前提下，更易读、更易被工具理解。本章覆盖从变量标注到泛型、协议与运行时校验的完整链路。

## 为什么用类型标注 {#why-type-hints}

类型标注解决「可读与可维护」，而非「运行正确」：

- **可读性**：函数签名一眼看出参数与返回值类型。
- **IDE 补全**：VS Code、PyCharm 依据标注提供精准补全与提示。
- **静态检查**：`mypy`、`pyright`、`ruff` 能在运行前发现类型错误。

核心事实：**标注只是提示，运行时不强制**。下面代码能跑，但类型检查器会报错：

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")   # 运行时不报错，mypy 会提示类型不匹配
```

## 变量与函数标注 {#variable-function}

变量用 `名: 类型`，函数参数用 `参数: 类型`、返回值用 `-> 类型`：

```python
x: int = 1
name: str = "Alice"
items: list[int] = []

def add(a: int, b: int) -> int: ...
def greet(name: str) -> str: ...
def log(msg: str) -> None: ...   # 无返回值标注为 None
```

也可用「先声明后赋值」（类属性常见）：

```python
count: int            # 仅声明类型，暂不赋值
count = 0

class User:
    name: str         # 类属性类型声明
    age: int = 0
```

## 内置容器泛型 {#builtin-generics}

Python 3.9+ 直接在 `list`/`dict`/`tuple`/`set` 上用泛型，无需旧式 `typing.List`：

```python
# 推荐（3.9+）
nums: list[int] = [1, 2, 3]
scores: dict[str, int] = {"Alice": 90}
pair: tuple[int, str] = (1, "one")
unique: set[int] = {1, 2, 3}

# 旧式（不推荐）
from typing import List
old: List[int] = [1, 2, 3]
```

`tuple` 支持定长异构与变长同构：

```python
point: tuple[float, float] = (1.0, 2.0)       # 定长异构
coords: tuple[float, ...] = (1.0, 2.0, 3.0)   # 变长同构
```

## 联合类型 {#union-types}

多类型之一用联合类型。3.10+ 用 `|`，比旧式 `Union` 直观：

```python
# 推荐（3.10+）
def f(x: int | str) -> None: ...

# 旧式
from typing import Union
def g(x: Union[int, str]) -> None: ...
```

可空用 `X | None`，替代旧式 `Optional[X]`：

```python
def find_user(uid: int) -> dict | None: ...   # 推荐
from typing import Optional
def old(uid: int) -> Optional[dict]: ...        # 旧式
```

## typing 常用类型 {#typing-common}

```python
from typing import Any, Callable, Iterable, Sequence, Mapping, Literal

x: Any = 1              # 任意类型，绕过检查（应少用）

op: Callable[[int, int], int] = lambda a, b: a + b   # 可调用对象

def total(xs: Iterable[int]) -> int: ...    # 抽象接口，比 list 更灵活
def first(xs: Sequence[int]) -> int: ...
def get(d: Mapping[str, int], k: str) -> int: ...

Mode = Literal["read", "write", "append"]   # 限定取值
def open_file(mode: Mode) -> None: ...
```

`Any` 会失去静态检查，`Literal` 把魔法字符串变可检查。

## TypedDict 与结构化字典 {#typeddict}

`TypedDict` 描述「键固定、各键值类型不同」的字典：

```python
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int
    vip: bool

u: User = {"name": "Alice", "age": 25, "vip": True}
```

## TypeAlias 与 Final {#typealias-final}

类型别名用 `TypeAlias`（3.10+）；`Final` 表示不可重新赋值：

```python
from typing import TypeAlias, Final

Vector: TypeAlias = list[float]
def norm(v: Vector) -> float: ...

MAX_RETRY: Final = 3          # 类型检查器阻止后续修改
```

## 泛型函数与类 {#generics}

`TypeVar` 表达「同一类型贯穿多处」：

```python
from typing import TypeVar

T = TypeVar("T")

def first_item(xs: list[T]) -> T | None:
    return xs[0] if xs else None
```

泛型类：3.12+ 原生 `class Stack[T]`，旧版用 `Generic[T]`：

```python
class Stack[T]:                # 3.12+ 原生语法
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, x: T) -> None: self._items.append(x)
    def pop(self) -> T | None:
        return self._items.pop() if self._items else None
```

## Protocol 结构化类型 {#protocol}

`Protocol` 把「鸭子类型」形式化：具备所需方法即合规，无需继承：

```python
from typing import Protocol

class Renderer(Protocol):
    def render(self) -> str: ...

def show(r: Renderer) -> None:
    print(r.render())
```

## cast 与运行时校验 {#cast-assert}

`typing.cast` 只告诉类型检查器真实类型，运行时不转换：

```python
from typing import cast

value: object = "hello"
text = cast(str, value)        # 运行时不转换，仅影响检查
```

真正运行时校验用 `isinstance`：

```python
def double(x: object) -> int:
    if not isinstance(x, int):
        raise TypeError("需要 int")
    return x * 2
```

## NewType 名义类型 {#newtype}

`NewType` 创建与底层类型不同、运行值不变的新类型，区分不该混用的量：

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def get_user(uid: UserId) -> str: ...

uid = UserId(42)
oid = OrderId(42)
get_user(uid)
# get_user(oid)   # 检查器拒绝：虽底层都是 int，但类型不同
```

## dataclass 与类型标注结合 {#dataclass}

`@dataclass` 与标注天然契合，自动生成构造与表示：

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    label: str = "原点"

print(Point(1.0, 2.0))         # Point(x=1.0, y=2.0, label='原点')
```

## 运行时校验工具 {#runtime-validation}

```python
from typing import get_type_hints

def f(a: int, b: str) -> bool: ...

print(get_type_hints(f))       # 反射获取标注
```

常用第三方工具：

- **`typeguard`**：按标注在运行时检查参数/返回值。
- **`pydantic`**：数据校验与解析利器（FastAPI 教程深入讲解）。
- **`get_type_hints`**：框架做元编程的常用手段。

## TYPE_CHECKING 避免循环导入 {#type-checking}

`TYPE_CHECKING` 运行时为 `False`、检查时为 `True`，用于「只为标注导入」：

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import User     # 运行时不导入，避免循环依赖

def show(u: "User") -> None: ...  # 运行时用字符串延迟引用
```

## from __future__ import annotations {#future-annotations}

3.7+ 的 `from __future__ import annotations` 让所有标注变为延迟字符串，解决循环引用：

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import User

class Post:
    author: User            # User 未定义也不会报错
```

## 实用建议 {#practical-tips}

- **缺标注的库**：装 `types-requests` 等 stubs 补充类型信息。
- **mypy 入门**：`mypy your_module.py`；更严格用 `mypy --strict`。
- **渐进式标注**：先标公开 API，内部逐步补全。
- **配置文件**：在 `pyproject.toml` 的 `[tool.mypy]` 固化规则。
- **保持克制**：少用 `Any`，标注为人服务而非炫技。

## 小结 {#summary}

类型标注不改变运行时行为，却能提升可读性并经工具在运行前捕获错误。善用 `X | None`、`list[int]`、泛型与 `Protocol`，配合 `TYPE_CHECKING` 与 `from __future__ import annotations` 处理边界，再以渐进式策略融入开发。