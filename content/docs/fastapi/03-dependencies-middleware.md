---
title: 第三章 依赖注入与中间件
linkTitle: 依赖注入与中间件
description: Depends、数据库依赖示例、中间件、CORS 与异常处理
weight: 103
---

# 依赖注入与中间件

本章学习 FastAPI 的依赖注入系统 `Depends`，用它将数据库连接、公共逻辑等共享能力解耦复用；并了解中间件、CORS 配置与全局异常处理。

## 依赖注入基础 {#depends}

`Depends` 把可调用对象声明为依赖，FastAPI 会自动调用并注入返回值：

```python
from fastapi import Depends, FastAPI

app = FastAPI()


# 这是一个依赖函数
def get_query_token(q: str | None = None):
    return {"q": q}


@app.get("/items/")
def read_items(commons: dict = Depends(get_query_token)):
    # commons 即为依赖的返回值
    return {"items": [], "commons": commons}
```

## 数据库依赖示例 {#db-dependency}

用依赖在请求级别管理数据库会话，保证每个请求独立且自动关闭：

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

app = FastAPI()

# 创建同步引擎与会话工厂
engine = create_engine("sqlite:///./app.db")
SessionLocal = sessionmaker(bind=engine)


# 依赖：为每个请求提供 Session，请求结束自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/")
def list_users(db: Annotated[Session, Depends(get_db)]):
    return db.execute(__import__("sqlalchemy").text("SELECT 1")).all()
```

## 类作为依赖 {#class-dependency}

依赖既可以是函数，也可以是类（FastAPI 会实例化它）：

```python
from fastapi import Depends, FastAPI

app = FastAPI()


class Pagination:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit


@app.get("/items/")
def read_items(p: Annotated[Pagination, Depends()]):
    return {"skip": p.skip, "limit": p.limit}
```

## 中间件 {#middleware}

中间件在请求进入路由前、响应返回客户端前统一处理，常用于日志与耗时统计：

```python
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    # 调用后续处理链（路由或其他中间件）
    response = await call_next(request)
    cost = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(cost)
    return response
```

## CORS 跨域配置 {#cors}

通过 `CORSMiddleware` 允许浏览器跨域访问：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许的来源列表，生产环境应写具体域名
origins = ["https://example.com", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 异常处理 {#exception-handler}

用 `HTTPException` 主动抛出错误，并可用 `@app.exception_handler` 自定义返回格式：

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id != 42:
        # 抛出 404 及错误信息
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"item_id": item_id}


# 全局捕获未处理的异常，统一响应结构
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc)})
```

## 小结 {#summary}

本章掌握了 `Depends` 依赖注入及其在数据库连接等场景中的复用，并通过中间件、CORS、异常处理器增强了 Web 服务的健壮性。下一章将基于这些能力实现 OAuth2、JWT 与密码哈希的认证体系。
