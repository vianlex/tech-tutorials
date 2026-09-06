---
title: 第五章 Docker Compose 多服务编排
linkTitle: Docker Compose
description: Docker Compose V2、compose.yaml 完整语法、services/networks/volumes、depends_on 健康检查、env_file、profile 多环境
weight: 35
---

# Docker Compose 多服务编排

真实项目几乎都是「前端 + 后端 + 数据库 + 缓存」组合。**Docker Compose** 用一个 YAML 文件描述整套服务，用一条命令启动/停止/查看，比手动跑 `docker run` 高效得多。本章系统讲解 Compose V2（默认随 Docker 安装）。

## 为什么用 Compose {#why}

不用 Compose 时，启动一个 WordPress 需要 2-3 个 `docker run` 命令：

```bash
# 没 Compose 的痛苦
docker network create blog
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=xxx --network blog mysql:8
docker run -d --name wp --network blog -p 8080:80 -v wp-data:/var/www/html wordpress

# 而 Compose 只要一个 yaml + 一条命令
docker compose up -d
```

## Compose 与 docker run 的对应关系 {#mapping}

```yaml
# compose.yaml
services:
  mysql:                                       # 相当于 --name mysql
    image: mysql:8                             # 镜像
    environment:                               # -e KEY=VAL
      MYSQL_ROOT_PASSWORD: 123456
    volumes:
      - mysql-data:/var/lib/mysql              # -v mysql-data:/var/lib/mysql
    networks:
      - blog                                   # --network blog
    restart: unless-stopped                    # --restart=unless-stopped

  wordpress:
    image: wordpress
    ports:
      - "8080:80"                              # -p 8080:80
    depends_on:                                # 控制启动顺序
      - mysql
    networks:
      - blog
    restart: unless-stopped

volumes:                                       # 顶级声明卷
  mysql-data:

networks:                                      # 顶级声明网络
  blog:
```

## 安装 {#install}

Docker Desktop 自带 Compose；Linux 服务器安装：

```bash
# Ubuntu/Debian
sudo apt-get install docker-compose-plugin

# 验证
docker compose version
# Docker Compose version v2.27.0
```

> Compose V1（`docker-compose` 连字符）已废弃，V2 是 `docker compose`（空格）。

## compose.yaml 完整结构 {#yaml-structure}

```yaml
# 文件名：compose.yaml（旧版 docker-compose.yml 仍兼容）

# 顶层字段
name: my-project                          # 项目名（影响容器/网络/卷命名前缀）

services:                                  # 服务列表（每个对应一个容器）
  web:
    build: ./web                           # 或 build: { context: ./web, dockerfile: Dockerfile.dev }
    image: my-web:1.0                      # 配合 build 时构建后打的 tag
    container_name: my-web                 # 自定义容器名（不推荐）
    ports:
      - "8080:80"                          # 宿主机:容器
      - "127.0.0.1:9090:9090"              # 仅本机访问
      - target: 80                         # 长格式
        published: 8080
        protocol: tcp
    environment:
      NODE_ENV: production
      DB_HOST: db
    env_file:
      - .env
      - .env.production
    volumes:
      - ./html:/usr/share/nginx/html:ro    # bind mount
      - data:/var/lib/data                 # 命名卷
      - /tmp                              # 匿名卷
    networks:
      - frontend
      - backend
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:                           # 健康检查
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:                                # 仅 swarm 模式生效（见第六章）
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    profiles: ["frontend"]                 # 仅启用 --profile frontend 时启动

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  data:
  db-data:

networks:
  frontend:
  backend:

configs:                                   # 配置文件（Compose V2.4+）
  nginx.conf:
    file: ./nginx.conf

secrets:                                   # 密钥
  db_password:
    file: ./secrets/db_password.txt
```

## 启动与管理 {#manage}

