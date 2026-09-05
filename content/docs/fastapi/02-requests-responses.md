---
title: 第二章 请求与响应
linkTitle: 请求与响应
description: Pydantic v2 模型、请求体、参数校验与响应模型
weight: 102
---

# 请求与响应

本章围绕数据建模展开：用 Pydantic v2 定义请求体，借助 `Field` 与 `Query` / `Path` 完成参数校验，并通过响应模型约束返回结构，同时指定 HTTP 状态码。

## Pydantic v2 模型 {#pydantic-model}

Pydantic v2 通过类型注解完成数据解析与校验，是 FastAPI 请求体的核心：

```python
from pydantic import BaseModel


# 继承 BaseModel 即可作为数据模型
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []
```

`str | None` 为 Python 3.10+ 的联合类型写法，等价于 `Optional[str]`。

## 请求体 {#request-body}

将模型类型作为函数参数，FastAPI 会自动读取 JSON 请求体并完成校验：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None


# 声明 Item 类型参数即代表接收请求体
@app.post("/items/")
def create_item(item: Item):
    return item
```

发送请求：

```bash
curl -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name": "键盘", "price": 199.0, "tax": 19.9}'
```

## 字段校验 {#field-validation}

使用 `Field` 对模型字段附加约束（长度、范围、示例等）：

```python
from pydantic import BaseModel, Field


class Item(BaseModel):
    # 名称限制 1~50 个字符，并给出示例
    name: str = Field(min_length=1, max_length=50, examples=["机械键盘"])
    # 价格必须为正数
    price: float = Field(gt=0, description="商品价格")
    # 标签最多 5 个
    tags: list[str] = Field(default_factory=list, max_length=5)
```

## 路径与查询参数校验 {#param-validation}

除模型字段外，路径与查询参数也能用 `Path` / `Query` 校验：

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(
    item_id: int = Path(title="商品ID", ge=1),
    q: str | None = Query(default=None, min_length=3, max_length=50),
):
    return {"item_id": item_id, "q": q}
```

`ge=1` 表示大于等于 1；校验失败时自动返回 422 与详细错误。

## 响应模型 {#response-model}

用 `response_model` 约束返回结构，多余字段会被自动过滤：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name: str
    price: float
    secret: str  # 不应返回给客户端


class ItemOut(BaseModel):
    name: str
    price: float


@app.post("/items/", response_model=ItemOut)
def create_item(item: ItemIn):
    # secret 字段不会被序列化进响应
    return item
```

## 状态码 {#status-code}

通过 `status_code` 指定成功响应的 HTTP 状态码：

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item():
    return {"created": True}


# 等价写法：直接传数字
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    return None
```

## 小结 {#summary}

本章使用 Pydantic v2 完成了请求体建模与字段校验，并对路径、查询参数施加了约束。同时学会了用响应模型过滤输出、用 `status_code` 控制 HTTP 状态。下一章将深入依赖注入机制与中间件、CORS 等横切能力。
