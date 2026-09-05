---
title: 第二章 函数、方法与接口
linkTitle: 函数与接口
description: Go 函数、多返回值、方法、接口与类型断言
weight: 32
---

# 函数、方法与接口

## 函数 {#functions}

```go
func add(a, b int) int {
    return a + b
}
```

### 多返回值 {#multiple-returns}

Go 函数可以返回多个值，这是其特色：

```go
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("除数为零")
    }
    return a / b, nil
}

result, err := divide(10, 2)
if err != nil {
    // 处理错误
}
```

### 命名返回值 {#named-returns}

```go
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return // 裸返回
}
```

### 可变参数 {#variadic}

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3, 4) // 10
```

## 方法 {#methods}

方法是**带有接收者**的函数：

```go
type Rectangle struct {
    Width, Height float64
}

// 值接收者
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 指针接收者（可修改字段）
func (r *Rectangle) Scale(f float64) {
    r.Width *= f
    r.Height *= f
}
```

## 接口 {#interfaces}

接口定义行为契约，Go 的接口是**隐式实现**的：

```go
type Shape interface {
    Area() float64
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return 3.14 * c.Radius * c.Radius
}

// Circle 无需显式声明，只要实现 Area() 就满足 Shape
var s Shape = Circle{Radius: 5}
fmt.Println(s.Area())
```

> [!TIP]
> Go 的哲学是「小接口」，接口通常只包含一两个方法。隐式实现让代码解耦更自然。

## 类型断言与类型开关 {#assertion}

```go
// 类型断言
c, ok := s.(Circle)
if ok {
    fmt.Println("是 Circle，半径", c.Radius)
}

// 类型开关
switch v := s.(type) {
case Circle:
    fmt.Println("Circle", v.Radius)
case Rectangle:
    fmt.Println("Rectangle", v.Width)
default:
    fmt.Println("未知类型")
}
```

## 小结 {#summary}

多返回值、隐式接口和指针接收者是 Go 函数体系的精髓。下一章学习结构体与错误处理。
