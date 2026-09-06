---
title: 第六章 标准库与工程实践
linkTitle: 标准库与工程
description: io.Reader/Writer 哲学、fmt/strings/time、encoding/json 进阶与 Go 1.27 JSON v2 变更、net/http 服务与中间件、os/filepath、slices/maps、测试进阶与 fuzz、模块管理与交叉编译
weight: 36
---

# 标准库与工程实践

Go 的标准库以" batteries included "著称，覆盖网络、加解密、编解码、并发等绝大多数场景。**优先用标准库**是 Go 社区的共识。

## io：Reader / Writer 哲学 {#io}

Go 的 I/O 抽象极其优雅：**只要实现了 `Read` 就是数据源，实现了 `Write` 就是数据目标**，文件、网络、内存、压缩流可以任意组合。

```go
type Reader interface {
    Read(p []byte) (n int, err error)     // 读入 p，返回读取字节数
}
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

### 组合的力量 {#io-compose}

```go
// 文件 → gzip 压缩 → 加密 → 写入网络：像搭积木一样组合
file, _ := os.Open("data.txt")
defer file.Close()

gz := gzip.NewWriter(conn)        // conn 是 net.Conn，实现了 io.Writer
defer gz.Close()

_, err := io.Copy(gz, file)       // 一行搞定：从 file 拷贝数据到 gz（自动压缩后写入 conn）
```

### 常用 io 工具 {#io-utils}

```go
io.Copy(dst, src)                    // 拷贝（内部用 32KB 缓冲）
io.CopyBuffer(dst, src, buf)         // 自定义缓冲
io.CopyN(dst, src, 1024)             // 只拷贝 N 字节
io.ReadAll(r)                        // 全部读入内存（注意大文件会 OOM）
io.ReadFull(r, buf)                  // 读满 buf 或出错
io.MultiWriter(w1, w2, w3)           // 同时写多个目标（如同时写文件和日志）
io.TeeReader(r, w)                   // 读的同时旁路写入 w（如记录请求体）
io.LimitReader(r, 1<<20)             // 限制最多读 1MB（防止恶意大文件）
io.Pipe()                            // 内存管道，连接 Reader 和 Writer

// 包装进度
type ProgressReader struct {
    io.Reader
    total int64
}
func (pr *ProgressReader) Read(p []byte) (int, error) {
    n, err := pr.Reader.Read(p)
    pr.total += int64(n)
    fmt.Printf("\r已读取 %d 字节", pr.total)
    return n, err
}
```

> [!TIP]
> **`Read` 的语义必须正确**：`n > 0` 时**可能同时返回 `err != nil`**（如 `io.EOF`）。判断是否读完要看 `n`，不能只看 err。
> ```go
> for {
>     n, err := r.Read(buf)
>     if n > 0 {
>         process(buf[:n])       // 先处理读到的数据
>     }
>     if err == io.EOF {
>         break                  // 再判断结束
>     }
>     if err != nil {
>         return err
>     }
> }
> ```

### bufio：缓冲 I/O {#bufio}

```go
// 逐行读取大文件（不要 ReadAll！）
f, _ := os.Open("huge.log")
defer f.Close()
scanner := bufio.NewScanner(f)
scanner.Buffer(make([]byte, 1024*1024), 1024*1024)   // 调大单行上限（默认 64KB）
for scanner.Scan() {
    line := scanner.Text()
    // 处理
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}

// 缓冲写入
w := bufio.NewWriter(file)
w.WriteString("...")
w.Flush()            // ⚠️ 必须 Flush，否则数据还在缓冲区
```

> [!WARNING]
> `bufio.Scanner` 默认单行上限 **64KB**，超长行会报 `token too long`。处理日志或 JSON Lines 时记得调 `Buffer`。

## fmt 格式化 {#fmt}

```go
fmt.Println(a, b)                 // 自动空格 + 换行
fmt.Printf("%s\n", s)
fmt.Sprintf("%d-%s", 1, "a")      // 返回字符串
fmt.Fprintf(w, "%d", n)           // 写入 io.Writer
fmt.Errorf("失败: %w", err)        // 构造 error（%w 包装）