```bash
# 前台启动（看日志，Ctrl+C 停止）
docker compose up

# 后台启动
docker compose up -d

# 仅启动指定服务
docker compose up -d db                    # 只启动 db 及其依赖
docker compose up -d --build               # 启动前重新构建

# 查看状态
docker compose ps
docker compose ps -a                       # 含已停止的

# 查看日志
docker compose logs -f
docker compose logs -f web                 # 单个服务
docker compose logs --tail 100 web         # 最近 100 行
docker compose logs --since 10m            # 最近 10 分钟

# 进入容器
docker compose exec web sh
docker compose exec db psql -U postgres

# 执行一次性命令（不修改 compose.yaml）
docker compose run --rm web node -v

# 停止与删除
docker compose stop                        # 停止（不删容器）
docker compose down                        # 停止 + 删除容器、网络
docker compose down -v                     # 连卷一起删（⚠️ 数据丢失）
docker compose down --rmi all              # 连镜像一起删

# 重启单个服务
docker compose restart web

# 扩缩容（仅 Swarm）
docker compose scale web=3
```

## depends_on：服务启动顺序 {#depends-on}

`depends_on` 控制**启动顺序**，**不等待服务可用**——这是常见误区。

```yaml
services:
  web:
    depends_on:
      - db                                  # 仅启动顺序，不等 db 就绪
      - redis

  # ✅ 等待 db 健康后才启动 web（推荐）
  web:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
```

```mermaid
sequenceDiagram
    autonumber
    participant Compose
    participant DB
    participant Redis
    participant Web
    Compose->>DB: docker compose up
    DB-->>Compose: 容器启动（未就绪）
    Compose->>Redis: docker compose up
    Redis-->>Compose: 容器启动
    Compose->>Web: docker compose up
    Note over Web: 如果依赖 service_healthy，<br/>Web 等 DB 健康才启动
    Web->>DB: 连接 db:5432
    Web->>Redis: 连接 redis:6379
```

> 早期版本 `depends_on` 只能控制启动顺序；V2 起支持 `condition: service_healthy` 等条件。

## 环境变量与 .env 文件 {#env}

```yaml
services:
  api:
    image: my-api
    environment:
      DB_HOST: db                           # 字面量
      DB_PORT: "5432"                       # 注意引号（数字也建议加）
      DEBUG: ${DEBUG:-false}                # 变量 + 默认值
    env_file:
      - .env                                # 加载 .env 文件
      - .env.local                          # 后加载覆盖前加载
```

`.env` 文件：

```bash
# .env
DB_PASSWORD=secret123
LOG_LEVEL=info
```

**变量插值优先级**（从高到低）：

1. shell 环境变量（`DB_PASSWORD=xxx docker compose up`）
2. 命令行 `docker compose run -e`
3. compose.yaml `environment`
4. `env_file`
5. 镜像默认值

## 健康检查（healthcheck）{#healthcheck}

没有 healthcheck 时 Docker 只判断「进程是否启动」，而进程启动 ≠ 服务可用（应用还没初始化好）。

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s                         # 检查间隔
      timeout: 5s                           # 单次超时
      retries: 5                             # 失败 N 次才标记 unhealthy
      start_period: 30s                     # 启动后宽限期（这段时间失败不计入）
```

| 状态 | 含义 |
|------|------|
| `starting` | 启动中（start_period 内） |
| `healthy` | 健康 |
| `unhealthy` | 多次检查失败 |

`docker compose ps` 会显示健康状态：

```
NAME      SERVICE   STATUS              PORTS
api       api       Up 5 minutes (healthy)
db        db        Up 5 minutes (healthy)
web       web       Up 1 minute         0.0.0.0:8080->80/tcp
```

## profile：多环境多套配置 {#profile}

用 profile 按需启用某些服务：

```yaml
services:
  web:
    image: my-web

  db:
    image: postgres
    profiles: ["default"]                   # 默认启动（不指定 profile 也启用）

  debug-tools:
    image: nicolaka/netshoot
    profiles: ["debug"]                     # 仅 --profile debug 时启动

  loadtest:
    image: loader.io/loader
    profiles: ["loadtest"]                  # 压测时启用
```

```bash
# 默认启动：web + db
docker compose up -d

