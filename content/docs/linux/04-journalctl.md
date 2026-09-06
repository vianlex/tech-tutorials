---
title: 第四章：journalctl 日志分析
linkTitle: journalctl 日志分析
description: 查看 systemd 服务日志、时间过滤、实时跟踪、按优先级筛选
weight: 184
---

# journalctl 日志分析

`journalctl` 是 systemd 系统的**统一日志查看工具**，可查询所有 systemd 管理的服务日志、内核日志。相比传统 `/var/log/` 下的分散日志文件，它支持强大的过滤和实时跟踪能力，是现代 Linux（CentOS 7+、Ubuntu 16+、Debian 8+）排查问题的第一入口。

## 一、基本用法

```bash
journalctl                    # 查看全部日志（按时间正序，最旧在前）
journalctl -r                 # 倒序（最新在前）
journalctl -b                 # 只看本次启动以来的日志
journalctl -b -1              # 看上一次启动的日志（排查重启前问题）
journalctl -k                 # 只看内核日志（dmesg）
```

翻页与搜索和 `less` 一致：方向键/`j``k` 翻页，`/` 搜索，`g` 到顶，`G` 到底，`q` 退出。

## 二、按服务/单元过滤

```bash
journalctl -u nginx           # 看 nginx 服务的日志
journalctl -u nginx -u php    # 看多个服务
journalctl -u docker --since "1 hour ago"   # 最近 1 小时 docker 日志
```

`-u` 是 `--unit` 的简写，单元名即 `systemctl status nginx` 里显示的单元名。

## 三、按时间过滤

```bash
journalctl --since "2026-09-06 08:00:00"            # 从某时间起
journalctl --until "2026-09-06 09:00:00"            # 到某时间止
journalctl --since "2 hours ago" --until "30 min ago"  # 时间区间
journalctl --since today                              # 今天
journalctl --since yesterday                          # 昨天
```

## 四、实时跟踪日志

```bash
journalctl -f               # 实时跟踪（类似 tail -f）
journalctl -u nginx -f      # 实时跟踪 nginx 日志
journalctl -u app -f -n 50  # 先显示最后 50 行，再跟踪
```

`-n`（`--lines`）指定显示最近多少行，默认 10 行。

## 五、按优先级过滤

日志有 8 个级别（从高到低）：

| 级别 | 数字 | 含义 |
| --- | --- | --- |
| emerg | 0 | 系统不可用 |
| alert | 1 | 需立即处理 |
| crit | 2 | 严重 |
| err | 3 | 错误 |
| warning | 4 | 警告 |
| notice | 5 | 普通但重要 |
| info | 6 | 信息 |
| debug | 7 | 调试 |

```bash
journalctl -p err            # 只看错误及以上级别
journalctl -p warning -u nginx   # nginx 的警告及以上
journalctl -p 3              # 用数字：级别 ≤ 3（err 及以上）
```

## 六、输出格式与字段

```bash
journalctl -o short          # 默认：时间 主机 进程[pid]: 消息
journalctl -o verbose        # 完整字段（含 _PID、_UID 等元数据）
journalctl -o json           # JSON 格式（便于程序处理）
journalctl -o json-pretty    # 美化 JSON

# 只看某进程的日志
journalctl _PID=1234
# 只看某用户的日志
journalctl _UID=1000
```

## 七、常见实战场景

```bash
# 1. 排查服务启动失败：看本次启动以来某服务的错误
journalctl -b -u myservice -p err

# 2. 看最近 30 分钟系统整体日志
journalctl --since "30 min ago"

# 3. 实时跟踪 + 错误级别过滤
journalctl -f -p warning

# 4. 查看重启前一刻的日志，定位宕机原因
journalctl -b -1 -n 100

# 5. 磁盘占用排查：日志占了多少空间
journalctl --disk-usage

# 6. 清理旧日志（保留最近 100M）
journalctl --vacuum-size=100M
# 或按时间清理（保留最近 7 天）
journalctl --vacuum-time=7d
```

## 八、日志持久化与权限

- 默认情况下 journal 日志存在内存（`/run/log/journal`），重启后丢失。要持久化到 `/var/log/journal`：

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
```

- 普通用户默认只能看自己的日志，看系统日志需 `sudo`，或把用户加入 `systemd-journal` 组。

```bash
sudo usermod -aG systemd-journal amias   # 加入后可免 sudo 看日志
```

## 小结

- 基本：`journalctl`（全量）、`-b`（本次启动）、`-u`（服务）、`-f`（实时）、`-n`（行数）。
- 过滤：`--since/--until` 时间、`-p` 优先级、`_PID`/`_UID` 字段。
- 排查套路：`journalctl -b -u 服务 -p err` 先看本次启动的错误，`-f` 实时跟踪复现。
- 维护：`--disk-usage` 看占用、`--vacuum-size/time` 清理、持久化到 `/var/log/journal`。
