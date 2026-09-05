---
title: 第三章 变量与内置变量
linkTitle: 变量与内置变量
description: NR/NF/FNR/FS/OFS/RS/ORS、自定义变量与多文件处理
weight: 153
---

# 变量与内置变量

本章系统讲解 awk 的内置变量与自定义变量。内置变量让你可以获取行号、字段数、分隔符等信息；自定义变量用于计数、累加等中间状态。

## 行号 `NR` 与字段数 `NF` {#nr-nf}

- `NR`（Number of Record）：当前已经读到的**总行数**（跨文件累计）。
- `NF`（Number of Field）：当前行的**字段数**。

```bash
# 给每行加行号
echo -e "苹果\n香蕉\n橙子" | awk '{ print NR ". " $0 }'
# 输出：
# 1. 苹果
# 2. 香蕉
# 3. 橙子
```

```bash
# 打印字段数
echo -e "a b c\nd e" | awk '{ print "第" NR "行有" NF "个字段" }'
# 输出：
# 第1行有3个字段
# 第2行有2个字段
```

## 多文件：`FNR` vs `NR` {#fnr-vs-nr}

处理多个文件时，`NR` 跨文件累计，而 `FNR`（File Number of Record）在每个文件内**从 1 重新计数**。这是区分「第几个文件、第几行」的关键。

```bash
# 准备两个小文件
printf 'a1\na2\n' > /tmp/f1.txt
printf 'b1\nb2\nb3\n' > /tmp/f2.txt

# 对比 NR（全局累计）与 FNR（每文件独立）
awk '{ print "NR=" NR " FNR=" FNR " 内容=" $0 }' /tmp/f1.txt /tmp/f2.txt
# 输出：
# NR=1 FNR=1 内容=a1
# NR=2 FNR=2 内容=a2
# NR=3 FNR=1 内容=b1
# NR=4 FNR=2 内容=b2
# NR=5 FNR=3 内容=b3
```

实用场景：只在每个文件的第一行打印文件名（`FNR==1`）：

```bash
awk 'FNR==1 { print "=== 文件:" FILENAME " ===" } { print }' /tmp/f1.txt /tmp/f2.txt
# 输出：
# === 文件: /tmp/f1.txt ===
# a1
# a2
# === 文件: /tmp/f2.txt ===
# b1
# b2
# b3
```

> `FILENAME` 也是内置变量，表示当前正在处理的文件名。

## 输入分隔符 `FS` 与输出分隔符 `OFS` {#fs-ofs}

- `FS`（Field Separator）：输入字段分隔符，等价于 `-F`，可在 `BEGIN` 中设置。
- `OFS`（Output Field Separator）：`print` 多字段时的连接符。

```bash
# 在 BEGIN 里设置输入分隔符为逗号
echo "x,y,z" | awk 'BEGIN{FS=","} { print $1, $3 }'
# 输出：
# x z
```

同时设置输入/输出分隔符，完成格式转换：

```bash
echo "a:b:c" | awk 'BEGIN{FS=":"; OFS=" | "} { print $1, $2, $3 }'
# 输出：
# a | b | c
```

## 记录分隔符 `RS` 与 `ORS` {#rs-ors}

默认一行是一条「记录」（`RS="\n"`）。把 `RS` 改成其他字符，可以按段落/自定义边界切分；`ORS` 控制输出时记录之间用什么连接。

```bash
# 输入用空行分段，把 RS 设为空行，统计每段行数
printf 'a\nb\n\nc\nd\ne\n' | awk 'BEGIN{RS=""} { print "一段有" NF "个词" }'
# 输出：
# 一段有2个词
# 一段有3个词
```

把 `RS` 设为逗号，按逗号切分（适合紧凑数据）：

```bash
echo "10,20,30" | awk 'BEGIN{RS=","} { print "值:" $0 }'
# 输出：
# 值:10
# 值:20
# 值:30
```

## 整行 `$0` 与字符串连接 {#dollar0-concat}

`$0` 是整个当前记录。awk 中**字符串直接相邻即为连接**，无需 `+` 或 `.`：

```bash
# 拼接字符串
echo "awk" | awk '{ s = "学习" $0 "很有趣"; print s }'
# 输出：
# 学习awk很有趣
```

也可对 `$0` 整体替换后输出：

```bash
echo "hello world" | awk '{ $0 = ">> " $0; print }'
# 输出：
# >> hello world
```

## 自定义变量 {#user-vars}

变量无需声明，首次赋值即用。常用作计数器、累加器。

```bash
# 统计非空行数
echo -e "a\n\nb\nc" | awk 'NF>0 { count++ } END { print "非空行数:", count }'
# 输出：
# 非空行数: 3
```

累加求和（自定义变量 `sum`）：

```bash
echo -e "10\n20\n30" | awk '{ sum = sum + $1 } END { print "总和:", sum }'
# 输出：
# 总和: 60
```

## 用 `-v` 从外部传入变量 {#pass-var}

`-v name=value` 把 shell 变量传给 awk，方便脚本参数化。

```bash
# 用 shell 变量 threshold 控制阈值
threshold=80
echo -e "70\n85\n90" | awk -v t="$threshold" '$1 > t { print $1 " 超阈值" }'
# 输出：
# 85 超阈值
# 90 超阈值
```

## 常用例子 {#examples}

**例 1：给行加行号并标注字段数**

```bash
echo -e "cat dog\nbird" | awk '{ print NR") " $0 "  (字段:" NF ")" }'
# 输出：
# 1) cat dog  (字段:2)
# 2) bird  (字段:1)
```

**例 2：统计每个文件各有多少行**

```bash
awk '{ n[FILENAME]++ } END { for (f in n) print f ": " n[f] " 行" }' /tmp/f1.txt /tmp/f2.txt
# 输出（顺序可能不同）：
# /tmp/f1.txt: 2 行
# /tmp/f2.txt: 3 行
```

**例 3：跳过某文件的前 N 行**（用 FNR 实现）

```bash
# 每个文件跳过第 1 行（表头）
awk 'FNR>1 { print }' /tmp/f1.txt /tmp/f2.txt
# 输出：
# a2
# b2
# b3
```

**例 4：改变记录分隔符统计段落**

```bash
printf '标题\n正文1\n\n标题2\n正文2\n' | awk 'BEGIN{RS=""} { print "第" NR "段:" }'
# 输出：
# 第1段:
# 第2段:
```

## 小结 {#summary}

本章掌握了内置变量 `NR`/`NF`/`FNR`/`FS`/`OFS`/`RS`/`ORS`/`FILENAME`，以及自定义变量与 `-v` 传参，能完成加行号、统计字段数、多文件分别计数等任务。下一章将用这些变量做真正的统计计算：求和、计数、平均值、最大最小值，并用 `printf` 美化输出。
