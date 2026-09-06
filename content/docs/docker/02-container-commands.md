---
title: 第二章 容器与镜像常用命令
linkTitle: 容器与镜像命令
description: Docker 日常最常用命令：容器生命周期、查看与进入、文件传输、日志与资源限制、镜像搜索与删除、清理与速查表
weight: 32
---

# 容器与镜像常用命令

本章覆盖日常使用最高频的 Docker 命令。命令很多，但用熟了就 20 来个。建议先通读一遍建立心智模型，再回头当速查表用。

## 容器生命周期 {#lifecycle}

### 创建并启动容器：`docker run`

```bash
# 最简形式：拉镜像 + 启动 + 打印 hello
docker run hello-world

# 启动一个 nginx 并映射端口
docker run -d -p 8080:80 --name my-nginx nginx:1.27
# -d  后台运行
# -p  宿主机端口:容器端口
# --name  自定义容器名

# 启动后自动删除（适合一次性任务）
docker run --rm -it alpine sh

# 设置环境变量
docker run -e MYSQL_ROOT_PASSWORD=123456 -d mysql:8

# 限制资源
docker run -d --memory=512m --cpus=1.5 nginx

# 挂载目录
docker run -d -v /host/data:/container/data nginx
```

`docker run` 等价于 `docker create` + `docker start` 两步：

```bash
# 先 create（仅创建，不启动）
docker create --name my-nginx nginx:1.27

# 再 start
docker start my-nginx
```

### 查看容器 {#ps}

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（含已停止）
docker ps -a

# 只看 ID
docker ps -aq

