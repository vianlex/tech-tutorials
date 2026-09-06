---
title: 第二章：find 文件查找
linkTitle: find 文件查找
description: 按名称/类型/大小/时间查找文件、执行动作、常用组合场景
weight: 183
---

# find 文件查找

`find` 是 Linux 最强大的文件查找工具，能按**名称、类型、大小、时间、权限**等多种条件精确定位文件，并支持对结果**执行动作**（删除、移动、执行命令）。

## 一、基本语法

```bash
find [路径] [条件] [动作]
```

- 路径：从哪里开始找，默认当前目录，会**递归**所有子目录。
- 条件：多个条件默认是「且（AND）」关系，可用 `-o`（或）、`-not`（非）组合。
- 动作：对匹配结果做什么，默认 `-print`（打印路径）。

```bash
find /home -name "*.log"        # 在 /home 下找 .log 文件
find . -type f                  # 找当前目录所有普通文件
```

## 二、按名称查找

```bash
find . -name "file.txt"         # 精确匹配（区分大小写）
find . -iname "FILE.txt"        # 忽略大小写
find . -name "*.jpg"            # 通配符：所有 jpg
find . -name "*.conf" -o -name "*.cfg"   # 匹配多个
```

> 通配符要加引号（`"*.jpg"`），否则会被 shell 先展开，导致 find 行为异常。

## 三、按类型查找

```bash
find . -type f    # 普通文件
find . -type d    # 目录
find . -type l    # 符号链接
find . -type f -name "*.go"   # 类型 + 名称组合
```

## 四、按大小查找

```bash
find . -size +100M       # 大于 100MB
find . -size -10k        # 小于 10KB
find . -size 0           # 空文件
find / -size +1G -type f # 查找大于 1G 的大文件（排查磁盘占用）
```

单位：`c`（字节）、`k`、`M`、`G`。`+` 表示大于，`-` 表示小于，无符号表示精确。

## 五、按时间查找

```bash
# 按修改时间（mtime：内容修改）
find . -mtime -7      # 7 天内修改过
find . -mtime +30     # 30 天前修改（找旧文件）
find . -mmin -60      # 60 分钟内修改过

# 按访问时间（atime）和状态变更时间（ctime）
find . -atime +30     # 30 天内未被访问
find . -cmin -10      # 10 分钟内权限/属性变更
```

时间语义（以 `-mtime +30` 为例）：

- `+30`：超过 30 天
- `-30`：30 天以内
- `30`：恰好 30 天

## 六、按权限与属主查找

```bash
find . -user amias            # 属主是 amias
find . -group staff           # 属组是 staff
find . -perm 755              # 权限精确为 755
find . -perm -u+w             # 属主有写权限
find . -empty                 # 空文件或空目录
```

## 七、对结果执行动作

`find` 的杀手锏是能对找到的文件**批量执行命令**。

### 1. -delete：直接删除

```bash
find . -name "*.tmp" -delete   # 删除所有 .tmp 文件
```

### 2. -exec：执行任意命令

```bash
# 删除 30 天前的日志
find /var/log -name "*.log" -mtime +30 -exec rm -f {} \;

# 把所有 .sh 设为可执行
find . -name "*.sh" -exec chmod +x {} \;

# 查找大文件并按大小列出（exec 多命令）
find / -size +500M -exec ls -lh {} \;
```

`{}` 是找到的文件占位符，`\;` 表示命令结束（`-exec` 必须带）。

### 3. -exec ... + 批量处理（性能更好）

```bash
# 用 + 结尾，一次把多个文件传给命令，减少进程开销
find . -name "*.tmp" -exec rm -f {} +
```

### 4. 配合 xargs

```bash
# xargs 把 find 结果转成参数传给命令，支持并行
find . -name "*.jpg" | xargs -I {} mv {} /backup/
find . -name "*.txt" -print0 | xargs -0 rm -f   # -print0 处理含空格文件名
```

## 八、常见实战场景

```bash
# 1. 清理磁盘：找最大的 10 个文件
find / -type f -size +100M -exec ls -lh {} + 2>/dev/null | sort -k5 -h | tail -10

# 2. 找出并删除所有空目录
find . -type d -empty -delete

# 3. 批量重命名（配合 mv）
find . -name "*.JPG" -exec bash -c 'mv "$0" "${0%.JPG}.jpg"' {} \;

# 4. 查找最近 1 小时内修改的文件
find . -mmin -60 -type f

# 5. 排除某个目录查找
find . -path "./node_modules" -prune -o -name "*.js" -print
```

## 小结

- `find [路径] [条件] [动作]`，默认递归、条件默认 AND。
- 按名称 `-name`/`-iname`、类型 `-type`、大小 `-size`、时间 `-mtime`/`-mmin`、权限 `-perm`、属主 `-user`。
- 动作：`-delete`、`-exec {} \;`、`-exec {} +`（批量）、`xargs`。
- 通配符要加引号；文件名含空格用 `-print0` + `xargs -0`。
