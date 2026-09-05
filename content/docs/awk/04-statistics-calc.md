---
title: 第四章 统计与计算
linkTitle: 统计与计算
description: 求和、计数、平均值、最大最小值、printf 与分组统计
weight: 154
---

# 统计与计算

本章把前面学的变量用起来，做最常见的数据统计：求和、计数、平均值、最大/最小值，以及用 `printf` 规范输出格式，并用数组做分组统计（数组详见第五章，这里先上手）。

## 求和 {#sum}

累加某一列最简单：`sum += $列号`，最后在 `END` 输出。

```bash
# 输入：每行一个数，求总和
echo -e "10\n20\n30\n40" | awk '{ sum += $1 } END { print "总和 =", sum }'
# 输出：
# 总和 = 100
```

按列求和（多列数据）：

```bash
# 输入：商品 销量 金额，求总销量与总金额
echo -e "A 3 30\nB 5 50\nC 2 20" | awk '{ s+=$2; m+=$3 } END { print "总销量=" s " 总金额=" m }'
# 输出：
# 总销量=10 总金额=100
```

## 计数 {#count}

用计数器统计行数或满足条件的行数：

```bash
# 统计总行数
echo -e "a\nb\nc" | awk 'END { print "共", NR, "行" }'
# 输出：
# 共 3 行
```

统计满足条件的行（例如分数及格人数）：

```bash
echo -e "88\n55\n92\n60" | awk '$1 >= 60 { pass++ } END { print "及格人数:", pass }'
# 输出：
# 及格人数: 3
```

## 平均值 {#average}

平均值 = 总和 / 个数。注意 awk 默认是浮点除法，结果带小数。

```bash
echo -e "80\n90\n70" | awk '{ sum+=$1; n++ } END { print "平均分 =", sum/n }'
# 输出：
# 平均分 = 80
```

保留两位小数的平均值（配合 `printf`，见下节）：

```bash
echo -e "80\n90\n73" | awk '{ sum+=$1; n++ } END { printf "平均分 = %.2f\n", sum/n }'
# 输出：
# 平均分 = 81.00
```

## 最大值与最小值 {#max-min}

用变量记录极值，遇到更大/更小的值就更新：

```bash
# 求最大值
echo -e "12\n45\n7\n99\n33" | awk 'NR==1 { max=$1 } $1>max { max=$1 } END { print "最大值 =", max }'
# 输出：
# 最大值 = 99
```

求最小值（初始设为很大的数，或直接用首行）：

```bash
echo -e "12\n45\n7\n99\n33" | awk 'NR==1 { min=$1 } $1<min { min=$1 } END { print "最小值 =", min }'
# 输出：
# 最小值 = 7
```

同时求最大、最小、平均：

```bash
echo -e "12\n45\n7\n99\n33" | awk '
NR==1 { max=min=$1 }
{ sum+=$1; n++; if($1>max)max=$1; if($1<min)min=$1 }
END { printf "最大=%d 最小=%d 平均=%.1f\n", max, min, sum/n }'
# 输出：
# 最大=99 最小=7 平均=39.2
```

## printf 格式化输出 {#printf}

`printf "格式串", 参数1, 参数2` 不自动换行，需手动加 `\n`。常用占位符：

- `%d` 整数、`%f` 浮点、`%.2f` 保留两位、`%s` 字符串、`%10s` 右对齐占 10 宽。

```bash
echo -e "苹果 5\n香蕉 3" | awk '{ printf "%-6s 数量:%3d\n", $1, $2 }'
# 输出（第1列左对齐占6宽，数字占3宽）：
# 苹果   数量:  5
# 香蕉   数量:  3
```

对齐排版成表格：

```bash
echo -e "name score\nTom 92\nLucy 88" | awk '
NR==1 { printf "%-8s %5s\n", $1, $2; next }
{ printf "%-8s %5d\n", $1, $2 }'
# 输出：
# name        score
# Tom           92
# Lucy          88
```

## 分组统计（用数组） {#group-by}

awk 的数组是「关联数组」（键可以是字符串）。按某列分组累加，是日志统计的杀手锏。

```bash
# 输入：城市 销售额，按城市求和
echo -e "北京 100\n上海 80\n北京 50\n上海 120" | awk '{ city[$1]+=$2 } END { for (c in city) print c, city[c] }'
# 输出（顺序可能不同）：
# 北京 150
# 上海 200
```

统计每个 IP 的访问次数：

```bash
echo -e "10.0.0.1\n10.0.0.2\n10.0.0.1\n10.0.0.1" | awk '{ ip[$1]++ } END { for (k in ip) print k, ip[k] }'
# 输出：
# 10.0.0.1 3
# 10.0.0.2 1
```

## 常用例子 {#examples}

**例 1：日志 QPS 统计（按分钟汇总请求数）**

```bash
# 输入：每行是 时间(到分钟) 请求数
echo -e "10:01 3\n10:01 5\n10:02 4\n10:02 2" | awk '{ qps[$1]+=$2 } END { for (t in qps) print t " 共 " qps[t] " 次" }'
# 输出：
# 10:01 共 8 次
# 10:02 共 6 次
```

**例 2：按列求和并算占比**

```bash
echo -e "A 30\nB 20\nC 50" | awk '
{ v[$1]=$2; total+=$2 }
END { for (k in v) printf "%s: %d (%.0f%%)\n", k, v[k], v[k]/total*100 }'
# 输出：
# A: 30 (30%)
# B: 20 (20%)
# C: 50 (50%)
```

**例 3：求某列最大值对应的整行**

```bash
echo -e "web 82\ndb 45\ncache 91" | awk '
$2>max { max=$2; line=$0 }
END { print "最高:", line }'
# 输出：
# 最高: cache 91
```

**例 4：统计空行数量**

```bash
echo -e "a\n\nb\n\nc" | awk 'NF==0 { blank++ } END { print "空行数:", blank+0 }'
# 输出：
# 空行数: 2
```

## 小结 {#summary}

本章能完成求和、计数、平均、极值、分组统计，并用 `printf` 输出整齐的报表。下一章将补充内置函数（字符串处理等）、关联数组进阶用法，并通过解析 CSV/日志、配合 `sort` 排序等实战，把 awk 真正用到生产场景，最后附一份速查表。
