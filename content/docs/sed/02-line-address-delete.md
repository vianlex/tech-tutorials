---
title: 第二章 行定位与删除
linkTitle: 行定位与删除
description: 用行号、正则和范围精准定位文本，并用 d 删除、p 打印、q 退出
weight: 142
---

# 行定位与删除

sed 不只是「全文替换」，更强大的地方在于能**精准定位到某几行**，再对这些行单独操作。本章讲定位方法和最常见的「删除」操作。

## 行号定位 {#address-line}

直接用数字指定行。注意 sed 的行号从 **1** 开始：

```bash
# 只处理第 3 行：把这行的 apple 换成 orange
echo -e "a\nb\napple\nc" | sed '3 s/apple/orange/'
# 输出：
# a
# b
# orange
# c

# 只打印第 1 行
echo -e "a\nb\nc" | sed -n '1p'
# 输出：a
```

## 正则定位 {#address-regex}

用 `/正则/` 表示「匹配该正则的行」。这样命令只作用于符合条件的行：

```bash
# 只替换含 "error" 的行
echo -e "ok\nerror: timeout\nfine" | sed '/error/ s/timeout/TIMEOUT/'
# 输出：
# ok
# error: TIMEOUT
# fine

# 只打印含 "2024" 的行（相当于 grep 2024）
echo -e "2023 log\n2024 log" | sed -n '/2024/p'
# 输出：2024 log
```

## 范围定位 2,5 {#range-numbers}

用 `起始,结束` 表示「从第几行到第几行」的闭区间：

```bash
# 打印第 2 到第 4 行
echo -e "l1\nl2\nl3\nl4\nl5" | sed -n '2,4p'
# 输出：
# l2
# l3
# l4

# 删除第 2 到第 4 行（d 删除，见下节）
echo -e "l1\nl2\nl3\nl4\nl5" | sed '2,4d'
# 输出：
# l1
# l5
```

## 正则范围 /开始/,/结束/ {#range-regex}

用两个正则界定「从匹配 A 的行，到匹配 B 的行」：

```bash
# 打印从 <body> 到 </body> 之间的内容
echo -e "<head>\nx\n<body>\nhello\n</body>\ny" | sed -n '/<body>/,/<\/body>/p'
# 输出：
# <body>
# hello
# </body>
```

> 注意 `</body>` 里的 `/` 需要转义成 `\/`，或者换成别的分割符，例如 `\|</body>|`。

## 用 d 删除行 {#delete-d}

`d` 命令删除（不输出）当前匹配的行。这是清理文件的利器。

```bash
# 删除第 3 行
echo -e "a\nb\nc\nd" | sed '3d'
# 输出：
# a
# b
# d

# 删除所有含 "DEBUG" 的行（相当于 grep -v DEBUG）
echo -e "INFO x\nDEBUG y\nINFO z" | sed '/DEBUG/d'
# 输出：
# INFO x
# INFO z
```

## 用 ! 取反 {#negate}

在地址后加 `!`，表示「不匹配这些行才执行命令」：

```bash
# 删除除第 1 行以外的所有行（即只保留第 1 行）
echo -e "keep\ncut1\ncut2" | sed '1!d'
# 输出：keep

# 保留含 "error" 的行，其余删除
echo -e "ok\nerror a\nfine\nerror b" | sed '/error/!d'
# 输出：
# error a
# error b
```

## 删除空行 {#delete-blank}

空行（整行只有换行，或只有空白字符）很常见，删除它们能让文本更干净：

```bash
# 删除完全为空的行
echo -e "a\n\nb\n\nc" | sed '/^$/d'
# 输出：
# a
# b
# c

# 删除「空行或只有空格/制表符」的行（更彻底）
echo -e "a\n   \n\t\nb" | sed '/^[ \t]*$/d'
# 输出：
# a
# b
```

## 打印指定行 p {#print-p}

`p` 打印当前行。配合 `-n` 可以「只输出我关注的行」：

```bash
# 打印第 5 行到最后（模拟 tail -n +5）
echo -e "1\n2\n3\n4\n5\n6" | sed -n '5,$p'
# 输出：
# 5
# 6

# 打印奇数行
echo -e "a\nb\nc\nd\ne" | sed -n '1~2p'
# 输出：
# a
# c
# e
```

> `$` 表示最后一行，`1~2` 表示「从第 1 行起，每隔 2 行取一个」。

## 提前退出 q {#quit-q}

`q` 让 sed 读完当前行后立即退出，不再处理后续内容——处理超大文件时想「只看前几行」很有用：

```bash
# 只处理前 3 行就退出（比 sed -n '1,3p' 在大文件上更快）
echo -e "a\nb\nc\nd\ne" | sed '3q'
# 输出：
# a
# b
# c
```

## 综合小练习 {#practice}

把这些定位技巧组合起来：

```bash
# 删除第 1 行以及所有空行
sed '1d; /^$/d' notes.txt

# 只保留 10~20 行（删除其余）
sed '1,9d; 21,$d' data.txt

# 删除从 "# 配置开始" 到文件末尾的内容
sed '/# 配置开始/,$d' app.conf
```

## 小结 {#summary}

本章学会了用行号、正则、以及 `数字,数字` / `/正则/,/正则/` 范围来精准定位文本，并用 `d` 删除、`!` 取反、`p` 打印、`q` 提前退出。下一章将学习如何在指定位置「插入、追加、整行替换」内容。
