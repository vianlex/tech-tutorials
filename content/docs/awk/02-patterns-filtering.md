---
title: 第二章 模式与条件过滤
linkTitle: 模式与过滤
description: BEGIN/END、比较与逻辑运算符、正则匹配与条件过滤
weight: 152
---

# 模式与条件过滤

本章学习如何用「模式」筛选要处理的行：`BEGIN`/`END` 在首尾做预处理与收尾、比较/逻辑运算符做条件判断、正则 `/pattern/` 做文本匹配，以及范围模式和空行处理。

## BEGIN 与 END 块 {#begin-end}

`BEGIN { ... }` 在读入数据**之前**执行，常用来打印表头、设置变量；`END { ... }` 在**所有行处理完之后**执行，常用来输出统计结果。

```bash
# 打印表头 + 数据 + 表尾
echo -e "张三 90\n李四 85" | awk 'BEGIN{print "姓名 分数"} {print $1, $2} END{print "---- 结束 ----"}'
# 输出：
# 姓名 分数
# 张三 90
# 李四 85
# ---- 结束 ----
```

常见用法：用 `BEGIN` 设置分隔符（等价于 `-F`）：

```bash
echo "a,b,c" | awk 'BEGIN{FS=","} {print $1, $2}'
# 输出：
# a b
```

## 比较运算符 {#comparison}

可用 `<` `>` `<=` `>=` `==` `!=` 比较数值或字符串。写在模式位置，满足条件的行才执行动作。

```bash
# 输入：姓名 分数，只打印分数 >= 90 的行
echo -e "张三 95\n李四 82\n王五 91" | awk '$2 >= 90 { print $1, $2 }'
# 输出：
# 张三 95
# 王五 91
```

字符串相等比较（注意用 `==`）：

```bash
echo -e "ok 1\nfail 2\nok 3" | awk '$1 == "ok" { print $0 }'
# 输出：
# ok 1
# ok 3
```

## 逻辑运算符 `&&`、`||`、`!` {#logical}

组合多个条件：与 `&&`、或 `||`、非 `!`。

```bash
# 输入：姓名 年龄 分数，筛选 年龄>=18 且 分数>=60（成年且及格）
echo -e "张三 20 70\n李四 16 80\n王五 19 55" | awk '$2 >= 18 && $3 >= 60 { print $1 }'
# 输出：
# 张三
```

或运算示例：匹配失败或分数过低：

```bash
echo -e "ok 90\nfail 10\nok 20" | awk '$1 == "fail" || $2 < 30 { print $0 }'
# 输出：
# fail 10
# ok 20
```

取反：排除空行之外的处理（配合下一节的空行判断）：

```bash
echo -e "a\n\nb" | awk '!($0 == "") { print "非空:", $0 }'
# 输出：
# 非空: a
# 非空: b
```

## 正则匹配 `/pattern/` {#regex}

直接用 `/正则/` 作为模式，匹配整行。

```bash
# 输入：日志行，只保留含 "ERROR" 的行
echo -e "INFO start\nERROR timeout\nDEBUG ping\nERROR crash" | awk '/ERROR/'
# 输出：
# ERROR timeout
# ERROR crash
```

反向匹配 `!`：排除某些行：

```bash
echo -e "INFO a\nERROR b\nINFO c" | awk '!/INFO/'
# 输出：
# ERROR b
```

## 字段匹配：`~` 与 `!~` {#match-op}

`字段 ~ /正则/` 只匹配**某个字段**，而非整行；`!~` 表示不匹配。

```bash
# 只匹配第 1 列是纯数字的行的第 2 列
echo -e "100 apple\nabc banana\n200 cherry" | awk '$1 ~ /^[0-9]+$/ { print $2 }'
# 输出：
# apple
# cherry
```

排除第 2 列含 "test" 的行：

```bash
echo -e "a test1\nb real\nc test2" | awk '$2 !~ /test/ { print $0 }'
# 输出：
# b real
```

## 范围模式 {#range}

`/起点正则/, /终点正则/` 会选中「从匹配起点到匹配终点」之间的所有行（含两端），适合截取日志片段。

```bash
# 输入：多段日志，截取从 START 到 END 的部分
echo -e "header\nSTART line1\nmid line2\nEND line3\ntrailer" | awk '/START/,/END/'
# 输出：
# START line1
# mid line2
# END line3
```

## 空行与空白处理 {#blank-lines}

判断空行：`$0 == ""`；跳过空行：`/^$/ { next }`（`next` 表示跳过当前行后续动作）。

```bash
# 跳过空行后打印非空行行号
echo -e "a\n\nb\n" | awk 'NF==0 { next } { print NR": "$0 }'
# 输出：
# 1: a
# 3: b
```

`NF==0` 比 `$0==""` 更稳妥，因为它还能过滤「只有空格」的行（空格切分后字段数为 0）。

## 常用例子：条件过滤 {#examples}

**例 1：过滤超过阈值的数据行**

```bash
# 找出 CPU 使用率 > 80% 的记录（第 2 列为百分比）
echo -e "web 82\ndb 45\ncache 91" | awk '$2 > 80 { print $1 " 告警:" $2 "%" }'
# 输出：
# web 告警:82%
# cache 告警:91%
```

**例 2：匹配关键词并格式化**

```bash
echo -e "order created\npay failed\norder paid" | awk '/order/ { print "[订单] " $2 }'
# 输出：
# [订单] created
# [订单] paid
```

**例 3：统计符合条件的行数（BEGIN/END 配合）**

```bash
echo -e "ok 1\nfail 2\nok 3\nfail 4" | awk '/fail/ { c++ } END { print "失败次数:", c }'
# 输出：
# 失败次数: 2
```

**例 4：多条件筛选日志级别**

```bash
echo -e "INFO x\nWARN y\nERROR z\nWARN w" | awk '$1=="WARN" || $1=="ERROR"'
# 输出：
# WARN y
# ERROR z
# WARN w
```

## 小结 {#summary}

本章学会了用 `BEGIN`/`END` 做首尾处理、用比较与逻辑运算符构造条件、用 `/正则/` 与 `~`/`!~` 做匹配、用范围模式截取片段、以及跳过空行。下一章将系统讲解内置变量（`NR`/`NF`/`FNR`/`FS`/`OFS`/`RS`/`ORS`）与自定义变量，让你能做行号标注、多文件处理等更灵活的操作。
