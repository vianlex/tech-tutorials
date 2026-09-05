---
title: 第一章 sed 基础与替换
linkTitle: 基础与替换
description: 认识 sed、掌握最基本的 s/旧/新/ 替换语法与常用选项
weight: 141
---

# sed 基础与替换

本章先认识 sed 是什么、它如何工作，然后聚焦最常用的「替换」操作——这也是 sed 九成场景的核心。

## 什么是 sed {#what-is-sed}

sed 是 *Stream Editor*（流编辑器）的缩写。它一次读入一行文本，对这行应用你给的命令，再把结果输出；然后读下一行，如此循环。因为它「流式」处理，所以特别擅长处理大文件而无需一次性加载进内存。

典型用途：

- 批量替换文件里的某个词（比如把 `http` 改成 `https`）
- 删除空行、注释行
- 从日志里提取关键字段
- 在每行的开头/结尾加上内容

## 基本语法 {#basic-syntax}

sed 最经典的语法是「替换」：

```bash
sed 's/旧文本/新文本/' 文件名
```

`s` 表示 substitute（替换），`/ ` 是分隔符（也可以换成 `#`、`|` 等，后面会讲）。例如把 `apple` 换成 `orange`：

```bash
echo "I like apple" | sed 's/apple/orange/'
# 输出：I like orange
```

注意：上面的命令**不会修改原文件**，只是把改完的结果打印到屏幕上。这是 sed 的默认行为——只读不改源文件。

## sed 的工作方式 {#how-it-works}

理解 sed 的工作方式有助于避免困惑：

1. 从输入（文件或管道）读取**一行**到「模式空间」（pattern space，一块临时内存）。
2. 对这行依次执行你给的命令。
3. 默认会把模式空间的内容打印出来。
4. 清空模式空间，读取下一行，重复直到文件结束。

因为第 3 步是「默认打印」，所以你常常看到输出里既有被改的行、也有没改的行——它们都被原样打印了。

```bash
# 只有含 "error" 的行会被替换，但所有行都会打印
echo -e "ok\nerror code\nfine" | sed 's/error/ERROR/'
# 输出：
# ok
# ERROR code
# fine
```

## 用 -n 与 p 控制打印 {#n-and-p}

默认每读一行都打印，这有时会输出太多。加 `-n` 选项可以**关闭默认打印**，然后用 `p` 命令显式指定「只打印我关心的行」。

```bash
# 只打印发生了替换的行
echo -e "ok\nerror code\nfine" | sed -n 's/error/ERROR/p'
# 输出：ERROR code

# 只打印第 2 行
echo -e "line1\nline2\nline3" | sed -n '2p'
# 输出：line2
```

`-n` + `p` 的组合是「精准只显示我要的行」的常用手法。

## 用 -i 原地修改文件 {#in-place}

要真正改文件，而不是只在屏幕上看到结果，用 `-i`（in-place，原地）选项：

```bash
# 把文件里所有 apple 改成 orange，并直接写回文件
sed -i 's/apple/orange/' fruits.txt
```

> ⚠️ 危险提示：`-i` 会直接覆盖原文件，没有撤销！建议先不加 `-i` 在屏幕上验证结果，确认无误再加 `-i`。也可以先备份：
>
> ```bash
> # GNU sed：加 -i.bak 会在修改前生成 fruits.txt.bak 备份
> sed -i.bak 's/apple/orange/' fruits.txt
> ```

macOS（BSD sed）的 `-i` 写法不同，详见[第五章](../05-advanced-caveats/)。

## 全局替换 g {#global-flag}

默认情况下，一行里**只替换第一个**匹配。要替换一行里的**所有**匹配，加 `g`（global）标志：

```bash
echo "a-a-a" | sed 's/a/b/'
# 输出：b-a-a   （只改了第一个）

echo "a-a-a" |  sed 's/a/b/g'
# 输出：b-b-b   （全部替换）
```

`g` 也可以限制替换次数，比如 `s/a/b/2` 表示只替换第 2 个：

```bash
echo "a-a-a-a" | sed 's/a/b/2'
# 输出：a-b-a-a
```

## 用 & 引用匹配内容 {#ampersand}

在「新文本」里，`&` 代表「刚刚匹配到的整段内容」。常用于给匹配到的东西加前后缀：

```bash
# 给所有数字两边加上括号
echo "订单 100 和 200" | sed 's/[0-9]\+/(&)/g'
# 输出：订单 (100) 和 (200)

# 把邮箱整体用尖括号包起来
echo "联系 alice@example.com" | sed 's/[a-z]*@[a-z.]*/<&>/'
# 输出：联系 <alice@example.com>
```

## 分组与反向引用 \1 {#backreference}

用 `\(...\)` 把一部分匹配「分组」，在替换里用 `\1`、`\2`……引用第 1、2 个分组。这是重排文本顺序的利器。

```bash
# 把 "名 姓" 改成 "姓, 名"
echo "Alice Wong" | sed 's/\([A-Za-z]*\) \([A-Za-z]*\)/\2, \1/'
# 输出：Wong, Alice
```

实用例子——交换日期的「月-日」顺序（假设格式 `09-06` 改成 `06-09`）：

```bash
echo "生日 09-06" | sed 's/\([0-9][0-9]\)-\([0-9][0-9]\)/\2-\1/'
# 输出：生日 06-09
```

## 分隔符可以更换 {#delimiter}

当「旧文本」里本身含有 `/`（比如路径）时，继续用 `/` 作分隔符会很麻烦。可以换成 `#`、`|` 等任意字符：

```bash
# 用 # 作分隔符，替换文件路径
echo "/var/log/app.log" | sed 's#/var/log#/data/log#'
# 输出：/data/log/app.log

# 用 | 作分隔符
echo "a|b|c" | sed 's|a|X|'
# 输出：X|b|c
```

## 常用例子 {#common-examples}

把前面学到的用法串起来，下面是日常最高频的几个：

```bash
# 1) 把 http 改成 https（整文件，原地）
sed -i 's/http:/https:/g' config.txt

# 2) 去掉每行行首的空格和制表符
sed 's/^[ \t]*//' file.txt

# 3) 把连续的多个空格压缩成单个空格
sed 's/  */ /g' file.txt

# 4) 给每个邮箱打码：显示前两位 + 星号
echo "alice@example.com" | sed 's/\(..\)[a-z]*@/\1***@/'
# 输出：al***@example.com

# 5) 替换 Windows 换行带来的 ^M（\r）
sed 's/\r$//' windows_file.txt > unix_file.txt
```

## 小结 {#summary}

本章掌握了 sed 的「替换」核心：`s/旧/新/` 基本语法、`-n`+`p` 精准打印、`-i` 原地修改、`g` 全局替换、`&` 引用匹配、`\(\)` 分组与 `\1` 反向引用，以及分隔符的灵活更换。下一章将学习如何精准「定位到某几行」并对它们做删除等操作。