// 常用动词
%v    默认格式
%+v   struct 带字段名
%#v   Go 语法表示（含类型名）
%T    类型
%d    十进制    %x 十六进制    %b 二进制    %o 八进制
%f    浮点      %.2f 两位小数
%s    字符串    %q 带引号字符串
%p    指针地址
%t    布尔
%c    字符（rune）
```

> [!TIP]
> 调试结构体用 `%+v`（带字段名）或 `%#v`（带类型）。生产日志建议用结构化日志库（如 `log/slog`，Go 1.21+ 标准库内置）而非 `fmt`。

## time 时间处理 {#time}

### 参考时间（最重要的一课） {#reference-time}

Go 不用 `yyyy-MM-dd` 格式化，而用一个**固定的参考时间**作为模板：

```go
// 参考时间：2006-01-02 15:04:05.000000000 -0700 MST
// 记忆口诀：1月2日3点4分5秒6年7时区

t := time.Now()
t.Format("2006-01-02 15:04:05")     // 2026-09-06 10:30:45
t.Format("2006/01/02")              // 2026/09/06
t.Format("15:04")                   // 10:30
t.Format(time.RFC3339)              // 2026-09-06T10:30:45+08:00
t.Format(time.DateTime)             // Go 1.20+ 内置常量："2006-01-02 15:04:05"

// 解析（布局字符串同样用参考时间）
t, err := time.Parse("2006-01-02", "2026-09-06")
t, err := time.ParseInLocation("2006-01-02 15:04:05", "2026-09-06 10:30:45", time.Local)
```

> [!WARNING]
> `time.Parse` 得到的是 **UTC 时间**；解析本地时间字符串要用 `time.ParseInLocation(..., time.Local)`，否则会差 8 小时。

### 时间点与时长 {#time-ops}

```go
now := time.Now()
d := 3 * time.Second          // Duration（int64 纳秒）
later := now.Add(d)
later = now.Add(24 * time.Hour)
later.AddDate(0, 1, 0)        // 加 1 个月

diff := later.Sub(now)        // Duration
diff.Hours() / diff.Minutes() / diff.Seconds() / diff.Milliseconds()
diff.String()                 // "3s"

now.Before(later)             // true
now.After(later)              // false
now.Equal(later)              // 比较时间点（会考虑时区）

now.Unix()                    // 秒级时间戳
now.UnixMilli()               // 毫秒（Go 1.17+）
now.UnixNano()                // 纳秒
time.Unix(1700000000, 0)      // 时间戳转 time.Time
```

### Timer 与 Ticker {#timer-ticker}

```go
// Timer：一次性
timer := time.NewTimer(3 * time.Second)
<-timer.C                      // 阻塞等待
timer.Stop()                   // 停止（未触发时）
timer.Reset(5 * time.Second)   // 重置

time.After(3 * time.Second)    // 语法糖，返回 <-chan Time（循环内慎用，见第四章）

// Ticker：周期性
ticker := time.NewTicker(1 * time.Second)
defer ticker.Stop()            // ⚠️ 必须 Stop，否则泄漏
for {
    select {
    case t := <-ticker.C:
        fmt.Println("tick at", t)
    case <-ctx.Done():
        return
    }
}
```

### 时区 {#timezone}

```go
loc, err := time.LoadLocation("Asia/Shanghai")
t := time.Now().In(loc)
t.Format(time.RFC3339)        // 2026-09-06T10:30:45+08:00

// 容器环境如果缺少 tzdata，LoadLocation 会失败
// 解决：import _ "time/tzdata"（把时区数据编进二进制，增加约 450KB）
```

## encoding/json {#json}

### 基础 {#json-basic}

```go
type User struct {
    ID       int       `json:"id"`
    Name     string    `json:"name"`
    Email    string    `json:"email,omitempty"`   // 空值时省略
    Password string    `json:"-"`                 // 完全忽略
    Age      int       `json:"age,string"`        // 序列化成字符串
}

// 序列化
data, err := json.Marshal(user)                   // []byte
data, err := json.MarshalIndent(user, "", "  ")   // 带缩进（调试用）

// 反序列化
var u User
err := json.Unmarshal(data, &u)                   // 注意必须传指针

// 流式（处理大文件或网络流）
enc := json.NewEncoder(w)      // 直接写 io.Writer
enc.SetIndent("", "  ")
enc.Encode(user)

dec := json.NewDecoder(r)      // 从 io.Reader 读
dec.Decode(&u)
dec.DisallowUnknownFields()    // 严格模式：未知字段报错
```

