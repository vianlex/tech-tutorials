---
title: 第五章 实战完整配置
linkTitle: 实战完整配置
description: 静态站点 + SPA history 路由、前后端分离、WebSocket 代理、多服务完整 nginx.conf 案例
weight: 95
---

# 实战完整配置

本章把前四章内容整合为一个**前后端分离 + SPA + WebSocket** 的多服务 `nginx.conf` 案例，可直接裁剪使用（Nginx 1.24+）。

## 静态站点与 SPA {#static-spa}

前端构建产物放在 `/var/www/spa`，history 路由需回退到 `index.html`：

```nginx
server {
    listen      80;
    server_name app.example.com;
    root        /var/www/spa;
    index       index.html;

    # 带 hash 的资源带版本号，可长缓存
    location /assets/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA history 路由：找不到文件就回退到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 前后端分离 {#bff}

前端域名与后端 API 分离，API 转发到后端，并隐藏后端地址：

```nginx
server {
    listen      443 ssl;
    server_name app.example.com;

    ssl_certificate     /etc/nginx/ssl/app.example.com.fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/app.example.com.key;
    ssl_protocols       TLSv1.2 TLSv1.3;

    root        /var/www/spa;
    index       index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API：转发到 upstream 组
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## WebSocket 代理 {#websocket}

WebSocket 需显式升级协议，关键是 `Upgrade` 与 `Connection` 头：

```nginx
upstream wsbackend {
    server 127.0.0.1:4000;
}

server {
    location /ws/ {
        proxy_pass http://wsbackend;
        proxy_http_version 1.1;                  # WebSocket 需要 HTTP/1.1
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";   # 关键：升级为 WebSocket
        proxy_set_header Host       $host;
        proxy_read_timeout 3600s;                # 长连接，避免被过早断开
    }
}
```

`$http_upgrade` 来自客户端请求头，Nginx 原样透传；`Connection "upgrade"` 触发协议切换。

## 多服务完整案例 {#full-conf}

下面是一个整合了 HTTP→HTTPS 跳转、静态站点、API 负载均衡、WebSocket 的 `nginx.conf`：

```nginx
user                 nginx;
worker_processes     auto;
error_log            /var/log/nginx/error.log warn;
pid                  /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    sendfile            on;
    keepalive_timeout   65;
    server_tokens       off;

    gzip                on;
    gzip_comp_level     5;
    gzip_types          text/plain text/css application/json
                        application/javascript application/xml image/svg+xml;

    # 上游：API 负载均衡
    upstream backend {
        server 10.0.0.1:3000 weight=2;
        server 10.0.0.2:3000 weight=1;
        server 10.0.0.3:3000 backup;
    }

    # 上游：WebSocket
    upstream wsbackend {
        server 127.0.0.1:4000;
    }

    # 80 跳转 443
    server {
        listen      80;
        server_name app.example.com;
        return      301 https://$host$request_uri;
    }

    server {
        listen      443 ssl;
        server_name app.example.com;

        ssl_certificate     /etc/nginx/ssl/app.example.com.fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/app.example.com.key;
        ssl_protocols       TLSv1.2 TLSv1.3;

        root        /var/www/spa;
        index       index.html;

        location /assets/ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host              $host;
            proxy_set_header X-Real-IP         $remote_addr;
            proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            limit_req zone=perip burst=20 nodelay;
        }

        location /ws/ {
            proxy_pass http://wsbackend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade    $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host       $host;
            proxy_read_timeout 3600s;
        }
    }
}
```

> 注意：`limit_req` 引用的 `perip` 区域需在 `http` 块用 `limit_req_zone` 定义，可按需补充。

## 部署与验证 {#deploy}

```bash
# 1. 校验语法
nginx -t

# 2. 平滑重载
nginx -s reload

# 3. 验证 HTTPS 与路由
curl -I http://app.example.com        # 应 301 跳转到 https
curl -I https://app.example.com/api/  # 应转发到后端
```

## 小结 {#summary}

本案例串联了静态资源与 SPA 回退、API 负载均衡、WebSocket 升级与 HTTPS 跳转，可直接作为生产模板裁剪。建议每次改动后执行 `nginx -t` 校验再 `reload`。至此 Nginx 配置教程结束，可结合官方文档深入各指令细节。
