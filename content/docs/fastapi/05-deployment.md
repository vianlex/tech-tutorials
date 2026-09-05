---
title: 第五章 实战与部署
linkTitle: 实战与部署
description: SQLAlchemy 集成 CRUD、后台任务、测试 TestClient 与 Docker 部署
weight: 105
---

# 实战与部署

本章整合前几章知识，用 SQLAlchemy 实现完整的数据库 CRUD，演示后台任务与定时操作的写法，通过 TestClient 编写自动化测试，最后用 Docker 打包部署。

## SQLAlchemy 集成 {#sqlalchemy}

定义 ORM 模型与数据库初始化：

```python
from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 声明式基类
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    # 外键关联作者
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship("User")


# 创建同步引擎并建表
engine = create_engine("sqlite:///./app.db")
Base.metadata.create_all(engine)
```

## 实现 CRUD 接口 {#crud}

结合 Pydantic 模型与数据库依赖，提供增删改查接口：

```python
from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db  # 见第三章数据库依赖

app = FastAPI()


class PostCreate(BaseModel):
    title: str


# 用 ConfigDict 允许从 ORM 对象读取属性
class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


@app.post("/posts/", response_model=PostOut)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    post = Post(title=data.title, author_id=1)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@app.get("/posts/", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.scalars(select(Post)).all()


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="文章不存在")
    db.delete(post)
    db.commit()
```

## 后台任务 {#background-tasks}

用 `BackgroundTasks` 在响应返回后执行耗时操作（如发邮件）：

```python
import time

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def write_log(message: str):
    # 模拟耗时写入
    time.sleep(1)
    with open("app.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")


@app.post("/logs/")
def create_log(
    message: str,
    background_tasks: BackgroundTasks,
):
    # 请求立即返回，任务在后台执行
    background_tasks.add_task(write_log, message)
    return {"queued": True}
```

## 编写测试 {#testing}

FastAPI 基于 Starlette 的 `TestClient` 提供同步测试能力：

```python
from fastapi.testclient import TestClient

from main import app  # 导入你的 FastAPI 应用


def test_read_root():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Hello, FastAPI!"


def test_create_post():
    client = TestClient(app)
    resp = client.post("/posts/", json={"title": "测试文章"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "测试文章"
```

运行测试：

```bash
pip install pytest httpx
pytest -q
```

## Docker 部署 {#docker}

使用官方 Python 镜像构建精简的运行环境：

```dockerfile
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖清单以利用构建缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 暴露端口并启动
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt` 内容示例：

```text
fastapi[standard]
uvicorn[standard]
sqlalchemy
pydantic
passlib[bcrypt]
python-jose[cryptography]
```

构建并运行容器：

```bash
docker build -t fastapi-app .
docker run -d -p 8000:8000 fastapi-app
```

生产环境建议配合 Gunicorn 多进程：

```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4
```

## 小结 {#summary}

本章用 SQLAlchemy 完成了完整 CRUD，演示了后台任务与基于 TestClient 的自动化测试，并通过 Dockerfile 将应用打包部署到容器。至此你已掌握用 FastAPI 从零构建并上线一个生产级 API 服务的完整流程。