### 常见 tag 选项 {#json-tags}

| tag | 效果 |
|-----|------|
| `json:"name"` | 字段重命名 |
| `json:"-"` | 忽略该字段 |
| `json:"name,omitempty"` | 值为零值时省略 |
| `json:"name,string"` | 数值/布尔序列化为字符串 |
| `json:",omitempty"` | 只省略，不重命名 |

**`omitempty` 的坑**：它按**零值**判断，`0`、`false`、`""` 都会被省略。想区分"未设置"和"设置为 0"，用**指针**：

```go
type UpdateReq struct {
    Age  *int    `json:"age,omitempty"`     // nil 省略，指向 0 的指针会输出 0
    Name *string `json:"name,omitempty"`
}
```

### 自定义序列化 {#json-custom}

实现 `Marshaler` / `Unmarshaler` 接口：

```go
type Money int64    // 单位：分

func (m Money) MarshalJSON() ([]byte, error) {
    return []byte(fmt.Sprintf(`"%.2f"`, float64(m)/100)), nil
}

func (m *Money) UnmarshalJSON(data []byte) error {
    s := strings.Trim(string(data), `"`)
    f, err := strconv.ParseFloat(s, 64)
    if err != nil {
        return err
    }
    *m = Money(f * 100)
    return nil
}

// 常用于：自定义时间格式、枚举、敏感数据脱敏
```

**自定义时间格式**（高频需求）：

```go
type MyTime time.Time

func (t MyTime) MarshalJSON() ([]byte, error) {
    return []byte(`"` + time.Time(t).Format("2006-01-02 15:04:05") + `"`), nil
}
```

### 动态 JSON {#json-dynamic}

```go
// 结构未知 → map
var m map[string]any
json.Unmarshal(data, &m)

// 部分动态：用 json.RawMessage 延迟解析
type Event struct {
    Type    string          `json:"type"`
    Payload json.RawMessage `json:"payload"`    // 先不解析
}
var e Event
json.Unmarshal(data, &e)
switch e.Type {
case "user":
    var u User
    json.Unmarshal(e.Payload, &u)      // 按需解析
}
```

### ⚠️ Go 1.27 的 JSON v2 变更（必读） {#json-v2}

**Go 1.27（2026-08 发布）把 `encoding/json` 的底层引擎换成了 v2 实现**，`import "encoding/json"` 不用改，但**默认行为有破坏性变更**：

| 行为 | v1（旧） | v2（Go 1.27 默认） |
|------|---------|-------------------|
| nil slice / map 序列化 | `null` | **`[]` / `{}`** |
| 字段匹配 | 大小写不敏感 | **区分大小写** |
| 重复 key | 静默取最后一个 | **报错** |
| 无效 UTF-8 | 静默接受 | **拒绝** |
| 无效的 struct tag | 静默忽略 | **运行时报错** |

```go
type Response struct {
    Items []string `json:"items"`
}

// Go 1.26: {"items":null}
// Go 1.27: {"items":[]}      ← API 契约变了！前端要能处理
```

> [!WARNING]
> **如果你的服务是对外提供 JSON API，升级 Go 1.27 前必须检查**：
> 1. 是否有消费者依赖 `null` 与 `[]` 的区别
> 2. 是否依赖大小写不敏感匹配（如 JSON 里 `Name` 对应结构体 `name`）
> 3. 是否可能收到重复 key 的 JSON
>
> **临时回退**：构建时设 `GOEXPERIMENT=nojsonv2`（或 `GODEBUG=nojsonv2=1`）。注意该开关是临时的，未来版本会移除。

**v2 的新能力**（显式导入 `encoding/json/v2` 可用）：

```go
import "encoding/json/v2"

b, err := json.Marshal(v,
    json.Deterministic(true),          // map 输出顺序稳定
    json.OmitZeroStructFields(true),   // 零值结构体也省略
)

