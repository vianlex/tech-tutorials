---
title: 第一章 配置文件结构
linkTitle: 配置文件结构
description: nginx.conf 全局结构、main/events/http 块、include、校验与重载
weight: 91
---

# 配置文件结构

Nginx 的配置以**指令（directive）**和**块（block / context）**组织。理解层级关系是写好配置的前提：所有指令必须位于某个块内，且不能随意嵌套。

## 全局结构 {#overview}

一个典型的 `nginx.conf` 由外到内分为 `main`、`events`、`http` 三层。`main` 层是全局指令，没有包裹符号；`events` 控制连接处理；`http` 承载几乎所有 Web 相关配置。

```nginx
# 全局层 main（无大括号包裹）
user                 nginx;
worker_processes     auto;          # 工作进程数，auto 表示等于 CPU 核数
error_log            /var/log/nginx/error.log warn;
pid                  /run/nginx.pid;

events {
    worker_connections  1024;       # 单个 worker 最大并发连接数
}

http {
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    sendfile            on;
    keepalive_timeout   65;
}
```

## main 层常用指令 {#main-block}

`main` 层（也叫全局块）的指令对整个 Nginx 实例生效，常见的有：

```nginx
worker_processes    auto;           # 工作进程数
worker_rlimit_nofile 65535;         # 每个 worker 可打开的文件描述符上限
error_log           /var/log/nginx/error.log warn;  # 错误日志及级别
pid                 /run/nginx.pid; # 记录主进程 PID 的文件
user                nginx;           # worker 进程运行的用户与组
```

`worker_processes` 一般设为 `auto`，让 Nginx 自动按 CPU 核数拉起工作进程；高并发场景可结合 `worker_rlimit_nofile` 提高文件句柄上限。

## events 块 {#events-block}

`events` 块负责网络连接相关的设置，最常用的是 `worker_connections`：

```nginx
events {
    worker_connections  1024;       # 单 worker 并发连接上限
    use                 epoll;      # 事件模型（Linux 默认即可，可不写）
    multi_accept        on;         # 一次尽可能多接受新连接
}
```

理论最大连接数约为 `worker_processes × worker_connections`，实际还受系统 `ulimit` 与内存限制。

## http 块 {#http-block}

`http` 块是配置的核心，可包含多个 `server` 块，并集中设置 MIME、日志、压缩等通用项：

```nginx
http {
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    log_format  main    '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent"';
    access_log          /var/log/nginx/access.log main;

    sendfile            on;         # 零拷贝发送文件，提升静态资源性能
    tcp_nopush          on;         # 与 sendfile 配合，攒够包再发
    keepalive_timeout   65;         # 长连接超时时间
    server_tokens       off;        # 隐藏响应头中的 Nginx 版本号
}
```

`http` 中设置的指令会被其内部的 `server`、`location` 继承，子级可覆盖。

## include 拆分配置 {#include}

实际部署中，不会把所有配置塞进一个文件，而是用 `include` 拆分。Nginx 默认即如此组织：

```nginx
http {
    include       /etc/nginx/conf.d/*.conf;   # 引入 conf.d 下的虚拟主机
    include       /etc/nginx/sites-enabled/*; # 启用站点（Debian 系常见）
}
```

这样每个站点（server 块）单独成文件，便于维护。注意 `include` 的路径支持通配符 `*`。

## 校验与重载 {#test-and-reload}

修改配置后**务必先校验**再重载，避免语法错误导致 Nginx 无法启动：

```bash
# 检查配置文件语法是否正确
nginx -t

# 输出示例：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# 平滑重载（不中断现有连接）
nginx -s reload

# 其他常用信号
nginx -s stop    # 立即停止
nginx -s quit    # 优雅退出（处理完当前请求）
nginx -s reopen  # 重新打开日志文件
```

`nginx -t` 只检查语法，不会真正应用；`reload` 才让新配置生效，且对线上连接零中断。

## 小结 {#summary}

Nginx 配置由 `main` / `events` / `http` 三层块构成，`http` 内部再嵌套 `server` 与 `location`。用 `include` 拆分多站点配置，修改后用 `nginx -t` 校验、再 `reload` 平滑生效。下一章讲解 `server` 与 `location`，这是承载具体站点规则的关键。
