---
title: 第三章 结构体与错误处理
linkTitle: 结构体与错误
description: Go 结构体、指针、错误处理模式与 panic/recover
weight: 33
---

# 结构体与错误处理

## 结构体 {#structs}

```go
type User struct {
    ID       int
    Name     string
    Email    string
    Active   bool
}

// 创建实例
u1 := User{ID: 1, Name: "Alice", Email: "a@example.com", Active: true}
u2 := User{2, "Bob", "b@example.com", false} // 按位置（不推荐）
var u3 User // 零值
```

## 指针 {#pointers}

Go 的指针与 C 类似，但没有指针运算：

```go
x := 42
p := &x        // p 是指向 x 的指针
fmt.Println(*p) // 42，解引用

*p = 100       // 通过指针修改
fmt.Println(x) // 100

// 结构体指针的字段访问可省略 *
up := &User{ID: 1}
up.Name = "Alice" // 等价于 (*up).Name
```

## new 与 make {#new-make}

```go
// new：分配内存，返回指针，零值初始化
p := new(int)       // *int，指向 0

// make：只用于 slice、map、channel
s := make([]int, 0, 10)
m := make(map[string]int)
ch := make(chan int)
```

## 错误处理 {#error-handling}

Go 用**显式返回 error** 而非异常：

```go
func readFile(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("读取 %s 失败: %w", path, err)
    }
    return data, nil
}
```

> [!IMPORTANT]
> `%w` 用于包装错误，保留错误链，配合 `errors.Is` / `errors.As` 判断错误类型。

### 自定义错误 {#custom-error}

```go
type NotFoundError struct {
    Resource string
}

func (e NotFoundError) Error() string {
    return e.Resource + " 不存在"
}
```

## panic 与 recover {#panic-recover}

```go
// panic 用于不可恢复的错误，会中断程序
// recover 只能在 defer 中捕获 panic

func safeDivide(a, b int) (result int) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("捕获到 panic:", r)
            result = 0
        }
    }()
    return a / b // b 为 0 时会 panic
}
```

> [!WARNING]
> 不要用 panic 做常规错误处理，error 才是 Go 的惯用方式。panic 只用于真正的程序错误。

## 小结 {#summary}

Go 通过显式 error 返回值处理错误，代码清晰可追踪。下一章进入 Go 的招牌特性——并发编程。