err = json.Unmarshal(data, &v,
    json.RejectUnknownMembers(true),   // 严格模式：未知字段直接报错（推荐用于 API 入参）
)

// 流式：jsontext 包提供 Token/Value 级别处理
```

`RejectUnknownMembers(true)` 特别推荐用于 API 边界——v1 默认"静默丢弃未知字段"，客户端拼错字段名会变成静默的零值，极难排查。

## net/http {#http}

### 服务端 {#http-server}

```go
func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s", r.URL.Path[1:])
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)     // 用默认 ServeMux
}
```

**生产环境必须设置超时**（默认的 `http.Server` 没有超时，会被慢连接拖垮）：

```go
srv := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,     // 读请求（含 body）超时
    WriteTimeout: 10 * time.Second,    // 写响应超时
    IdleTimeout:  120 * time.Second,   // keep-alive 空闲超时
    ReadHeaderTimeout: 2 * time.Second,
}
log.Fatal(srv.ListenAndServe())
```

### ServeMux 增强路由（Go 1.22+） {#servemux}

Go 1.22 起，标准库的 `ServeMux` 支持**方法匹配**和**路径通配符**，不再需要第三方路由：

```go
mux := http.NewServeMux()

// 方法 + 路径
mux.HandleFunc("GET /users", listUsers)
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("GET /users/{id}", getUser)          // {id} 通配符
mux.HandleFunc("DELETE /users/{id}", deleteUser)
mux.HandleFunc("GET /files/{path...}", serveFile)   // {path...} 匹配剩余全部

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")        // Go 1.22+ 获取路径参数
    // ...
}

// 未匹配的方法会返回 405 Method Not Allowed
```

### 中间件链 {#middleware}

中间件是 Go HTTP 的核心模式（回顾第三章的 panic recover）：

```go
type Middleware func(http.Handler) http.Handler

// 串起多个中间件
func Chain(h http.Handler, mws ...Middleware) http.Handler {
    for i := len(mws) - 1; i >= 0; i-- {   // 倒序包裹
        h = mws[i](h)
    }
    return h
}

// 日志中间件
func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

// 使用
handler := Chain(mux, RecoveryMiddleware, Logger, CORSMiddleware)
http.ListenAndServe(":8080", handler)
```

### 客户端（必配超时） {#http-client}

```go
// ❌ 错误：http.DefaultClient 没有超时，会永久挂起
resp, err := http.Get(url)

