---
title: 第五章 综合实战与注意事项
linkTitle: 实战与注意
description: 组合案例、CSV/日志处理、-E 扩展正则、GNU 与 macOS 差异与速查表
weight: 145
---

# 综合实战与注意事项

最后一章把前面所有技巧组合起来，处理更接近真实工作的数据，并重点提醒 GNU sed 与 macOS BSD sed 的差异和常见坑。

## 扩展正则 -E（GNU sed）{#extended-e}

基础正则（BRE）里 `+`、`?`、`()`、`{}` 都要加 `\`，写起来累。GNU sed 用 `-E` 切换到**扩展正则（ERE）**，这些符号直接可用，可读性大幅提升：

```bash
# BRE 写法（要转义）
echo "电话 138-0000-0000" | sed 's/[0-9]\{3,4\}-\([0-9]\+\)/\1/'

# ERE 写法（-E，更清爽）
echo "电话 138-0000-0000" | sed -E 's/[0-9]{3,4}-([0-9]+)/\1/'
# 输出：电话 0000-0000
```

> 经验：凡是要写 `+`、`?`、`()`、`{}` 时，优先用 `sed -E`，少写一堆反斜杠，出错概率也更低。

## 兼容写法 -r {#compat-r}

`-r` 在 GNU sed 里与 `-E` 等价（都是开启扩展正则），老脚本里常见 `-r`。新代码推荐写 `-E`（更符合 POSIX/新版约定，macOS 也支持 `-E`）。

```bash
# 以下两者在 GNU sed 上效果相同
sed -r 's/(foo)+/X/' file.txt
sed -E 's/(foo)+/X/' file.txt
```

## 平台差异：GNU vs macOS {#platform-diff}

这是**最容易踩的坑**。`-i`（原地修改）在两个系统上行为不同：

```bash
# GNU sed（Linux）：-i 后可直接跟脚本
sed -i 's/foo/bar/' file.txt

# macOS / BSD sed：要求 -i 后跟「备份后缀参数」，哪怕是空串
sed -i '' 's/foo/bar/' file.txt      # 空串 = 不备份
sed -i.bak 's/foo/bar/' file.txt     # 生成 file.txt.bak 备份

# 追加/插入命令的换行也不同
# GNU:  sed '1a 新行'
# macOS:  sed '1a\' 然后换行写 新行（或用 $'\n'）
```

**跨平台安全写法**：如果脚本要同时跑在 Linux 和 macOS 上，推荐用 `-i ''` 的写法（GNU sed 也接受空后缀），或者用「先输出到临时文件再覆盖」的方式避免 `-i` 差异：

```bash
# 跨平台稳妥方案：重定向到临时文件再覆盖
sed 's/foo/bar/' file.txt > file.txt.tmp && mv file.txt.tmp file.txt
```

> 判断系统：Linux 上 `sed --version` 有输出；macOS 上会报「illegal option」。可在脚本里据此分支。

## 综合实战：处理 CSV {#csv-case}

假设有个 `users.csv`：`name,age,city`，要把城市统一大写、删除年龄小于 18 的行：

```bash
# 城市列（第 3 列）转大写（用 y 或 tr 思路，这里展示分组）
echo "alice,20,beijing" | sed -E 's/^([^,]+),([^,]+),([a-z]+)$/\1,\2,\U\3/'
# 注：\U 是 GNU sed 扩展，把后续转大写；输出 alice,20,BEIJING

# 删除 age 列（第 2 列）小于 18 的行（用正则排除 0-17 开头的两位年龄）
sed -E '/^[^,]+,(0?[0-9]|1[0-7]),/d' users.csv
```

> 复杂 CSV 建议交给 `awk`/`csvkit`，sed 适合「格式规整」的简单处理。

## 综合实战：聚合日志分析 {#log-case}

从 Nginx access.log 里统计访问最多的 IP（配合 sort/uniq）：

```bash
# 提取第一列 IP，排序去重计数，取前 10
sed -E 's/^([0-9.]+) .*/\1/' access.log | sort | uniq -c | sort -rn | head -10

# 把响应时间超过 1 秒（1000ms）的请求单独拎出来
sed -nE 's/.*response_time=([0-9]+)ms.*/\1 &/p' app.log | awk '$1 > 1000'

# 把日志里的日期格式 06/Sep/2024 统一成 2024-09-06
sed -E 's#([0-9]{2})/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/([0-9]{4})#\3-\2-\1#' access.log
```

## 常见坑与解决 {#pitfalls}

| 坑 | 现象 | 解决 |
|----|------|------|
| 加了 `-i` 文件变了没法恢复 | 源文件被覆盖 | 先预览，再 `-i`；或 `-i.bak` 留备份 |
| 替换里含 `/` 报错 | `s/a/b/c` 把路径拆坏了 | 换分隔符 `s#a#b#` 或转义 `\/` |
| 一行只替换了第一个 | 忘了 `g` | 加 `g`：`s/a/b/g` |
| `.*` 贪婪吃太多 | 匹配越过预期 | 用 `[^x]*` 限定边界 |
| macOS 上 `-i` 报非法参数 | BSD 语法不同 | 用 `sed -i ''` 或临时文件法 |
| 变量没展开 | 用单引号包了 `$VAR` | 用双引号 `"s/$VAR/new/"` 或在脚本里拼 |
| 特殊字符被 shell 解释 | `$`、`*` 出错 | 用单引号包裹 sed 脚本 |

## 与原地修改的变量结合 {#variable}

```bash
# 用 shell 变量做替换（双引号让变量展开）
OLD="staging"
NEW="production"
sed -i "s/$OLD/$NEW/g" deploy.conf

# 若变量含 / 等特殊字符，先转义再传入（简单场景）
sed -i "s#$OLD#$NEW#g" deploy.conf   # 改用 # 分隔更稳
```

## 速查表 {#cheatsheet}

```text
# 基础替换
sed 's/旧/新/' 文件          # 每行替换第一个
sed 's/旧/新/g' 文件         # 全局替换
sed -i 's/旧/新/g' 文件      # 原地修改（GNU）
sed -i '' 's/旧/新/g' 文件   # 原地修改（macOS）

# 定位
sed -n '5p' 文件              # 第 5 行
sed -n '2,5p' 文件            # 2~5 行
sed -n '/正则/p' 文件         # 匹配行
sed -n '10,$p' 文件           # 第 10 行到末尾
sed '/开始/,/结束/p' 文件     # 两个正则之间的行

# 行操作
sed '3d' 文件                 # 删第 3 行
sed '/空/d' 文件              # 删匹配行
sed '1!d' 文件                # 只留第 1 行
sed '/^$/d' 文件              # 删空行
sed '3q' 文件                 # 处理到第 3 行退出

# 增改
sed '2a 新行' 文件            # 第 2 行后追加（GNU）
sed '2i 新行' 文件            # 第 2 行前插入（GNU）
sed '2c 整行' 文件            # 第 2 行整行替换
sed 'y/abc/ABC/' 文件         # 字符映射

# 高级
sed -E 's/(a)+/X/' 文件       # 扩展正则
sed -n 's/旧/新/p' 文件       # 只打印被改的行
sed -f 脚本.sed 文件          # 用脚本文件
```

## 小结 {#summary}

本章用 `-E` 扩展正则简化写法，厘清了 GNU 与 macOS sed 在 `-i`、追加/插入上的关键差异，并给出 CSV、日志聚合等综合案例与一份速查表。掌握本教程的内容，你已能应对绝大多数日常命令行文本处理任务；遇到更复杂的表格数据，可进一步了解 `awk` 与 `csvkit`。
