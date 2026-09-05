---
title: 第一章 awk 基础与字段
linkTitle: 基础与字段
description: awk 基本结构、print、字段切分与分隔符
weight: 151
---

# awk 基础与字段

本章介绍 awk 是什么、最基本的 `awk '模式 {动作}'` 结构，以及如何按字段（列）切分文本并提取需要的内容。

## 什么是 awk {#what-is-awk}

awk 是一个「按行扫描、按列处理」的文本分析工具。它逐行读取输入，默认把每行按空白切成若干字段，你可以指定「对哪些行、做哪些操作」。常见用途：

- 从日志、CSV、配置文件里提取某一列
- 按条件过滤行、统计行数/求和
- 把一种格式的文本转换成另一种格式

awk 有多种实现，本教程以 GNU awk（`gawk`）5.x 为准。绝大多数 Linux/macOS 上的 `awk` 实际就是 `gawk` 或兼容版本。

```bash
# 查看 awk 版本（确认是 gawk）
awk --version
# GNU Awk 5.1.0, API: 3.0 (GNU MPFR 4.1.0, GNU MP 6.2.0)
```

## 基本结构：模式 + 动作 {#structure}

awk 程序的核心结构是：

```awk
awk '模式 { 动作 }' 文件
```

- **模式**（pattern）：决定「哪些行会被处理」，可省略（省略表示处理所有行）。
- **动作**（action）：花括号里的语句，决定「对这些行做什么」，通常是 `print`。

最简单的例子——打印每一行：

```bash
# 输入：一个多行文本
echo -e "hello\nworld\nawk" | awk '{ print }'
# 输出：
# hello
# world
# awk
```

省略动作时，awk 默认就是 `print $0`（打印整行），所以 `awk '{print}'` 与 `awk '{print $0}'` 等价。

## print 与字段 `$1`、`$2`、`$0` {#fields}

awk 把每行按分隔符切成字段，用 `$1`、`$2`… 引用第 1、2… 个字段，`$0` 表示整行。

```bash
# 输入：姓名 年龄 城市
echo -e "张三 25 北京\n李四 30 上海\n王五 28 广州" | awk '{ print $1, $3 }'
# 输出（默认用空格分隔打印的字段）：
# 张三 北京
# 李四 上海
# 王五 广州
```

提取整行 `$0`：

```bash
echo "only one line" | awk '{ print "读到：", $0 }'
# 输出：
# 读到： only one line
```

> 提示：`print` 后面多个参数用逗号分隔，awk 会用输出分隔符 `OFS`（默认空格）把它们连起来。

## 字段数量 `$NF` 与行号 `$NR` {#nf-nr}

- `$NF`：当前行的**最后一个**字段（`NF` 是字段数量，`$NF` 就是最后一列）。
- `$NR`：awk 没有 `$NR` 这种用法，行号直接用 `NR`（见第三章）。这里先记住 `$NF` 取最后一列。

```bash
# 输入：每行字段数不固定
echo -e "a b c\nx y" | awk '{ print "最后一列=", $NF, " 字段数=", NF }'
# 输出：
# 最后一列= c  字段数= 3
# 最后一列= y  字段数= 2
```

实用场景：取每行最后一个字段（例如文件路径、版本号）：

```bash
echo -e "/usr/local/bin/gawk\n/opt/app/v2" | awk '{ print $NF }'
# 输出：
# /usr/local/bin/gawk
# /opt/app/v2
```

## 指定分隔符 `-F` {#field-separator}

默认分隔符是「连续的空白」。遇到 CSV（逗号分隔）、冒号分隔的 `/etc/passwd` 等，用 `-F` 指定分隔符。

```bash
# 用逗号分隔，提取第 1、第 2 列（CSV 示例）
echo "苹果,5,3.5" | awk -F',' '{ print $1, "数量", $2 }'
# 输出：
# 苹果 数量 5
```

处理 `/etc/passwd`（冒号分隔），取用户名和登录 shell：

```bash
awk -F':' '{ print $1, "->", $NF }' /etc/passwd
# 输出（节选）：
# root -> /bin/bash
# daemon -> /usr/sbin/nologin
```

`-F` 也支持正则表达式，例如同时按冒号或分号切分：

```bash
echo "a:b;c" | awk -F'[:;]' '{ print $1, $2, $3 }'
# 输出：
# a b c
```

## 输出分隔符 `OFS` {#ofs}

`print` 打印多个字段时，用什么字符连接由 `OFS`（输出字段分隔符）决定，默认是空格。可以用 `-v OFS=...` 修改：

```bash
# 把 CSV 的逗号改成制表符（TAB），方便粘贴到表格
echo "苹果,5,3.5" | awk -F',' -v OFS='\t' '{ print $1, $2, $3 }'
# 输出（制表符分隔）：
# 苹果	5	3.5
```

也可以在 `BEGIN` 里设置（下一章详讲 `BEGIN`）：

```bash
echo "a b c" | awk 'BEGIN{OFS="-"} {print $1,$2,$3}'
# 输出：
# a-b-c
```

## 常用例子：提取与打印列 {#examples}

**例 1：提取日志里的访问路径**（假设第 1 列是 IP，第 2 列是路径）

```bash
echo -e "10.0.0.1 /index.html\n10.0.0.2 /login" | awk '{ print $2 }'
# 输出：
# /index.html
# /login
```

**例 2：打印整行 + 行内字段数**

```bash
echo -e "a b c\nd e" | awk '{ print $0, "[字段数:" NF "]" }'
# 输出：
# a b c [字段数:3]
# d e [字段数:2]
```

**例 3：用 `-F` 读取指定列并重新排版**

```bash
# 输入：日期,金额,备注
echo -e "2024-01-01,100,餐费\n2024-01-02,50,交通" | awk -F',' '{ print $2 " 元 - " $3 }'
# 输出：
# 100 元 - 餐费
# 50 元 - 交通
```

## 小结 {#summary}

本章掌握了 awk 的 `模式 {动作}` 结构、`print` 与字段 `$1/$0/$NF`、`-F` 指定分隔符、`OFS` 控制输出分隔符。你已经能完成「提取某列、打印整行、按分隔符切分」等日常任务。下一章将学习如何用模式和条件过滤行，例如「只打印金额大于 100 的行」「匹配关键词的行」。