// ✅ 正确：自定义 Client 并设置超时
client := &http.Client{
    Timeout: 10 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

// 带 context 的请求（推荐：可取消、可超时）
req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
req.Header.Set("Authorization", "Bearer "+token)
resp, err := client.Do(req)
if err != nil {
    return err
}
defer resp.Body.Close()        // ⚠️ 必须关闭，否则连接不复用、文件描述符泄漏

// 读取响应（限制大小，防止恶意响应）
body, err := io.ReadAll(io.LimitReader(resp.Body, 10<<20))   // 最多 10MB
```

> [!IMPORTANT]
> **`defer resp.Body.Close()` 两个必做动作**：
> 1. 读取 body（即使不用）
> 2. 关闭 body
>
> 否则 TCP 连接不会归还连接池，最终耗尽文件描述符。这是 Go HTTP 客户端最常见的资源泄漏。

### 发送 JSON {#http-json}

```go
// 发送
payload := map[string]any{"name": "Alice"}
body, _ := json.Marshal(payload)
req, _ := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
req.Header.Set("Content-Type", "application/json")
resp, err := client.Do(req)

// 接收
var result User
json.NewDecoder(resp.Body).Decode(&result)     // 流式解码，比 ReadAll + Unmarshal 省内存
```

## os / filepath / exec {#os}

```go
// 文件读写
data, err := os.ReadFile("a.txt")                    // 一次性读（小文件）
err = os.WriteFile("b.txt", data, 0644)              // 一次性写
f, err := os.OpenFile("c.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)

// 文件信息
info, err := os.Stat("a.txt")
info.Size() / info.Mode() / info.ModTime() / info.IsDir()

// 目录操作
os.MkdirAll("a/b/c", 0755)
os.RemoveAll("tmp")
os.ReadDir(".")                                      // Go 1.16+

// 环境变量
os.Getenv("PORT")
os.Setenv("PORT", "8080")
os.LookupEnv("PORT")        // value, ok

// 路径处理
filepath.Join("a", "b", "c")        // a/b/c（自动处理分隔符）
filepath.Base("/a/b/c.txt")         // c.txt
filepath.Ext("c.txt")               // .txt
filepath.Dir("/a/b/c.txt")          // /a/b
filepath.Abs("a.txt")               // 绝对路径
filepath.WalkDir(root, fn)          // 遍历目录树
os.UserHomeDir()                    // 家目录
```

> [!TIP]
> 路径操作用 `path/filepath`（处理 OS 分隔符），URL 路径用 `path`。两者在 Windows 上行为不同，别混用。

```go
// 执行外部命令
cmd := exec.CommandContext(ctx, "ls", "-l", "/tmp")
out, err := cmd.Output()             // 只取 stdout
out, err := cmd.CombinedOutput()     // stdout + stderr

// 实时输出
cmd := exec.Command("tail", "-f", "app.log")
stdout, _ := cmd.StdoutPipe()
cmd.Start()
scanner := bufio.NewScanner(stdout)
for scanner.Scan() {
    fmt.Println(scanner.Text())
}
cmd.Wait()
```

## slices 与 maps（Go 1.21+） {#slices-maps}

标准库终于提供了泛型集合操作，替代大量手写循环：

```go
import (
    "slices"
    "maps"
)

// 排序
slices.Sort([]int{3, 1, 2})
slices.SortFunc(users, func(a, b User) int {
    return cmp.Compare(a.Age, b.Age)         // 需要 import "cmp"
})
slices.SortStableFunc(...)                   // 稳定排序

// 查找
idx := slices.Index(s, 42)                   // 位置，不存在返回 -1
has := slices.Contains(s, 42)
slices.ContainsFunc(s, func(v int) bool { return v > 10 })

// 其他
slices.Clone(s)                              // 浅拷贝
slices.Equal(s1, s2)
slices.Reverse(s)
slices.Delete(s, 1, 3)                       // 删除 [1,3)
slices.Compact(s)                            // 去除相邻重复（需先排序）

// map 操作
maps.Keys(m)         // Go 1.23+ 返回迭代器
maps.Values(m)
maps.Clone(m)
maps.Equal(m1, m2)
maps.Copy(dst, src)

// 遍历排序后的 key
for _, k := range slices.Sorted(maps.Keys(m)) {
    fmt.Println(k, m[k])
}
```

老项目仍在用 `sort` 包：

```go
sort.Ints(s)
sort.Strings(s)
sort.Slice(users, func(i, j int) bool {
    return users[i].Age < users[j].Age
})
```

> [!TIP]
> 新代码优先用 `slices`，它类型安全（编译期检查）且性能略好（`sort.Slice` 依赖反射）。

## 测试 {#testing}

Go 内置测试框架，**测试文件以 `_test.go` 结尾**，与源码同包。

### 表驱动测试（Go 的招牌风格） {#table-driven}

```go
func TestDivide(t *testing.T) {
    cases := []struct {
        name    string
        a, b    int
        want    int
        wantErr bool
    }{
        {"正常除法", 10, 2, 5, false},
        {"除数为零", 10, 0, 0, true},
        {"负数", -10, 2, -5, false},
    }
    
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {      // 子测试，每个用例独立报告
            got, err := divide(tc.a, tc.b)
            if (err != nil) != tc.wantErr {
                t.Fatalf("divide(%d,%d) err=%v, wantErr=%v", tc.a, tc.b, err, tc.wantErr)
            }
            if got != tc.want {
                t.Errorf("divide(%d,%d) = %d, want %d", tc.a, tc.b, got, tc.want)
            }
        })
    }
}
```

运行：

```bash
go test ./...                          # 跑所有包
go test -v ./...                       # 详细输出
go test -run TestDivide ./...          # 只跑匹配的测试
go test -run 'TestDivide/除数为零' -v   # 只跑某个子测试
go test -race ./...                    # 竞态检测
go test -cover ./...                   # 覆盖率
go test -coverprofile=cover.out . && go tool cover -html=cover.out   # 生成 HTML 报告
go test -count=1 ./...                 # 禁用缓存（结果被缓存时用它强制重跑）
```

### t.Errorf vs t.Fatalf {#error-vs-fatal}

| | 行为 |
|---|---|
| `t.Errorf` | 记录错误，**继续执行**当前测试 |
| `t.Fatalf` | 记录错误，**立即终止**当前测试（相当于 `return`） |
| `t.Log` / `t.Logf` | 记录信息，`-v` 时显示 |
| `t.Skip` | 跳过测试 |

> [!TIP]
> 判断"前置条件失败导致后续无意义"时用 `Fatal`（如初始化失败），否则用 `Error`（可以一次看到多个失败点）。**子测试里用 `Fatal` 只会终止该子测试**，不影响其他用例。

### 测试辅助与并行 {#test-helper}

```go
// 标记为辅助函数：报错时指向调用方行号，而非辅助函数内部
func assertEqual[T comparable](t *testing.T, got, want T) {
    t.Helper()
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}

