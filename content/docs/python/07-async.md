---
title: 第七章 异步编程
linkTitle: 异步编程
description: async/await 协程、事件循环、并发爬取与常见坑
weight: 47
---

# 异步编程

当程序大量等待网络、数据库或文件 IO 时，传统「一请求等一响应」会浪费时间。Python 的 `asyncio` 用单线程协程实现高效并发。本章从语法到实战再到避坑，带你掌握 `async`/`await`。

## 为什么需要 async {#why-async}

瓶颈在 **IO 密集型** 场景：发请求后 CPU 在「干等」响应。多线程也能并发，但切换有开销、受 GIL 限制。协程在**单线程内**主动让出控制权，等待 IO 时把执行权交给别的协程，实现高并发。

关键区分：**并发 ≠ 并行**。并发是交替推进多件事，并行是同时跑在多核。`asyncio` 是并发（单线程协程切换），不提供 CPU 并行。

## 基础语法 {#basics}

`async def` 定义协程，`await` 等待可等待对象，`asyncio.run()` 是入口：

```python
import asyncio

async def hello() -> None:
    print("开始")
    await asyncio.sleep(1)   # 模拟 IO，不阻塞整个线程
    print("一秒后")

asyncio.run(hello())
```

`await` 只能在 `async def` 内使用；`asyncio.run()` 在程序最外层调用一次。

## 协程对象 vs 任务 {#coroutine-task}

调用 `async def` 只返回 **coroutine 对象**，不执行；须 `await` 或交给循环才运行：

```python
async def task() -> int:
    await asyncio.sleep(0.1)
    return 42

c = task()          # 只是协程对象，未执行
```

真正**并发**用 `asyncio.create_task()` 包装成任务：

```python
import asyncio

async def worker(name: str, sec: float) -> str:
    await asyncio.sleep(sec)
    return f"{name} 完成"

async def main() -> None:
    t1 = asyncio.create_task(worker("A", 1))
    t2 = asyncio.create_task(worker("B", 1))
    print(await t1, await t2)      # 总耗时约 1 秒，而非 2 秒

asyncio.run(main())
```

## 并发核心 asyncio.gather {#gather}

`asyncio.gather` 同时驱动多个协程，按传入顺序收集结果：

```python
import asyncio

async def fetch(n: int) -> int:
    await asyncio.sleep(0.5)
    return n * n

async def main() -> None:
    print(await asyncio.gather(fetch(1), fetch(2), fetch(3)))  # [1, 4, 9]

asyncio.run(main())
```

`return_exceptions=True` 让异常以对象返回而非中断整体：

```python
async def boom() -> int:
    raise ValueError("出错")

results = await asyncio.gather(fetch(1), boom(), return_exceptions=True)
print(results)     # [1, ValueError('出错')]
```

`asyncio.wait` 返回「已完成/未完成」两组任务；`as_completed` 按完成顺序逐个产出：

```python
done, pending = await asyncio.wait({t1, t2}, timeout=2)
async for coro in asyncio.as_completed([t1, t2]):
    print(await coro)
```

## 实际例子：并发爬取 {#crawl-example}

用 `aiohttp` 并发请求多个 URL，再与同步 `requests` 对比耗时：

```python
# 安装：pip install aiohttp
import asyncio, time
import aiohttp

urls = ["https://httpbin.org/delay/1"] * 3

async def fetch(session: aiohttp.ClientSession, url: str) -> int:
    async with session.get(url) as resp:
        return resp.status

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(fetch(session, u) for u in urls))
    print("状态码:", results)

start = time.perf_counter()
asyncio.run(main())
print(f"异步耗时 {time.perf_counter() - start:.2f} 秒")   # 约 1 秒（并发）
```

同步对比：每个串行等 1 秒，共约 3 秒：

```python
# 安装：pip install requests
import requests, time

start = time.perf_counter()
for u in urls:
    requests.get(u)            # 阻塞等待，逐个完成
print(f"同步耗时 {time.perf_counter() - start:.2f} 秒")    # 约 3 秒
```

## 超时与取消 {#timeout-cancel}

`asyncio.wait_for` 加超时上限，超时抛 `asyncio.TimeoutError`：

