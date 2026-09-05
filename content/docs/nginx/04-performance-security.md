---
title: 第四章 性能与安全
linkTitle: 性能与安全
description: SSL/HTTPS 配置、gzip、缓存 proxy_cache、限速 limit_req、访问控制
weight: 94
---

# 性能与安全

完成代理转发后，还需加固 HTTPS、开启压缩与缓存、限制恶意流量。本章覆盖生产环境必备的性能与安全配置。

## SSL/HTTPS 配置 {#ssl}

为 `server` 监听 443 并启用 SSL，建议用 TLS 1.2/1.3：

```nginx
server {
    listen      443 ssl;
    server_name example.com;

    ssl_certificate     /etc/nginx/ssl/example.com.fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com.key;

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;   # 优先用客户端支持的现代密码套件

    ssl_session_cache   shared:SSL:10m;   # 会话复用，减少握手开销
    ssl_session_timeout 10m;
}
```

同时把 80 端口跳转 443，强制 HTTPS：

```nginx
server {
    listen      80;
    server_name example.com;
    return      301 https://$host$request_uri;
}
```

证书可用 Let's Encrypt 免费签发，配合 `certbot` 自动续期。

## gzip 压缩 {#gzip}

开启 gzip 可显著减小文本类响应体积：

```nginx
http {
    gzip            on;
    gzip_comp_level 5;                  # 压缩级别 1-9，5 为性价比平衡
    gzip_min_length 1024;              # 小于 1KB 不压缩
    gzip_types      text/plain text/css application/json
                    application/javascript application/xml image/svg+xml;
    gzip_proxied    any;               # 对代理响应也压缩
    gzip_vary       on;                # 增加 Vary: Accept-Encoding 头
}
```

`gzip_types` 默认不含 JS/CSS，需显式列出；图片等已压缩格式无需再压。

## 代理缓存 proxy_cache {#proxy-cache}

对上游响应做缓存，减轻后端压力、提升命中速度：

```nginx
http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=mycache:10m
                     max_size=1g inactive=60m use_temp_path=off;

    server {
        location /api/ {
            proxy_pass      http://backend;
            proxy_cache     mycache;
            proxy_cache_key $scheme$proxy_host$request_uri;
            proxy_cache_valid 200 302 10m;   # 200/302 缓存 10 分钟
            proxy_cache_valid 404      1m;
            add_header      X-Cache-Status $upstream_cache_status;  # 命中状态
        }
    }
}
```

`$upstream_cache_status` 取值为 `HIT` / `MISS` / `BYPASS`，便于排查缓存是否生效。

## 限速 limit_req {#limit-req}

用**漏桶算法**限制单位时间请求数，防刷防 CC：

```nginx
http {
    limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;

    server {
        location /api/ {
            # 突发 20 个，nodelay 表示突发内不延迟
            limit_req zone=perip burst=20 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

`$binary_remote_addr` 按客户端 IP 限流；`rate=10r/s` 即每秒 10 个；`burst` 允许瞬时排队，`nodelay` 让突发请求立即处理而非延时。

## 访问控制 {#access-control}

限制来源 IP 或屏蔽敏感路径：

```nginx
# 仅允许内网访问管理后台
location /admin/ {
    allow   10.0.0.0/8;
    deny    all;
}

# 禁止访问隐藏文件与备份
location ~ /\. {
    deny    all;
    return  404;
}
```

`allow`/`deny` 按出现顺序匹配，先写先生效；`location ~ /\.` 可挡掉 `.git`、`.env` 等敏感文件。

## 小结 {#summary}

用 TLS 1.2/1.3 与 80→443 跳转加固 HTTPS，gzip 压缩文本、proxy_cache 缓存响应、limit_req 限速防刷、allow/deny 做访问控制。下一章把所有知识汇成一个前后端分离、含 WebSocket 的完整 nginx.conf 案例。