// 并行测试（相互独立的用例可以并行加速）
func TestParallel(t *testing.T) {
    for _, tc := range cases {
        tc := tc                        // Go 1.22 前必须创建副本
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()                // 声明并行
            // ...
        })
    }
}
```

### TestMain（全局 setup/teardown） {#testmain}

```go
func TestMain(m *testing.M) {
    // 所有测试前：启动数据库容器、加载配置等
    setup()
    
    code := m.Run()        // 运行所有测试
    
    teardown()             // 所有测试后：清理
    os.Exit(code)          // 必须 os.Exit，且必须用 m.Run() 的返回值
}
```

### HTTP 测试 {#http-test}

标准库 `net/http/httptest` 无需启动真实端口：

```go
func TestHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users/123", nil)
    rec := httptest.NewRecorder()          // 捕获响应
    
    handler(rec, req)
    
    if rec.Code != http.StatusOK {
        t.Errorf("status = %d, want 200", rec.Code)
    }
    // 解析响应体
    var u User
    json.Unmarshal(rec.Body.Bytes(), &u)
}

// 测试整个 Server
func TestServer(t *testing.T) {
    srv := httptest.NewServer(mux)        // 启动临时服务器
    defer srv.Close()
    
    resp, err := http.Get(srv.URL + "/users")
    // ...
}
```

### 基准测试 {#benchmark}

```go
func BenchmarkConcat(b *testing.B) {
    // 耗时准备不计入
    data := prepareData()
    
    b.ResetTimer()                  // 重置计时器
    for i := 0; i < b.N; i++ {      // b.N 由框架自动调整
        _ = concat(data)
    }
}

// 对比不同实现
func BenchmarkConcatBuilder(b *testing.B) { /* strings.Builder 版本 */ }
```

```bash
go test -bench=. -benchmem          # -benchmem 显示内存分配
go test -bench=. -benchtime=10s     # 延长测试时间，结果更稳
go test -bench=BenchmarkConcat -count=5    # 跑 5 轮对比
```

输出解读：

```
BenchmarkConcat-8     5000    245678 ns/op    1048567 B/op    12 allocs/op
                       ↑        ↑每次耗时      ↑每次分配内存   ↑分配次数
