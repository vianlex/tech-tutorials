---
title: awk 使用教程
linkTitle: awk 教程
description: awk 文本分析处理工具从字段切分到脚本化处理的实用教程
weight: 150
---

# awk 使用教程

awk 是一款强大的文本分析处理工具，擅长按列（字段）处理结构化文本、做统计汇总，常用于日志分析、数据清洗与报表生成。本教程以 GNU awk（gawk）5.x 为准，由浅入深，用大量真实场景示例带你从「提取某一列」一路学到「分组统计与实战脚本」。

## 章节 {.cards}

- [第一章：基础与字段](/docs/awk/01-basics-fields/) — awk 是什么、`模式 {动作}` 结构、字段 `$1/$0`、`-F` 分隔符与 `print`
- [第二章：模式与条件过滤](/docs/awk/02-patterns-filtering/) — `BEGIN`/`END`、比较与逻辑运算符、正则匹配 `/pattern/`
- [第三章：变量与内置变量](/docs/awk/03-variables-builtin/) — `NR`/`NF`/`FNR`/`FS`/`OFS`/`RS`，自定义变量与多文件处理
- [第四章：统计与计算](/docs/awk/04-statistics-calc/) — 求和、计数、平均值、最大最小值、`printf` 格式化与分组统计
- [第五章：函数、数组与实战](/docs/awk/05-functions-arrays/) — 内置函数、关联数组分组汇总、解析 CSV/日志与速查表
