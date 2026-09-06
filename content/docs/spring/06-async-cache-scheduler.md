---
title: 第六章 异步、缓存与定时任务
linkTitle: 异步、缓存与调度
description: "@Async 异步调用与 TaskExecutor、@Scheduled 定时任务与 Cron、Spring Cache 抽象（@Cacheable/@CachePut/@CacheEvict）与 Caffeine"
weight: 16
---

# 异步、缓存与定时任务

企业应用除了请求-响应、数据库事务，还有一类「不阻塞主流程」的需求：异步发短信、定时跑报表、把热点数据缓存起来。本章讲 Spring 在这三件事上的统一抽象。

## @Async：让方法异步执行 {#async}

### 基础使用

```java
@Service
public class NotificationService {

    // ✅ 简单用法：返回 void 或 CompletableFuture
    @Async
    public void sendEmail(String to, String content) {
        // 模拟耗时
        mailClient.send(to, content);
    }

    @Async
    public CompletableFuture<User> fetchUserAsync(Long id) {
        return CompletableFuture.completedFuture(userRepo.findById(id).orElse(null));
    }
}
```

调用方**不需要等待**返回值，调用立即返回：

```java
@RestController
public class OrderController {
    @Autowired
    private NotificationService notificationService;

    @PostMapping
    public Result create() {
        orderService.create();
        notificationService.sendEmail("user@example.com", "订单已创建");  // 异步发出
        return Result.ok();  // 立即返回，不等邮件发送完成
    }
}
```

### 启用与配置

```java
@Configuration
@EnableAsync    // 开启异步支持
public class AsyncConfig { /* ... */ }
```

### 自定义线程池

默认 Spring 用 `SimpleAsyncTaskExecutor`——**每次都创建新线程**，生产环境绝对不能用。务必配置专用线程池：

```java
@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("mailExecutor")
    public Executor mailExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);          // 核心线程数
        executor.setMaxPoolSize(16);          // 最大线程数
        executor.setQueueCapacity(100);       // 队列容量
        executor.setKeepAliveSeconds(60);
        executor.setThreadNamePrefix("mail-");
        // 拒绝策略：CallerRunsPolicy（调用方线程执行，避免丢失任务）
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        executor.initialize();
        return executor;
    }
}

@Service
public class NotificationService {
    @Async("mailExecutor")   // 指定使用的线程池
    public void sendEmail(String to, String content) { /* ... */ }
}
```

> [!TIP]
> **核心原则**：不同业务用**独立线程池**——邮件、短信、文件处理各一个池，互相隔离。一个池满不会影响另一个池。

### @Async 的陷阱

```java
@Service
public class UserService {

    // ❌ 自调用：this 调方法不走代理
    public void register(User u) {
        saveUser(u);
        sendWelcome(u);    // 没走代理，@Async 不生效
    }

    @Async
    public void sendWelcome(User u) { /* ... */ }
}
```

解法与事务自调用同源——**拆类**或注入自身代理：

```java
@Service
public class UserService {
    private final UserService self;
    public UserService(@Lazy UserService self) { this.self = self; }

    public void register(User u) {
        saveUser(u);
        self.sendWelcome(u);  // ✅ 走代理
    }

    @Async
    public void sendWelcome(User u) { /* ... */ }
}
```

**返回值必须是 `Future` 或 `void`**——直接返回对象会被 Spring 包装成 `AsyncResult`，类型不匹配编译失败。

## @Scheduled：定时任务 {#scheduled}

### 基础使用

```java
@Component
@EnableScheduling   // 在启动类或配置类加一次
public class ScheduledTasks {

    // 1. fixedRate：上次开始后多久再执行（高频任务用这个）
    @Scheduled(fixedRate = 5000)
    public void heartbeat() {
        log.info("heartbeat");
    }

    // 2. fixedDelay：上次结束后多久再执行（避免任务重叠）
    @Scheduled(fixedDelay = 10_000)
    public void syncData() {
        syncService.run();
    }

    // 3. cron：Cron 表达式
    @Scheduled(cron = "0 0 2 * * ?")       // 每天凌晨 2 点
    public void backup() {
        backupService.run();
    }
}
```

### Cron 表达式详解

