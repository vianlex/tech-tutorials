---
title: 第一章 快速上手
linkTitle: 快速上手
description: FastAPI 安装、第一个应用与自动文档
weight: 101
---

# 快速上手

本章带你完成 FastAPI 的环境搭建，创建第一个应用，并通过 uvicorn 启动服务，再认识自动生成的 Swagger / ReDoc 文档，最后了解路径参数与查询参数的用法。

## 安装 {#install}

推荐使用虚拟环境隔离依赖，FastAPI 需要 `fastapi` 与 ASGI 服务器 `uvicorn`：

```bash
# 创建并激活虚拟环境（Python 3.10+）
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装核心依赖
pip install "fastapi[standard]"
```

验证安装版本：

```bash
python -c "import fastapi, uvicorn; print(fastapi.__version__, uvicorn.__version__)"
# 例如：0.115.0 0.30.6
```

## 第一个应用 {#hello-world}

新建 `main.py`，用最少的代码启动一个接口：

```python
from fastapi import FastAPI

# 创建应用实例
app = FastAPI()


# 定义根路径的 GET 接口
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
```

## 使用 uvicorn 运行 {#run}

在项目根目录执行以下命令启动开发服务器：

```bash
# --reload 开启热重载，仅用于开发环境
uvicorn main:app --reload
```

启动后访问 <http://127.0.0.1:8000> ，即可看到返回的 JSON：

```json
{
  "message": "Hello, FastAPI!"
}
```

## 自动文档 {#docs}

FastAPI 基于 OpenAPI 规范自动生成两套交互式文档，无需任何额外配置：

- **Swagger UI**：访问 <http://127.0.0.1:8000/docs> ，可在页面上直接调试每个接口。
- **ReDoc**：访问 <http://127.0.0.1:8000/redoc> ，提供更适合阅读的文档视图。

打开 `/docs` 后，点击任意接口下的「Try it out」即可在线发送请求。

## 路径参数 {#path-params}

路径参数通过函数形参声明，FastAPI 会按类型自动转换并校验：

```python
from fastapi import FastAPI

app = FastAPI()


# {item_id} 是路径参数，声明为 int 会自动校验类型
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

若访问 `/items/abc`，FastAPI 会返回 422 错误，提示类型校验失败。

## 查询参数 {#query-params}

未在路径中声明的函数参数即为查询参数，写在 URL 的 `?` 之后：

```python
from fastapi import FastAPI

app = FastAPI()


# q 为可选查询参数，short 为带默认值的布尔参数
@app.get("/search/")
def search(q: str | None = None, short: bool = False):
    result = {"query": q}
    if short:
        result["short"] = True
    return result
```

请求示例：

```bash
curl "http://127.0.0.1:8000/search/?q=fastapi&short=true"
```

## 小结 {#summary}

本章完成了 FastAPI 的环境搭建，并用 `uvicorn` 运行了第一个应用，体验了内置的 Swagger / ReDoc 自动文档。你也掌握了路径参数与查询参数的声明方式。下一章将学习如何用 Pydantic v2 定义请求体，并进行参数与响应校验。