```

**优化目标**：降低 `B/op`（减少分配）和 `allocs/op`（减少分配次数），通常比降低 ns/op 更关键。

### pprof 性能分析 {#pprof}

```go
import _ "net/http/pprof"       // 注册到默认 ServeMux

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
# CPU 分析
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
# 内存
go tool pprof http://localhost:6060/debug/pprof/heap
# goroutine（查泄漏）
go tool pprof http://localhost:6060/debug/pprof/goroutine
# 交互式命令
(pprof) top        # 最耗时的函数
(pprof) list func  # 查看函数逐行耗时
(pprof) web        # 生成火焰图（需 graphviz）
```

### Fuzz 测试（Go 1.18+） {#fuzz}

模糊测试：自动生成随机输入，寻找崩溃或边界问题。

```go
func FuzzParseURL(f *testing.F) {
    // 种子语料（从这些输入开始变异）
    f.Add("https://example.com")
    f.Add("http://a.b/c?d=1")
    
    f.Fuzz(func(t *testing.T, input string) {
        u, err := parseURL(input)
        if err != nil {
            return             // 解析失败是合法结果
        }
        // 断言不变量：解析出来的 URL 再格式化后应保持一致
        if u.String() == "" {
            t.Errorf("empty result for %q", input)
        }
    })
}
```

```bash
go test -fuzz=FuzzParseURL        # 持续运行直到发现问题或手动停止
go test -fuzz=FuzzParseURL -fuzztime=30s
```

发现失败时，Go 会把触发输入保存到 `testdata/fuzz/<FuzzName>/`，并自动成为回归测试用例。

### Mock 与依赖注入 {#mock}

Go 的 mock 风格：**定义接口 → 生产实现 → 测试实现**（通常不用 mock 框架）：

```go
// 1. 定义接口（在使用方定义）
type UserStore interface {
    Get(ctx context.Context, id int64) (*User, error)
}

// 2. 生产实现
type DBUserStore struct{ db *sql.DB }
func (s *DBUserStore) Get(ctx context.Context, id int64) (*User, error) { /* 真实查询 */ }

// 3. 测试实现（手写 stub，比 mock 框架更直观）
type fakeUserStore struct {
    users map[int64]*User
    err   error
}
func (f *fakeUserStore) Get(ctx context.Context, id int64) (*User, error) {
    if f.err != nil {
        return nil, f.err
    }
    return f.users[id], nil
}

// 4. 测试时注入
func TestGetUser(t *testing.T) {
    svc := &UserService{store: &fakeUserStore{
        users: map[int64]*User{1: {ID: 1, Name: "Alice"}},
    }}
    u, err := svc.GetUser(context.Background(), 1)
    // ...
}
```

需要复杂 mock 时可用 `github.com/golang/mock`（gomock）或 `github.com/vektra/mockery` 生成。

## 模块管理 {#modules}

### 常用命令 {#mod-commands}

```bash
go mod init github.com/you/project     # 初始化
go get github.com/gin-gonic/gin        # 添加依赖（默认最新版）
go get github.com/gin-gonic/gin@v1.9.1 # 指定版本
go get github.com/gin-gonic/gin@latest
go get -u ./...                        # 升级所有依赖（谨慎）
go mod tidy                            # 整理：添加缺失的、删除多余的（提交前必跑）
go mod download                        # 下载依赖到缓存
go mod verify                          # 校验依赖哈希
go mod graph                           # 查看依赖图
go list -m all                         # 列出所有依赖
go list -m -u all                      # 列出可升级的依赖
go mod why -m <module>                 # 为什么依赖这个模块
```

### go.mod 结构 {#gomod}

```go
module github.com/you/project

go 1.27                       // 语言版本（影响语言特性和语义，如循环变量语义）

require (
    github.com/gin-gonic/gin v1.9.1
    gopkg.in/yaml.v3 v3.0.1
)

require (...indirect...)      // 间接依赖

// replace：替换依赖（本地调试、fork 修复）
replace github.com/foo/bar => github.com/you/bar v1.2.3
replace github.com/foo/bar => ../local/bar          // 指向本地目录

// exclude：排除有问题的版本
exclude github.com/foo/bar v1.0.0

// retract：声明自己的某些版本有问题（作为被依赖方时）
retract v1.0.0
```

> [!IMPORTANT]
> `go.mod` 和 `go.sum` **都必须提交**。CI 里用 `go mod tidy` + `git diff --exit-code` 检查是否有未整理的依赖。

### replace 的典型场景 {#replace-usage}

```bash
# 1. 本地调试依赖库（改了依赖看效果，不用先发布）
go mod edit -replace github.com/foo/bar=../bar

# 2. 用 fork 修复上游 bug
go mod edit -replace github.com/buggy/lib=github.com/you/lib@fix-branch