```
秒 分 时 日 月 周 [年]
```

| 字段 | 允许值 | 特殊字符 |
|------|--------|----------|
| 秒 | 0-59 | `, - * /` |
| 分 | 0-59 | `, - * /` |
| 时 | 0-23 | `, - * /` |
| 日 | 1-31 | `, - * ? / L W` |
| 月 | 1-12 | `, - * /` |
| 周 | 0-6 (日=0) | `, - * ? / L #` |

**常用示例**：

```text
0 0 2 * * ?            # 每天凌晨 2 点
0 */10 * * * ?         # 每 10 分钟
0 0 9-18 * * ?         # 每天 9 点到 18 点整点
0 30 9 * * MON-FRI     # 工作日上午 9:30
0 0 0 1 * ?            # 每月 1 日零点
```

> [!TIP]
> Spring 的 Cron 表达式比标准 Unix Cron 多**秒**字段（6 位 vs 5 位）。如果你熟悉 Linux Cron，写 Spring 时前面加秒位即可。

### 定时任务线程池

```java
@Configuration
@EnableScheduling
public class ScheduleConfig implements SchedulingConfigurer {

    @Override
    public void configureTasks(ScheduledTaskRegistrar registrar) {
        registrar.setScheduler(taskScheduler());
    }

    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(8);                       // 池大小
        scheduler.setThreadNamePrefix("scheduled-");
        scheduler.setRejectedExecutionHandler(
            new ThreadPoolExecutor.CallerRunsPolicy());
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        scheduler.setAwaitTerminationSeconds(60);
        scheduler.initialize();
        return scheduler;
    }
}
```

**注意**：默认所有 `@Scheduled` 任务共享一个**单线程**调度器——一个任务执行 10s 会**阻塞下一个**任务的执行。生产务必配置线程池。

### 分布式定时任务

单机 `@Scheduled` 在多实例部署时会**重复执行**。解决：

```text
1. 分布式锁（Redis / Zookeeper）：抢到锁的实例才执行
2. Quartz + JDBC Store：原生支持分布式调度
3. XXL-JOB / Elastic-Job：成熟的分布式任务调度框架
```

```java
// Redis 分布式锁实现单点执行
@Scheduled(cron = "0 0 2 * * ?")
public void backup() {
    String lockKey = "backup:lock";
    if (redis.setIfAbsent(lockKey, "1", Duration.ofHours(1))) {
        try {
            backupService.run();
        } finally {
            redis.delete(lockKey);
        }
    }
}
```

## Spring Cache 抽象 {#cache}

Spring Cache 把"缓存逻辑"从业务代码中抽离，用注解声明式配置：

```java
@Service
@EnableCaching    // 启动类或配置类加一次
public class UserService {

    @Cacheable(value = "user", key = "#id")        // 读：先查缓存，没有再执行方法
    public User findById(Long id) {
        return userRepo.findById(id).orElse(null);
    }

    @CachePut(value = "user", key = "#user.id")    // 写：执行方法 + 回写缓存
    public User update(User user) {
        return userRepo.save(user);
    }

    @CacheEvict(value = "user", key = "#id")       // 删：清缓存
    public void delete(Long id) {
        userRepo.deleteById(id);
    }

    @Caching(evict = {
        @CacheEvict(value = "user", key = "#userId"),
        @CacheEvict(value = "userList", key = "#userId")
    })                                              // 组合：一次清多个缓存
    public void delete2(Long userId) { /* ... */ }
}
```

### key 生成规则（SpEL）

```java
// 方法参数
@Cacheable(value = "user", key = "#id")                      // 参数 id
@Cacheable(value = "user", key = "#user.id")                 // 参数对象的 id
@Cacheable(value = "user", key = "#p0")                      // 第 1 个参数（p0/p1/...）
@Cacheable(value = "user", key = "#root.methodName + #id")    // 方法名 + 参数

// 多个参数组合
@Cacheable(value = "user", key = "#dept + ':' + #name")

// 条件
@Cacheable(value = "user", key = "#id", condition = "#id > 0")
@Cacheable(value = "user", key = "#id", unless = "#result == null")  // 结果为 null 不缓存
```

### 缓存实现选型

