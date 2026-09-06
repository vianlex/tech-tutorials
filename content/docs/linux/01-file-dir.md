---
title: 第一章：文件与目录操作
linkTitle: 文件与目录操作
description: ls/cd/cp/mv/rm 等基础命令、权限管理 chmod/chown、软硬链接
weight: 181
---

# 文件与目录操作

Linux 一切皆文件，文件与目录操作是最高频的命令。这一章打好基础，后续 find、grep 都建立在这些概念之上。

## 一、目录导航与查看

```bash
pwd                    # 打印当前目录
ls                     # 列出当前目录内容
ls -l                  # 长格式（权限、大小、时间）
ls -la                 # 含隐藏文件（. 开头）
ls -lh                 # 人类可读的大小（K/M/G）
ls -lt                 # 按修改时间排序，最新的在前
cd /path               # 切换目录
cd -                   # 回到上一个目录
cd ~                   # 回到 home 目录
```

`ls -l` 输出解读：

```
-rw-r--r--  1 amias  staff  1234  Sep 6 08:00  file.txt
└┬┘└──┬──┘  └┬┘  └─┬─┘  └─┬─┘  └──┬──┘  └────┘  └──┬───┘
 │    │      │     │      │      │         │        文件名
 │    │      │     │      │      │       修改时间
 │    │      │     │      │     文件大小
 │    │      │     │     属组
 │    │      │    属主
 │    │    链接数
 │  权限（9 位）
 类型（-文件 d目录 l链接）
```

## 二、创建、复制、移动、删除

```bash
touch file.txt         # 创建空文件 / 更新时间戳
mkdir dir              # 创建目录
mkdir -p a/b/c         # 递归创建多级目录

cp src dest            # 复制文件
cp -r dir1 dir2        # 递归复制目录
cp -i src dest         # 覆盖前询问（防误删）

mv old new             # 移动 / 重命名
mv file dir/           # 移动到目录

rm file                # 删除文件
rm -r dir              # 递归删除目录
rm -f file             # 强制删除，不提示
rm -rf dir             # 强制递归删除（危险！）
```

> [!WARNING]
> `rm -rf` 极其危险，删除不可恢复，没有回收站。执行前务必确认路径，**绝不要**对 `/`、`~`、`/home` 等目录使用。

## 三、查看文件内容

```bash
cat file               # 一次性输出全部内容
less file              # 分页查看（上下翻页，q 退出，/ 搜索）
head -n 20 file        # 看前 20 行
tail -n 20 file        # 看后 20 行
tail -f file           # 实时跟踪文件增长（看日志常用）
wc -l file             # 统计行数
du -sh dir             # 统计目录大小
```

## 四、权限管理

### 权限模型

每个文件有三类权限，分别对应**属主（u）**、**属组（g）**、**其他人（o）**：

```bash
chmod 755 file         # rwxr-xr-x（属主读写执行，其他只读执行）
chmod 644 file         # rw-r--r--（属主读写，其他只读）
chmod u+x script.sh    # 给属主加执行权限
chmod -R 755 dir       # 递归修改目录权限
```

数字权限对照（r=4, w=2, x=1）：

| 数字 | 权限 | 含义 |
| --- | --- | --- |
| 7 | rwx | 读 + 写 + 执行 |
| 6 | rw- | 读 + 写 |
| 5 | r-x | 读 + 执行 |
| 4 | r-- | 只读 |

### 属主与属组

```bash
chown amias:staff file     # 修改属主和属组
chown -R amias:staff dir   # 递归修改
```

## 五、软链接与硬链接

```bash
# 软链接（符号链接）：类似 Windows 快捷方式，可跨文件系统，可指向目录
ln -s /target/path link_name

# 硬链接：同一 inode 的多个名字，删除一个不影响另一个
ln target hard_link
```

区别：

| | 软链接 | 硬链接 |
| --- | --- | --- |
| 本质 | 指向路径的指针 | 同一 inode 的别名 |
| 指向目录 | 可以 | 不可以 |
| 跨文件系统 | 可以 | 不可以 |
| 原文件删除后 | 链接失效 | 文件仍存在 |

## 六、管道与重定向

这是 Linux 组合命令的**灵魂**，find、grep 等命令靠它串联：

```bash
cmd > file      # 输出重定向到文件（覆盖）
cmd >> file     # 输出追加到文件
cmd 2> file     # 错误输出重定向
cmd 2>&1        # 错误合并到标准输出
cmd1 | cmd2     # 管道：cmd1 的输出作为 cmd2 的输入
```

```bash
# 实战：统计当前目录下文件数量
ls | wc -l

# 查找包含 error 的行并计数
grep "error" log.txt | wc -l

# 后台执行并把日志写文件
nohup ./app > app.log 2>&1 &
```

## 小结

- 高频命令：`ls -la`、`cd`、`cp -r`、`mv`、`rm -rf`（慎用）、`cat/less/tail -f`。
- 权限三类（u/g/o）+ 三种（r/w/x），数字 755/644 最常用。
- 软链接是路径指针、硬链接是 inode 别名，语义不同。
- 管道 `|` 和重定向 `>` 是组合命令、串联 find/grep 的基础。
