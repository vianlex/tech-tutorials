---
title: Nginx 配置教程
linkTitle: Nginx 配置教程
description: Nginx 配置文件从核心指令到实战部署的完整教程
weight: 90
---

# Nginx 配置教程

Nginx 是高性能的 HTTP 服务器与反向代理，本教程以稳定版 1.24+ 为准，从配置文件结构讲起，覆盖虚拟主机、反向代理、负载均衡、性能优化与安全，最后给出一个可复用的完整配置案例。建议按顺序阅读，边读边用 `nginx -t` 验证。

## 章节 {.cards}

- [第一章：配置文件结构](/docs/nginx/01-config-structure/) — nginx.conf 全局结构、main/events/http 块、include、校验与重载
- [第二章：server 与 location](/docs/nginx/02-server-location/) — 虚拟主机、listen/server_name、location 匹配规则、root/alias、try_files
- [第三章：反向代理与负载均衡](/docs/nginx/03-proxy-loadbalance/) — proxy_pass 与 proxy_* 指令、upstream、轮询/权重/ip_hash、健康检查
- [第四章：性能与安全](/docs/nginx/04-performance-security/) — SSL/HTTPS、gzip、proxy_cache、limit_req 限速、访问控制
- [第五章：实战完整配置](/docs/nginx/05-complete-config/) — 静态站点 + SPA、前后端分离、WebSocket 代理、多服务 nginx.conf 案例
