---
title: 第一章 环境搭建与基础语法
linkTitle: 基础语法
description: Go 安装、变量声明、基本类型、控制流
weight: 31
---

# 环境搭建与基础语法

## 安装 Go {#install}

从 [golang.org/dl](https://golang.org/dl/) 下载安装，验证：

```bash
go version
# go version go1.22.0 linux/amd64
```

## 第一个程序 {#hello-world}

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go!")
}
```

运行：

```bash
go run main.go
```

## 变量声明 {#variables}

```go
// 完整声明
var name string = "Alice"

// 类型推断
var age = 25

// 短变量声明（仅函数内）
count := 10

// 多变量
var x, y int = 1, 2
a, b := 3, 4
```

## 基本类型 {#types}

```go
bool            // true / false

string          // 字符串

int, int8, int16, int32, int64   // 有符号整数
uint, uint8, uint16, uint32, uint64 // 无符号整数
float32, float64                  // 浮点数
complex64, complex128             // 复数

byte   // uint8 别名
rune   // int32 别名，表示 Unicode 码点
```

## 常量与 iota {#constants}

```go
const Pi = 3.14159

// iota 用于枚举
const (
    Sunday = iota // 0
    Monday        // 1
    Tuesday       // 2
)
```

## 控制流 {#control-flow}

```go
// if（可带初始化语句）
if n := len(s); n > 0 {
    fmt.Println(n)
}

// for 是唯一的循环关键字
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// 类似 while
sum := 0
for sum < 100 {
    sum += 10
}

// switch（无需 break）
switch day {
case 1:
    fmt.Println("周一")
default:
    fmt.Println("其他")
}
```

## 小结 {#summary}

Go 语法简洁，`for` 是唯一循环，`:=` 短变量声明是常用习惯。下一章学习函数与接口。
