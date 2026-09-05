---
title: 第二章 AOP 面向切面编程
linkTitle: AOP 切面编程
description: Spring AOP 的切面、通知、切点与常见应用场景
weight: 12
---

# AOP 面向切面编程

## 什么是 AOP {#what-is-aop}

AOP（Aspect-Oriented Programming，面向切面编程）把**横切关注点**（如日志、事务、安全）从业务逻辑中分离出来，避免代码重复。

> [!TIP]
> 日志、事务、权限校验这类逻辑散落在每个方法里，是典型的「横切关注点」，正适合用 AOP 抽取。

## 核心概念 {#concepts}

- **切面（Aspect）**：横切关注点的模块化，如 `LoggingAspect`。
- **通知（Advice）**：切面在特定时机执行的动作。
- **切点（Pointcut）**：定义在哪些方法上织入通知。
- **连接点（Join Point）**：程序执行的某个点，如方法调用。

## 通知类型 {#advice-types}

| 通知 | 时机 | 注解 |
|------|------|------|
| 前置 | 方法执行前 | `@Before` |
| 后置 | 方法正常返回后 | `@AfterReturning` |
| 异常 | 方法抛异常后 | `@AfterThrowing` |
| 最终 | 无论是否异常都执行 | `@After` |
| 环绕 | 包裹整个方法 | `@Around` |

## 示例：日志切面 {#logging-example}

```java
@Aspect
@Component
public class LoggingAspect {

    // 切点：匹配 service 包下所有方法
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceMethods() {}

    @Around("serviceMethods()")
    public Object log(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed(); // 执行原方法
        long cost = System.currentTimeMillis() - start;
        System.out.println(pjp.getSignature() + " 耗时 " + cost + "ms");
        return result;
    }
}
```

## 常见应用 {#applications}

1. **事务管理** — Spring 的 `@Transactional` 就是 AOP 的典型实现。
2. **日志记录** — 统一记录方法入参、耗时。
3. **权限校验** — 在方法执行前检查权限。
4. **性能监控** — 统计方法调用频率与耗时。

## 小结 {#summary}

AOP 建立在 IoC 之上，通过「切面」把横切逻辑从业务代码中剥离。它与 IoC 共同构成 Spring 的两大基石。