# 3. 解决无法访问的内网依赖
go mod edit -replace example.com/internal=git.company.com/internal@v1.0.0
```

**注意**：`replace` 只在**当前模块（main module）**生效——你的库被别人依赖时，你的 replace 指令会被忽略。所以不要在上游修复前把它当长期方案。

### Go Workspace（多模块开发） {#go-work}

同时开发多个相互依赖的模块时（如主项目 + 私有库），用 workspace 代替一堆 replace：

```bash
go work init ./app ./lib          # 初始化
go work use ./another             # 添加模块
go work sync                      # 同步
```

生成 `go.work`：

```go
go 1.27

use (
    ./app
    ./lib
)
```

> [!TIP]
> `go.work` 是**本地开发用**的，通常加入 `.gitignore`（团队各自配置），不提交。

### 私有仓库 {#private-repo}

```bash
# 跳过校验和数据库和代理，直接走 git
go env -w GOPRIVATE=git.company.com,github.com/you/private

# 或更精细
go env -w GONOSUMDB=git.company.com
go env -w GONOSUMCHECK=1
```

## 构建与交叉编译 {#build}

```bash
# 基本
go build -o app .
go build -ldflags="-s -w" -o app .       # 去除符号表和调试信息，减小体积（约 30%）
go build -trimpath -o app .              # 去除本地路径信息（可复现构建）

# 交叉编译（Go 的强项，无需额外工具链）
GOOS=linux   GOARCH=amd64 go build -o app-linux
GOOS=linux   GOARCH=arm64 go build -o app-arm
GOOS=windows GOARCH=amd64 go build -o app.exe
GOOS=darwin  GOARCH=arm64 go build -o app-mac

# 静态链接（Docker scratch 镜像需要）
CGO_ENABLED=0 GOOS=linux go build -a -ldflags='-s -w -extldflags "-static"' -o app .

# 查看支持的所有平台
go tool dist list
```

### 注入构建信息 {#ldflags}

```bash
go build -ldflags="-X 'main.Version=1.2.3' -X 'main.BuildTime=$(date +%Y-%m-%d)'" -o app .
```

```go
var (
    Version   = "dev"
    BuildTime = "unknown"
)

func main() {
    flag.BoolFunc("version", "print version", func(string) error {
        fmt.Printf("v%s built at %s\n", Version, BuildTime)
        os.Exit(0)
        return nil
    })
}
```

### 条件编译（build tags） {#build-tags}

```go
//go:build linux
// +build linux        // 旧语法，兼容用

package main
```

```bash
go build -tags="dev,debug" .
```

常用场景：区分开发/生产配置、平台特定实现、集成测试（`//go:build integration`）。

> [!IMPORTANT]
> `//go:build` 行和 `package` 之间**必须有空行**，否则会被当成普通注释。

### 工具命令 {#go-tools}

```bash
go run .                 # 编译并运行
go vet ./...             # 静态检查（CI 必跑）
gofmt -l -w .            # 格式化（-l 列出需格式化的文件）
gofmt -s -w .            # 简化代码
go doc fmt.Println       # 查看文档
go doc -all time         # 包文档
go install golang.org/x/tools/cmd/goimports@latest    # 安装工具
go tool                  # Go 1.24+ 管理项目级工具依赖
```

静态检查推荐加 `golangci-lint`（集成 gofmt/vet/errcheck/staticcheck 等数十个 linter）。

## 小结 {#summary}

- **io.Reader/Writer** 是 Go I/O 的统一抽象，任意组合；大文件用 `bufio.Scanner` 而非 `ReadAll`
- **time** 用固定的参考时间格式化（`2006-01-02 15:04:05`），解析本地时间用 `ParseInLocation`
- **JSON**：Go 1.27 换成了 v2 引擎，**nil slice 变 `[]`、字段匹配区分大小写**，升级前务必检查 API 契约
- **net/http**：生产必须设超时；`defer resp.Body.Close()` 前要先读完 body
- **测试**：表驱动 + 子测试是标准风格；`-race`、`-cover`、`-bench` 是 CI 标配
- **模块**：`go mod tidy` 提交前必跑；多模块开发用 `go work` 代替一堆 replace
- **交叉编译**是 Go 的强项：`GOOS`/`GOARCH` + `CGO_ENABLED=0` 直接产出静态二进制

下一章是本教程的最后一章——**泛型与反射**，补齐现代 Go 的这两个重要能力。
