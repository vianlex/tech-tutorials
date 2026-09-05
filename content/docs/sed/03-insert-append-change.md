---
title: 第三章 插入、追加与修改
linkTitle: 插入与修改
description: 用 a 追加、i 插入、c 整行替换、y 字符转换，以及多命令和脚本文件
weight: 143
---

# 插入、追加与修改

除了替换行内的文本，sed 还能在指定位置「加一行」或「整行换掉」。本章讲解 `a`/`i`/`c` 等命令，以及多命令的执行方式。

## 用 a 追加一行 {#append-a}

`a`（append）在**匹配行之后**追加新行：

```bash
# 在第 2 行之后追加一行
echo -e "line1\nline2\nline3" | sed '2a 这是新加的一行'
# 输出：
# line1
# line2
# 这是新加的一行
# line3

# 在含 "apple" 的行之后追加
echo -e "apple\nbanana" | sed '/apple/a 下面也是水果'
# 输出：
# apple
# 下面也是水果
# banana
```

> GNU sed 支持 `a\` 后直接跟文本（`a 文本`），写法如上。macOS BSD sed 需要 `a\` 换行后写文本，详见第五章。

## 用 i 插入一行 {#insert-i}

`i`（insert）在**匹配行之前**插入新行，与 `a` 方向相反：

```bash
# 在第 1 行之前插入标题
echo -e "内容A\n内容B" | sed '1i # 这是标题'
# 输出：
# # 这是标题
# 内容A
# 内容B

# 在含 "错误" 的行之前加一行警告
echo -e "正常\n错误发生了" | sed '/错误/i [警告] 上一行有问题'
# 输出：
# 正常
# [警告] 上一行有问题
# 错误发生了
```

## 用 c 整行替换 {#change-c}

`c`（change）把**整行**换成新内容（不管原来行里有什么）：

```bash
# 把第 2 行整体换成别的
echo -e "a\nb\nc" | sed '2c 替换后的第二行'
# 输出：
# a
# 替换后的第二行
# c

# 把含 "TODO" 的整行替换成 "DONE"
echo -e "写代码\nTODO: 测试\n上线" | sed '/TODO/c DONE: 测试已完成'
# 输出：
# 写代码
# DONE: 测试已完成
# 上线
```

## 用 y 字符转换 {#translate-y}

`y/源字符集/目标字符集/` 做**一对一字符映射**（类似 `tr`），不能用于字符串：

```bash
# 把 a 换成 A、b 换成 B（逐字符）
echo "abcabc" | sed 'y/abc/ABC/'
# 输出：ABCABC

# 把小写月份首字母等做映射
echo "mon tue wed" | sed 'y/mtw/MTW/'
# 输出：Mon Tue Wed
```

> 注意 `y` 是字符级替换：`y/abc/XYZ/` 表示 a→X、b→Y、c→Z，两边字符个数必须相等。

## 多命令 -e {#multi-e}

一行里想执行多条 sed 命令，用 `-e` 分隔（或用 `;` 在同一脚本里分号隔开）：

```bash
# 方式一：多个 -e
echo "hello world" | sed -e 's/hello/HELLO/' -e 's/world/WORLD/'
# 输出：HELLO WORLD

# 方式二：用分号把命令写在一起
echo "hello world" | sed 's/hello/HELLO/; s/world/WORLD/'
# 输出：HELLO WORLD

# 组合：删除空行 + 把 tab 换成空格
sed -e '/^$/d' -e 's/\t/ /g' file.txt
```

## 脚本文件 -f {#script-f}

当命令很多、很复杂时，把 sed 命令写进一个 `.sed` 脚本文件，用 `-f` 调用，可维护性强：

```bash
# 先把命令写进脚本文件 clean.sed
cat > clean.sed <<'EOF'
# 删除空行
/^$/d
# 删除注释行
/^[ \t]*#/d
# 把 tab 替换成空格
s/\t/ /g
# 行首去空格
s/^[ \t]*//
EOF

# 用 -f 调用脚本处理文件
sed -f clean.sed input.txt
```

脚本文件里每行就是一条 sed 命令，`#` 开头为注释。

## 组合 a/i/c 的实用例子 {#combine-ai}

```bash
# 在文件开头插入版权声明行
sed '1i # Copyright 2024 公司名' -i config.txt

# 给每个含 "function" 的函数定义后加一个空行做分隔
sed '/function/a ' script.js

# 把所有 "# 待办" 注释整行改成已完成
sed '/# 待办/c # 已完成' -i todos.md
```

## 小结 {#summary}

本章掌握了对行「增删改」的骨架命令：`a` 在行后追加、`i` 在行前插入、`c` 整行替换、`y` 做字符映射，以及用 `-e` 串联多条命令、用 `-f` 调用脚本文件。下一章将系统讲解 sed 的正则语法，并给出一批真实可用的实战场景。
