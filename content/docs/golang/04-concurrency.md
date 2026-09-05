---
title: 第四章 并发编程
linkTitle: 并发编程
description: goroutine、channel、select 与并发模式
weight: 34
---

# 并发编程

Go 的并发是它的招牌特性，基于 **goroutine** 和 **channel**，遵循「不要通过共享内存来通信，而要通过通信来共享内存」。

## goroutine {#goroutine}

goroutine 是 Go 的轻量级线程，用 `go` 关键字启动：

```go
func say(s string) {
    for i := 0; i < 3; i++ {
        fmt.Println(s)
        time.Sleep(100 * time.Millisecond)
    }
}

func main() {
    go say("world") // 并发执行
    say("hello")    // 主 goroutine
}
```

goroutine 由 Go 运行时调度，创建成本远低于系统线程。

## channel {#channel}

channel 是 goroutine 之间通信的管道：

```go
ch := make(chan int)     // 无缓冲 channel
ch := make(chan int, 10) // 有缓冲 channel

// 发送和接收
ch <- 42      // 发送
value := <-ch // 接收

// 示例
func sum(nums []int, ch chan int) {
    total := 0
    for _, n := range nums {
        total += n
    }
    ch <- total // 把结果发送到 channel
}

func main() {
    ch := make(chan int)
    go sum([]int{1, 2, 3}, ch)
    go sum([]int{4, 5, 6}, ch)
    x, y := <-ch, <-ch
    fmt.Println(x, y, x+y)
}
```

## 关闭 channel {#close}

```go
ch := make(chan int)
go func() {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    close(ch) // 关闭后不能再发送
}()

for v := range ch { // range 会循环接收直到关闭
    fmt.Println(v)
}
```

## select {#select}

`select` 让 goroutine 同时等待多个 channel：

```go
select {
case v := <-ch1:
    fmt.Println("从 ch1 收到", v)
case v := <-ch2:
    fmt.Println("从 ch2 收到", v)
case <-time.After(1 * time.Second):
    fmt.Println("超时")
default:
    fmt.Println("无数据可读")
}
```

## sync.WaitGroup {#waitgroup}

等待一组 goroutine 完成：

```go
var wg sync.WaitGroup

for i := 0; i < 5; i++ {
    wg.Add(1) // 计数 +1
    go func(n int) {
        defer wg.Done() // 完成时计数 -1
        fmt.Println(n)
    }(i)
}

wg.Wait() // 等待所有 goroutine 完成
fmt.Println("全部完成")
```

## 并发安全 {#safety}

```go
// 共享变量用互斥锁保护
var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}
```

> [!TIP]
> 优先用 channel 通信；确实需要共享可变状态时才用互斥锁。可用 `go run -race` 检测数据竞争。

## 小结 {#summary}

goroutine + channel 是 Go 并发的核心模型，`select` 和 `WaitGroup` 提供了强大的协调能力。下一章学习标准库与工程实践。
