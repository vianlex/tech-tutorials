---
title: 第二章 server 与 location
linkTitle: server 与 location
description: 虚拟主机、listen/server_name、location 匹配规则与优先级、root/alias、try_files
weight: 92
---

# server 与 location

`server` 块定义一个**虚拟主机**（站点），`location` 块则把不同的 URI 请求路由到不同处理逻辑。二者是 Nginx 日常配置最频繁的部分。

## 虚拟主机 server {#server-block}

一个 `server` 块对应一个站点，通过监听端口与域名区分。可在 `http` 块内直接写，或拆到 `conf.d/*.conf` 中：

```nginx
http {
    server {
        listen      80;
        server_name example.com www.example.com;

        root        /var/www/example;
        index       index.html;
    }
}
```

`listen` 决定监听的端口（与 IP，可选），`server_name` 决定匹配哪个域名的请求。多个 `server` 可共用同一端口，由域名区分。

## listen 与 server_name {#listen-server-name}

`listen` 可指定 IP:端口，缺省 IP 表示监听所有网卡：

```nginx
listen 80;                 # 监听所有 IPv4 的 80 端口
listen 443 ssl;            # 监听 443 并启用 SSL
listen 127.0.0.1:8080;    # 仅本机访问的 8080 端口
```

`server_name` 支持精确、通配符与前缀正则：

```nginx
server_name example.com;            # 精确匹配
server_name *.example.com;          # 通配符，匹配任意子域
server_name ~^(?<sub>.+)\.example\.com$;  # 正则，并捕获子域到变量 $sub
```

匹配优先级：精确名称 > 通配符前缀 `*.` > 通配符后缀 `.*` > 正则 > 默认 `server`（第一个或标记 `default_server`）。

## location 匹配规则 {#location-match}

`location` 有多种前缀，匹配规则有明确优先级：

```nginx
location = / { ... }              # 1. 精确匹配（=）
location ^~ /static/ { ... }      # 2. 普通前缀，匹配后不再看正则（^~）
location ~ \.php$ { ... }         # 3. 区分大小写正则（~）
location ~* \.(gif|jpg)$ { ... }  # 4. 不区分大小写正则（~*）
location / { ... }                # 5. 普通前缀（最长匹配），兜底
```

优先级从高到低：**`=` 精确** → **`^~` 前缀** → **正则 `~`/`~*`** → **普通前缀（最长匹配）** → **`/` 兜底**。普通前缀先按最长匹配选出候选，再视是否遇到 `^~` 或正则决定最终命中。

## root 与 alias {#root-alias}

`root` 与 `alias` 都用于映射文件路径，但拼接方式不同：

```nginx
# root：请求路径直接拼接在 root 之后
location /images/ {
    root /var/www;        # 访问 /images/a.jpg → /var/www/images/a.jpg
}

# alias：把 location 匹配的部分整体替换
location /images/ {
    alias /var/www/img/;  # 访问 /images/a.jpg → /var/www/img/a.jpg
}
```

注意：`alias` 结尾的 `/` 要与 `location` 的 `/` 对应；`alias` 通常不能用于 `location /`，否则需写成 `alias /var/www/;`。

特别注意：`root` 与 `alias` 的值是**任意的本地绝对路径**，并不局限于 `/var/www` 或某个「站点根目录」——只要是 Nginx worker 进程有读取权限的目录即可。例如映射到用户主目录、数据盘，甚至某个任意位置：

```nginx
# 映射到用户主目录下的静态资源
location /uploads/ {
    alias /home/alice/uploads/;   # 访问 /uploads/pic.jpg → /home/alice/uploads/pic.jpg
}

# 映射到挂载的数据盘
location /data/ {
    root /mnt/data-disk;          # 访问 /data/report.pdf → /mnt/data-disk/data/report.pdf
}
```

`root` 与 `alias` 的区别依然适用：`root` 把完整请求 URI 拼接到路径后，`alias` 用配置值整体替换 `location` 匹配的部分。因此映射到「路径名与 URI 不一致」的任意目录时，`alias` 通常更直观。

但有三个前提与坑要注意：

1. **权限（最常见的问题）**：Nginx 默认以 `nginx`/`www-data` 这类低权限用户运行 worker 进程，它必须对目标目录及其上级路径有**读 + 执行**权限，否则会返回 `403 Forbidden` 或 `404`。任意目录往往权限较严（如 `/home/alice` 默认 `700`），需要相应放行，例如：
   ```bash
   chmod 755 /home/alice /home/alice/uploads
   # 或把目录属主交给 nginx 运行用户
   chown -R nginx:nginx /home/alice/uploads
   ```
   排查时先看错误日志 `error_log` 里的 `Permission denied`。

2. **`alias` 的作用域局限**：`alias` 只在 `location` 内有效，不能放到 `server` 或 `http` 层；`root` 则可以在任意层级声明并被继承。

3. **别把敏感目录暴露出去**：正因为能指任意路径，`alias` 指向 `/etc`、`/home`、`/root`、`.git` 等敏感位置并开放给公网，会造成信息泄露甚至安全风险。生产环境务必只映射确实需要对外提供的目录，并用 `location` 精确限定前缀。

## try_files 指令 {#try-files}

`try_files` 按顺序尝试文件/目录，最后回退到指定 URI，常用于静态站点与前端路由：

```nginx
location / {
    root /var/www/example;
    # 依次尝试：文件、目录、最后交给 /index.html（SPA 兜底）
    try_files $uri $uri/ /index.html;
}
```

```nginx
# 接口不存在时回退到后端
location /api/ {
    try_files $uri @backend;
}
location @backend {
    proxy_pass http://127.0.0.1:3000;
}
```

`try_files` 的最后一项若以 `/` 或 `.php` 等结尾会被当作内部跳转，否则作为回退 URI。

## 完整示例 {#example}

一个静态站点加一个 API 反向代理的 `server` 示例：

```nginx
server {
    listen      80;
    server_name example.com;

    root        /var/www/example;
    index       index.html;

    # 静态资源
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 转发到本地 Node 服务
    location /api/ {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

## 小结 {#summary}

`server` 用 `listen` 和 `server_name` 区分站点，`location` 按「精确 > ^~ > 正则 > 前缀 > 兜底」的优先级路由请求。用 `root`/`alias` 映射文件、`try_files` 处理回退与 SPA。下一章进入反向代理与负载均衡，这是 Nginx 作为网关最常用的能力。
