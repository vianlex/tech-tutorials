---
title: sed 使用教程
linkTitle: sed 教程
description: sed 流编辑器从基础替换到高级文本处理的实用教程
weight: 140
---

# sed 使用教程

sed（Stream Editor，流编辑器）是 Linux/Unix 下最强大的命令行文本处理工具之一，它逐行读取文本并按规则修改后输出，特别适合批量替换、删除、插入和提取等任务。本教程从最基础的 `s/旧/新/` 替换讲起，循序渐进到行定位、增删改，再到正则实战与综合案例，配合大量真实场景示例，让你真正用得上 sed。

## 章节 {.cards}

- [第一章：sed 基础与替换](/docs/sed/01-basics-substitute/) — 什么是 sed、基本语法、`-n`/`p`、`-i` 原地修改、全局替换与反向引用
- [第二章：行定位与删除](/docs/sed/02-line-address-delete/) — 行号/正则定位、范围匹配、`d` 删除、`!` 取反、删除空行与注释
- [第三章：插入、追加与修改](/docs/sed/03-insert-append-change/) — `a` 追加、`i` 插入、`c` 整行替换、`y` 字符转换、多命令与脚本文件
- [第四章：正则与实用场景](/docs/sed/04-regex-scenarios/) — sed 正则速览、实战批量替换、处理配置文件、提取日志字段
- [第五章：综合实战与注意事项](/docs/sed/05-advanced-caveats/) — 组合案例、CSV/日志处理、`-E` 扩展正则、GNU 与 macOS 差异与速查表