# 格式化输出（写脚本好用）
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 停止 / 启动 / 重启 {#start-stop}

```bash
docker stop my-nginx           # 优雅停止（发送 SIGTERM，10s 后 SIGKILL）
docker start my-nginx          # 启动已存在的容器
docker restart my-nginx        # 重启
docker kill my-nginx           # 强制结束（SIGKILL）

# 优雅停止超时时间
docker stop -t 30 my-nginx     # 30 秒后强制 kill
```

### 删除容器 {#rm}

```bash
docker rm my-nginx                  # 删除已停止的容器
docker rm -f my-nginx               # 强制删除运行中的容器（先 kill 再 rm）
docker rm -f $(docker ps -aq)       # 删除所有容器（⚠️ 慎用）
docker container prune              # 删除所有已停止的容器（推荐）
```

## 与运行中容器交互 {#interact}

### 进入容器终端 {#exec}

```bash
# 启动一个新 shell 进入容器
docker exec -it my-nginx sh
docker exec -it my-nginx bash

# 在容器内执行单条命令并退出
docker exec my-nginx cat /etc/nginx/nginx.conf
docker exec my-nginx ls /usr/share/nginx/html
```

> `-it` 是 `-i`（保持 STDIN 打开）+ `-t`（分配伪终端）的合写。少了 `-t` 很多命令的输出会无换行或乱码。

### 查看日志 {#logs}

```bash
docker logs my-nginx
docker logs -f my-nginx              # 跟踪日志（类似 tail -f）
docker logs --tail 100 my-nginx      # 最后 100 行
docker logs --since 10m my-nginx     # 最近 10 分钟
docker logs --until 2026-09-01T12:00 my-nginx
docker logs -t my-nginx              # 显示时间戳
```

### 文件传输 {#cp}

```bash
# 从容器拷出
docker cp my-nginx:/etc/nginx/nginx.conf ./nginx.conf

# 拷入容器
docker cp ./index.html my-nginx:/usr/share/nginx/html/

# 整个目录也行
docker cp ./dist my-nginx:/usr/share/nginx/html/
```

### 查看进程 / 资源占用 {#stats}

```bash
# 实时资源监控（CPU/内存/网络/磁盘）
docker stats
docker stats my-nginx                # 只看指定容器

# 查看容器内进程
docker top my-nginx

# 查看容器详细信息（含网络、挂载、环境变量等）
docker inspect my-nginx

# 查看容器内变更（启动后改了哪些文件）
docker diff my-nginx
```

## 镜像管理 {#image}

```bash
# 搜索镜像（默认从 Docker Hub）
docker search nginx
docker search --filter is-official=true nginx    # 只看官方镜像

# 拉取镜像
docker pull nginx                              # 默认 tag = latest
docker pull nginx:1.27                         # 指定 tag
docker pull nginx:1.27-alpine                  # alpine 变体（更小）

# 查看本地镜像
docker images
docker images -a                               # 含中间层

# 删除镜像
docker rmi nginx:1.27
docker image prune                              # 清理 dangling 镜像
docker image prune -a                           # 清理所有未被使用的镜像

# 查看镜像历史（各层构建命令）
docker history nginx:1.27

# 给镜像打标签（不会复制，只是别名）
docker tag nginx:1.27 my-registry.com/nginx:1.27

# 查看镜像详细信息
docker inspect nginx:1.27
```

## 端口与网络（基础）{#port}

```bash
# 查看端口映射
docker port my-nginx
# 80/tcp -> 0.0.0.0:8080

# 直接通过容器 IP 访问（不需要端口映射）
docker inspect my-nginx | grep IPAddress

# 查看容器网络
docker network ls
docker network inspect bridge
```

详细的网络原理与 6 种网络模式见第四章。

## 数据卷（基础）{#volume}

```bash
# 创建一个命名卷
docker volume create my-data

# 启动容器并挂载
docker run -d -v my-data:/data nginx

# 查看卷
docker volume ls
docker volume inspect my-data

# 清理无用卷
docker volume prune
```

`bind mount` 与 `tmpfs` 等更详细的卷用法见第四章。

## 资源限制与系统信息 {#resources}

### 内存 / CPU

```bash
# 限制内存 + 禁用 swap
docker run -d --memory=512m --memory-swap=512m nginx

# 限制 CPU（可用核数）
docker run -d --cpus=1.5 nginx                # 最多 1.5 核
docker run -d --cpuset-cpus=0,1 nginx         # 限定使用 CPU 0 和 1

# 限制磁盘 IO（需 blkio 支持）
docker run -d --device-read-bps /dev/sda:1mb nginx
```

### 重启策略

```bash
docker run -d --restart=always nginx           # 总是重启
docker run -d --restart=on-failure:5 nginx    # 失败才重启，最多 5 次
docker run -d --restart=unless-stopped nginx   # 默认推荐（手动 stop 不重启）
```

### 查看磁盘占用 {#disk-usage}

```bash
docker system df
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          28        15        8.432GB   3.141GB (37%)
# Containers      38        20        1.2GB     600MB (50%)
# Local Volumes   12        8         500MB     200MB (40%)
# Build Cache     0         0         0B        0B

# 详细占用
docker system df -v
```

## 清理 {#cleanup}

```bash
# 一次性清理：停掉所有容器、删除所有容器、删除所有未用镜像、清理网络
docker system prune
# ⚠️ WARNING! This will remove:
#   - all stopped containers
#   - all networks not used by at least one container
#   - all dangling images
#   - all build cache

# 激进清理：连所有未用镜像（非 dangling）也一起删
docker system prune -a

# 分别清理
docker container prune                       # 已停止的容器
docker image prune                            # dangling 镜像
docker image prune -a --filter "until=24h"    # 24 小时前创建且无引用的镜像
docker volume prune                           # 无用卷
docker network prune                          # 无用网络
docker builder prune                          # 构建缓存
```

## 常用命令速查表 {#cheatsheet}

| 类别 | 命令 | 用途 |
|------|------|------|
| 容器 | `docker run -d -p 80:80 --name x nginx` | 创建并后台启动 |
| 容器 | `docker ps -a` | 列出所有容器 |
| 容器 | `docker stop/start/restart x` | 启停 |
| 容器 | `docker rm -f x` | 删除 |
| 容器 | `docker exec -it x sh` | 进入终端 |
| 容器 | `docker logs -f x` | 跟踪日志 |
| 容器 | `docker cp src dst` | 文件传输 |
| 容器 | `docker stats` | 资源监控 |
| 镜像 | `docker pull/push x` | 拉取/推送 |
| 镜像 | `docker images` | 列出本地镜像 |
| 镜像 | `docker rmi x` | 删除镜像 |
| 镜像 | `docker tag src dst` | 打标签 |
| 镜像 | `docker history x` | 查看层历史 |
| 系统 | `docker info` | 查看引擎信息 |
| 系统 | `docker system df` | 查看占用 |
| 系统 | `docker system prune` | 清理 |

## 实用 alias {#aliases}

把高频命令写成别名，写入 `~/.zshrc` 或 `~/.bashrc`：

```bash
alias dps='docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dpsa='docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"'
alias dim='docker images'
alias dex='docker exec -it'
alias dlogs='docker logs -f'
alias dstop='docker stop $(docker ps -q)'
alias drm='docker rm -f $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'
```

## 小结 {#summary}

本章覆盖了 Docker 最常用的 30+ 个命令——容器生命周期（`run`/`ps`/`stop`/`rm`）、交互（`exec`/`logs`/`cp`）、资源（`stats`/`inspect`/`diff`）、镜像管理（`pull`/`push`/`images`/`rmi`/`tag`）、清理（`system prune`）。下一章开始构建自定义镜像，并学习「镜像在不同环境间迁移」的导入导出方案。
