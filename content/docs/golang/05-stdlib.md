---
title: 第五章 标准库与工程实践
linkTitle: 标准库与工程
description: Go 常用标准库、模块管理、测试与工具链
weight: 35
---

# 标准库与工程实践

## 常用标准库 {#stdlib}

```go
import (
    "fmt"      // 格式化输出
    "os"       // 操作系统接口
    "io"       // I/O 原语
    "strings"  // 字符串操作
    "strconv"  // 字符串转换
    "encoding/json" // JSON 处理
    "net/http" // HTTP 客户端和服务端
    "time"     // 时间处理
)
```

### JSON 处理 {#json}

```go
type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

// 序列化
data, _ := json.Marshal(User{ID: 1, Name: "Alice"})
// {"id":1,"name":"Alice"}

// 反序列化
var u User
json.Unmarshal(data, &u)
```

### HTTP 服务 {#http-server}

```go
func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s", r.URL.Path[1:])
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
```

## 模块管理 {#modules}

```bash
# 初始化模块
go mod init github.com/you/project

# 添加依赖
go get github.com/gin-gonic/gin

# 整理依赖
go mod tidy

# 查看依赖
go mod graph
```

`go.mod` 记录依赖，`go.sum` 记录校验和，两者都要提交。

## 测试 {#testing}

Go 内置测试框架，测试文件以 `_test.go` 结尾：

```go
// add_test.go
package main

import "testing"

func TestAdd(t *testing.T) {
    result := add(2, 3)
    if result != 5 {
        t.Errorf("期望 5，得到 %d", result)
    }
}

// 表格驱动测试
func TestDivide(t *testing.T) {
    cases := []struct {
        a, b, want int
    }{
        {10, 2, 5},
        {9, 3, 3},
        {8, 4, 2},
    }
    for _, c := range cases {
        if got, _ := divide(c.a, c.b); got != c.want {
            t.Errorf("divide(%d,%d) = %d, want %d", c.a, c.b, got, c.want)
        }
    }
}
```

运行测试：

```bash
go test            # 运行测试
go test -v         # 详细输出
go test -cover     # 覆盖率
go test -bench=.   # 基准测试
```

## 工具链 {#tools}

```bash
go build     # 编译
go run       # 编译并运行
go vet       # 静态检查
go fmt       # 格式化（gofmt）
go doc       # 查看文档
go install   # 安装到 $GOBIN
```

## 小结 {#summary}

Go 工具链完整且开箱即用，标准库覆盖大部分常见需求。至此 Go 教程完成，建议通过实际项目巩固。
