---
title: 第四章 认证与安全
linkTitle: 认证与安全
description: OAuth2 Password Bearer、JWT、密码哈希与权限控制
weight: 104
---

# 认证与安全

本章实现一套完整的用户认证：使用 OAuth2 密码模式获取令牌，用 JWT 签发与校验令牌，借助 `passlib` 对密码加盐哈希，最后通过依赖实现接口级权限控制。

## 密码哈希 {#password-hash}

绝不存储明文密码，使用 `passlib` 的 `bcrypt` 算法进行加盐哈希：

```python
from passlib.context import CryptContext

# 指定 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # 生成加盐哈希
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # 校验明文与哈希是否匹配
    return pwd_context.verify(plain, hashed)


# 示例
hashed = hash_password("secret123")
print(verify_password("secret123", hashed))  # True
```

## 用户模型与数据 {#user-model}

定义用户表结构与内存中的演示数据：

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    username: str
    disabled: bool = False


# 演示用数据库（实际项目应替换为真实存储）
fake_users = {
    "alice": {
        "username": "alice",
        "hashed_password": "$2b$12$...",  # hash_password("alice123") 的结果
    }
}


def get_user(username: str) -> User | None:
    if username in fake_users:
        return User(username=username)
    return None
```

## OAuth2 密码模式 {#oauth2-password}

使用 `OAuth2PasswordBearer` 声明令牌获取方式，登录接口返回 JWT：

```python
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# tokenUrl 指向登录接口路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "change-me-in-production"   # 生产环境务必使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(subject: str) -> str:
    # 签发 30 分钟有效的 JWT
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    import jwt
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

## 登录与签发令牌 {#login}

```python
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()


# 使用表单格式接收用户名密码（Swagger 自带表单）
@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_users.get(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    # 返回符合 OAuth2 规范的令牌
    return {"access_token": create_access_token(form.username), "token_type": "bearer"}
```

## 校验令牌获取当前用户 {#get-current-user}

用依赖解析并校验 JWT，得到当前登录用户：

```python
import jwt
from fastapi import Depends, HTTPException

app = FastAPI()


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_error = HTTPException(
        status_code=401, detail="无效凭证", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_error
    except jwt.PyJWTError:
        raise credentials_error
    user = get_user(username)
    if user is None:
        raise credentials_error
    return user
```

## 权限控制 {#permission}

在需要保护的接口上注入 `get_current_user`，并基于用户状态二次校验：

```python
from fastapi import Depends

app = FastAPI()


@app.get("/me")
def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.get("/admin")
def read_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    return {"admin": True}
```

访问受保护接口时需在请求头携带令牌：

```bash
curl "http://127.0.0.1:8000/me" \
  -H "Authorization: Bearer <你的access_token>"
```

## 小结 {#summary}

本章用 OAuth2 密码模式与 JWT 实现了无状态认证，并结合 `passlib` 完成了密码的安全哈希存储。通过依赖注入把"获取当前用户"与"权限校验"复用到了各个受保护接口。下一章将综合所学，完成数据库 CRUD、测试与 Docker 部署的实战。
