---
title: 第三章：grep 文本检索
linkTitle: grep 文本检索
description: 正则匹配、上下文、递归搜索、反向匹配、常用选项
weight: 183
---

# grep 文本检索

`grep` 是文本检索神器，能在文件或命令输出中**按模式（正则）查找匹配行**，是排查日志、分析代码的必备命令。

## 一、基本语法

```bash
grep [选项] "模式" 文件...
```

```bash
grep "error" app.log              # 在文件中查找含 error 的行
grep "error" *.log                # 在多个文件中查找
cat app.log | grep "error"        # 从管道输入查找
```

返回所有**包含**匹配字符串的行。无匹配时返回空，退出码为 1（可用在脚本判断）。

## 二、常用选项

```bash
grep -i "error" app.log          # 忽略大小写
grep -v "debug" app.log          # 反向匹配：排除含 debug 的行
grep -n "error" app.log          # 显示行号
grep -c "error" app.log          # 只统计匹配行数
grep -w "main" file              # 整词匹配（不匹配 mainFunction）
grep -r "TODO" ./src             # 递归搜索目录
grep -l "TODO" *.js              # 只列出含匹配的文件名
grep -E "err|fail" app.log       # 扩展正则（支持 | 等）
grep -F "a.b" file               # 固定字符串（. 不当作通配）
```

## 三、显示上下文（排查日志必备）

匹配行的前后文往往有关键信息：

```bash
grep -B 3 "error" app.log   # 匹配行前 3 行（Before）
grep -A 5 "error" app.log   # 匹配行后 5 行（After）
grep -C 3 "error" app.log   # 前后各 3 行（Context）
```

## 四、正则表达式

`grep` 默认用**基础正则**，`-E`（或 `egrep`）用**扩展正则**，`-P` 用 PCRE（支持更多语法）。

```bash
# 基础字符类
grep "err.r" file           # . 匹配任意单字符
grep "^2026" log            # ^ 行首
grep "error$" log           # $ 行尾
grep "a[0-9]b" file         # [] 字符类
grep "a.*b" file            # * 前一个字符重复 0+ 次

# 扩展正则（-E）
grep -E "error|fail|timeout" log      # | 或
grep -E "a+" file                     # + 前一个字符 1+ 次
grep -E "a{2,4}" file                 # {m,n} 重复 m~n 次
grep -E "colou?r" file                # ? 可选（color/colour）
grep -E "(err|fail)[0-9]+" log        # 分组
```

## 五、常见实战场景

```bash
# 1. 看日志中的错误及其前后文
grep -n -C 3 -i "error" /var/log/app.log

# 2. 统计每个错误出现次数
grep -oE "[A-Za-z]+Error" app.log | sort | uniq -c | sort -rn

# 3. 递归搜索代码里的 TODO
grep -rn "TODO" ./src --include="*.js"

# 4. 排除某些目录/文件搜索
grep -rn "keyword" . --exclude-dir=node_modules --exclude="*.min.js"

# 5. 找配置文件里非注释、非空的有效行
grep -vE "^\s*(#|$)" nginx.conf

# 6. 实时跟踪日志中匹配的行
tail -f app.log | grep --line-buffered "error"

# 7. 匹配 IP 地址
grep -oE "[0-9]{1,3}(\.[0-9]{1,3}){3}" access.log
```

## 六、与其他命令组合

`grep` 常和 `find`、`xargs`、`wc` 等组合：

```bash
# 在 find 找到的文件里搜索内容
find /var/log -name "*.log" | xargs grep -l "error"

# 统计匹配行数
grep -c "error" app.log

# 高亮匹配（很多发行版已默认开启 --color）
grep --color=auto "error" app.log
```

## 七、grep 家族

- `grep`：标准文本搜索。
- `egrep` = `grep -E`：扩展正则。
- `fgrep` = `grep -F`：固定字符串。
- `rg`（ripgrep）：现代替代品，速度更快、默认递归、自动忽略 .gitignore，推荐在大型代码库使用。

## 小结

- 基本：`grep "模式" 文件`，加 `-i` 忽略大小写、`-v` 反向、`-n` 行号、`-r` 递归。
- 上下文：`-A`（后）、`-B`（前）、`-C`（前后），排查日志必备。
- 正则：基础正则 + `-E` 扩展正则（`|`、`+`、`?`、`{m,n}`）。
- 组合：`grep | sort | uniq -c | sort -rn` 统计、`find | xargs grep` 批量搜内容。