```python
import asyncio

async def slow() -> None:
    await asyncio.sleep(10)

async def main() -> None:
    try:
        await asyncio.wait_for(slow(), timeout=2)
    except asyncio.TimeoutError:
        print("超时了")

asyncio.run(main())
```

`task.cancel()` 取消任务，协程收到 `CancelledError`，可在 `except` 里清理（记得重新抛出）：

```python
async def worker() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("被取消，执行清理")
        raise

async def main() -> None:
    t = asyncio.create_task(worker())
    await asyncio.sleep(1)
    t.cancel()
    await t

asyncio.run(main())
```

## 常见坑（重点） {#pitfalls}

**坑 1：协程里调用阻塞函数。** `time.sleep` 或同步 `requests` 会**阻塞整个事件循环**：

```python
async def bad() -> None:
    time.sleep(2)        # 错误：阻塞所有协程

async def good() -> None:
    await asyncio.sleep(2)                  # 让出控制权
    await asyncio.to_thread(time.sleep, 2)  # 阻塞调用丢到线程池（3.9+）
```

**坑 2：忘记 await。** 只调用不 `await` 永不执行，触发 `RuntimeWarning: coroutine was never awaited`：

```python
f()              # 错误：创建了协程却没 await
await f()        # 正确
```

**坑 3：在 async 里调用 asyncio.run。** `run` 应只在外层一次；内部再调用会报错：

```python
async def outer() -> None:
    await inner()          # 用 await 串联

asyncio.run(outer())       # 唯一一次 run
```

**坑 4：循环里串行 await。** 逐个 `await` 等于串行，失去并发：

```python
for u in urls:
    await fetch_one(u)                       # 低效

await asyncio.gather(*(fetch_one(u) for u in urls))   # 高效并发
```

## async with 与 async for {#async-with-for}

`async with` 用于异步上下文管理器（如 `aiohttp.ClientSession`）；`async for` 遍历异步迭代器：

```python
import asyncio

async def gen():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield i

async def main() -> None:
    async for x in gen():
        print(x)

asyncio.run(main())
```

`aiohttp` 的会话与请求都用 `async with` 管理资源：

```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.text()
```

## 同步原语 {#sync-primitives}

协程间需协调。`asyncio.Lock` 保证临界区独占：

```python
lock = asyncio.Lock()
async def safe_inc():
    async with lock:
        ...
```

`asyncio.Semaphore` 限流并发——例如最多 5 个请求：

```python
sem = asyncio.Semaphore(5)

async def fetch(session, url):
    async with sem:            # 超过 5 个在此排队
        async with session.get(url) as resp:
            return await resp.text()
```

`asyncio.Queue` 是协程安全的任务队列，常用于生产者-消费者模型。

## 与多线程/多进程的定位 {#positioning}

| 场景 | 推荐方案 |
| --- | --- |
| IO 密集（网络/数据库/文件） | `asyncio` 或线程池 |
| 阻塞的同步库 | `asyncio.to_thread` 桥接 |
| CPU 密集（计算/编码） | `multiprocessing` 或 `ProcessPoolExecutor` |

`asyncio.to_thread` 把无法改写的阻塞函数接入事件循环；真正多核并行靠多进程。

## 3.11 性能与事件循环 {#event-loop}

Python 3.11 大幅优化协程创建与任务调度性能，并改进异步错误回溯。事件循环是心脏，`asyncio.run()` 自动创建并关闭；手动管理时用：

```python
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# loop.run_until_complete(...)
loop.close()
```

日常几乎无需手动操作循环。

## 生态 {#ecosystem}

- **`aiohttp`**：成熟的异步 HTTP 客户端/服务端库。
- **`httpx`**：支持 `async` 的「requests 替代品」，API 友好。
- **`asyncpg`**：高性能异步 PostgreSQL 驱动。
- **`fastapi`**：基于 `async` 的 Web 框架（FastAPI 教程深入讲解）。

## 小结 {#summary}

`async`/`await` 通过单线程协程切换实现 IO 并发，核心是 `gather` 与 `create_task` 驱动并发、`wait_for`/`cancel` 控制生命周期。避开协程内阻塞、忘记 await、循环串行 await 等坑，配合信号量限流与 `to_thread` 桥接，即可写出高效正确的异步程序。