| 实现 | 依赖 | 特点 |
|------|------|------|
| **Caffeine** | `caffeine` | JVM 内本地缓存，最快最常用 |
| **Redis** | `spring-boot-starter-data-redis` | 分布式，多实例共享 |
| **Simple** | 无 | 默认 ConcurrentHashMap，单测用 |
| **Ehcache** | `ehcache` | 老牌，支持堆外/磁盘 |

**Caffeine（推荐本地缓存）**：

```yaml
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=10000,expireAfterWrite=30s,recordStats
    cache-names: user,product,order
```

```java
// 上述 user/product/order 三个缓存按 Caffeine 配置生效
```

**Redis（分布式缓存）**：

```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 30m          # 全局 TTL
      use-key-prefix: true       # key 加缓存名前缀
      cache-null-values: false   # null 不缓存（避免穿透）
```

```java
// 指定 TTL：@Cacheable(value = "user", key = "#id") 上无单独 TTL 配置
// 进阶：在 RedisCacheManagerBuilderCustomizer 内 per-cache 配置
@Bean
public RedisCacheManagerBuilderCustomizer customizer() {
    return builder -> builder
        .withCacheConfiguration("user",
            RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(30)))
        .withCacheConfiguration("product",
            RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofHours(1)));
}
```

### 多级缓存（Caffeine + Redis）

```java
public class LayeredCacheManager implements CacheManager {
    private final CacheManager l1;     // Caffeine
    private final CacheManager l2;     // Redis

    // 读：先 L1，没有读 L2，还没有回源 + 写回两级
    // 写：清 L1 + 清 L2
}
```

实际项目用现成组件：[jetcache](https://github.com/alibaba/jetcache)、[J2Cache](https://gitee.com/ld/J2Cache) 都内置多级缓存支持。

### @Cacheable 失效清单

与 `@Transactional` 同源——AOP 代理外不生效：

- ❌ **同类内部调用**——同上，必须走代理。
- ❌ **private/final 方法**——同上。
- ❌ **非 Bean 方法**——手动 new 的对象没被代理。

> [!TIP]
> **`@Cacheable` 与 `@Transactional` 顺序问题**：当一个方法既要事务又要缓存时，Spring 默认拦截顺序由 BeanName 决定。**安全做法**——把缓存方法与事务方法**拆到不同 Bean**，避免顺序纠纷。

## 异步事件与监听器组合 {#async-event}

把 `@Async` 与 `@EventListener` 组合，是最常见的"解耦通知"模式：

```java
@Service
public class OrderService {
    @Autowired
    private ApplicationEventPublisher publisher;

    @Transactional
    public void placeOrder(Order o) {
        orderRepo.save(o);
        publisher.publishEvent(new OrderPlacedEvent(o.getId()));
    }
}

@Component
public class NotificationListener {
    @Async
    @EventListener
    public void onOrderPlaced(OrderPlacedEvent e) {
        mailClient.send(/* ... */);   // 异步发邮件，不阻塞下单主流程
    }
}
```

**`@TransactionalEventListener`** 让监听器在事务**提交后**才执行（避免事务回滚但邮件已发）：

```java
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
@Async
public void onPaid(OrderPaidEvent e) {
    // 事务已提交 + 异步执行
    mq.send("order-paid", e.getOrderId());
}
```

## 小结 {#summary}

本章覆盖了企业开发三个高频组件：

- **`@Async`**：方法异步执行，配套独立 `TaskExecutor` 线程池；自调用失效（与 `@Transactional` 同源）。
- **`@Scheduled`**：定时任务，Cron 表达式 6 位（秒+分+时+日+月+周）；分布式场景需加分布式锁或用 XXL-JOB。
- **Spring Cache**：声明式缓存抽象（`@Cacheable`/`@CachePut`/`@CacheEvict`），Caffeine（本地最快）/Redis（分布式）/多级缓存选型。
- **事务与缓存的顺序**：用 `TransactionSynchronization` 控制"提交后再清缓存"，避免缓存穿透。
- **异步事件**：`@TransactionalEventListener(AFTER_COMMIT) + @Async` 是最优雅的"事务提交后异步通知"模式。

下一章进入 Spring Security——企业应用必备的安全框架，从认证到授权完整覆盖。