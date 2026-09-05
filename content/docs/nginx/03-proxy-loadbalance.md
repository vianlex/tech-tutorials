---
title: 第三章 反向代理与负载均衡
linkTitle: 反向代理与负载均衡
description: proxy_pass 及常用 proxy_* 指令、upstream、轮询/权重/ip_hash、健康检查
weight: 93
---

# 反向代理与负载均衡

Nginx 作为反向代理，把客户端请求转发给后端应用（Node、Java、Python 等），并可作为多实例的负载均衡器。

## proxy_pass 基础 {#proxy-pass}

`proxy_pass` 把请求转发到上游服务，是反向代理的核心指令：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:3000;
}
```

`proxy_pass` 带不带 URI 路径，拼接行为不同：

```nginx
# 不带路径：完整转发原 URI
# 请求 /api/user → 转发到 http://127.0.0.1:3000/api/user
location /api/ {
    proxy_pass http://127.0.0.1:3000;
}

# 带路径 /：去掉匹配前缀再拼接
# 请求 /api/user → 转发到 http://127.0.0.1:3000/user
location /api/ {
    proxy_pass http://127.0.0.1:3000/;
}
```

## 常用 proxy_* 指令 {#proxy-directives}

转发时通常需要补全请求头、设置超时，否则后端拿不到真实客户端信息：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:3000;

    # 透传主机名与真实客户端 IP
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 超时控制
    proxy_connect_timeout 5s;   # 与后端建立连接超时
    proxy_send_timeout    30s;  # 发送请求超时
    proxy_read_timeout    30s;  # 读取响应超时
}
```

`X-Forwarded-For` 让后端能获取原始访问链；`X-Forwarded-Proto` 用于识别用户实际用的 http/https。

## upstream 负载均衡 {#upstream}

`upstream` 定义一组后端服务器，配合 `proxy_pass` 实现负载均衡：

```nginx
upstream backend {
    server 10.0.0.1:3000;
    server 10.0.0.2:3000;
    server 10.0.0.3:3000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

`upstream` 默认放在 `http` 块内，`proxy_pass` 中用 `http://backend` 引用其名字。

## 调度算法 {#scheduling}

默认是**轮询**（round-robin）。可通过参数切换策略：

```nginx
upstream backend {
    # 权重：性能好的机器多分流量
    server 10.0.0.1:3000 weight=3;
    server 10.0.0.2:3000 weight=1;

    # 基于客户端 IP 哈希，保证同一用户落到同一后端（会话保持）
    ip_hash;

    # 最少连接数（Nginx 1.3.1+）
    # least_conn;
}
```

- **weight**：加权轮询，数值越大分配越多。
- **ip_hash**：按 `$remote_addr` 哈希分配，适合需要会话保持但没用共享会话的场景；后端变动会导致重新分布。
- **least_conn**：优先转发给连接数最少的后端。

## 健康检查 {#health-check}

被动健康检查通过 `max_fails` 与 `fail_timeout` 实现（商业版支持主动 `health_check`）：

```nginx
upstream backend {
    server 10.0.0.1:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.2:3000 max_fails=3 fail_timeout=30s;
    # max_fails 次失败（30s 内）后，该节点被摘除 30s
}
```

还可临时摘除或限流：

```nginx
server 10.0.0.3:3000 backup;     # 备份节点，仅当其他都不可用时启用
server 10.0.0.4:3000 down;       # 标记为永久下线
```

## 小结 {#summary}

用 `proxy_pass` 转发请求，配合 `proxy_set_header` 透传真实客户端信息；`upstream` 把多后端组织成组，支持轮询、加权、ip_hash、least_conn 等调度与被动健康检查。下一章关注性能与安全：SSL、压缩、缓存与限速。