# 启动调试模式（额外启用 debug-tools）
docker compose --profile debug up -d

# 压测时启用 loadtest
docker compose --profile loadtest up -d
```

## .env 文件与变量插值 {#env-interpolation}

Compose 还会读取**项目目录下的 `.env` 文件**用于变量插值（与 `env_file` 不同）：

```.env
# .env（项目根目录）
POSTGRES_VERSION=16
WEB_PORT=8080
```

```yaml
services:
  db:
    image: postgres:${POSTGRES_VERSION}
  web:
    ports:
      - "${WEB_PORT}:80"
```

> 项目根 `.env` 用于 compose.yaml 自身的变量替换（build args、镜像 tag、端口等），`env_file:` 是把变量传给容器进程。

## 实战 1：WordPress + MySQL {#example-wp}

```yaml
name: blog

services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: wordpress
    volumes:
      - db-data:/var/lib/mysql
    networks:
      - blog
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  wordpress:
    image: wordpress:latest
    depends_on:
      db:
        condition: service_healthy
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: root
      WORDPRESS_DB_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    ports:
      - "8080:80"
    networks:
      - blog
    restart: unless-stopped

volumes:
  db-data:

networks:
  blog:
```

启动：

```bash
echo "MYSQL_ROOT_PASSWORD=secret123" > .env
docker compose up -d
# 访问 http://localhost:8080
```

## 实战 2：NestJS + Postgres + Redis {#example-stack}

```yaml
name: nest-app

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: nestdb
    volumes:
      - pg-data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d nestdb"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@postgres:5432/nestdb
      REDIS_HOST: redis
      REDIS_PORT: 6379
      NODE_ENV: production
    ports:
      - "3000:3000"
    networks:
      - backend
    restart: unless-stopped

volumes:
  pg-data:

networks:
  backend:
```

```bash
echo "DB_PASSWORD=xxx" > .env
docker compose up -d --build
```

## 常见命令对照表 {#commands}

| 任务 | docker compose | 等价 docker run |
|------|---------------|------------------|
| 启动所有 | `docker compose up -d` | 多个 `docker run` |
| 启动单个 | `docker compose up -d api` | `docker run ...` |
| 停止 | `docker compose stop` | `docker stop $(docker ps -q)` |
| 删除 | `docker compose down` | `docker rm -f` + `docker network rm` |
| 日志 | `docker compose logs -f` | `docker logs -f` |
| 进入容器 | `docker compose exec api sh` | `docker exec -it ... sh` |
| 重新构建 | `docker compose build` | `docker build -t ...` |

## 最佳实践 {#best-practices}

1. **compose.yaml 加入版本控制**，不要带 `.env`（`.env` 加进 `.gitignore`）。
2. **所有服务加入自定义网络**，不要用默认 bridge。
3. **关键服务配 healthcheck**，配合 `depends_on: condition: service_healthy`。
4. **慎用 `container_name`**：固定容器名限制了横向扩展（同一 compose 不能 scale）。
5. **数据卷必须显式声明**（`volumes: db-data:`），否则下次启动数据丢失。
6. **镜像 tag 显式指定**（如 `mysql:8.4`，不要 `mysql:latest`），保证构建可复现。
7. **多环境用 profile 或 override 文件**（`compose.override.yaml`）。

```yaml
# compose.override.yaml（开发期自动加载）
services:
  api:
    build:
      context: .
    volumes:
      - ./src:/app/src:ro          # 实时同步代码
    environment:
      NODE_ENV: development
      DEBUG: "true"
    command: npm run dev            # 覆盖生产 command
```

## 小结 {#summary}

Docker Compose 是单机多容器编排的事实标准：用一份 YAML 描述所有服务、网络、卷，一条命令启动/停止/查看。关键点：用自定义网络 + 容器名解析做服务发现；用 `healthcheck` + `depends_on condition: service_healthy` 控制依赖；用 profile 与 `.env` 管理多环境。Compose 与 Docker Swarm 关系密切——第六章会讲 Swarm 与 Compose 的协作（`deploy:` 字段、Stack 部署）。
