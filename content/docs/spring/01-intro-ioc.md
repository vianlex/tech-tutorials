---
title: 第一章 Spring 概述与 IoC
linkTitle: 概述与 IoC
description: Spring 框架定位、核心容器与依赖注入（IoC）原理
weight: 11
---

# Spring 概述与 IoC

## 什么是 Spring {#what-is-spring}

Spring 是一个**轻量级的 Java 企业级开发框架**，核心是**控制反转（Inversion of Control, IoC）** 和**依赖注入（Dependency Injection, DI）**。它让开发者专注于业务逻辑，而对象的创建与装配交给容器管理。

> [!NOTE]
> Spring 于 2003 年诞生，由 Rod Johnson 创建，最初是为了解决 EJB 时代的复杂性问题。

## 控制反转与依赖注入 {#ioc-di}

传统方式中，对象自己创建它依赖的对象：

```java
// 传统方式：类自己 new 依赖
public class UserService {
    private UserRepository repo = new UserRepository(); // 硬编码
}
```

使用 Spring 后，依赖由容器注入：

```java
@Service
public class UserService {
    private final UserRepository repo;

    // 构造器注入：Spring 容器自动提供 UserRepository 实例
    public UserService(UserRepository repo) {
        this.repo = repo;
    }
}
```

## 依赖注入的三种方式 {#di-ways}

| 方式 | 说明 | 推荐程度 |
|------|------|----------|
| 构造器注入 | 通过构造方法传入依赖 | ✅ 推荐（不可变、依赖明确） |
| Setter 注入 | 通过 setter 方法注入 | 可选依赖时使用 |
| 字段注入 | 通过 `@Autowired` 字段 | ❌ 不推荐（难以测试） |

## 容器的两种实现 {#container}

1. **BeanFactory** — 最基础的容器，懒加载。
2. **ApplicationContext** — 常用容器，在 BeanFactory 基础上增加国际化、事件、AOP 等能力。

```java
// 通过配置类创建容器
ApplicationContext context =
    new AnnotationConfigApplicationContext(AppConfig.class);
UserService service = context.getBean(UserService.class);
```

## 常用注解 {#annotations}

```java
@Component      // 通用组件
@Service        // 业务层
@Repository     // 数据访问层
@Configuration  // 配置类
@Bean           // 声明 Bean
@Scope          // 作用域：singleton / prototype
```

## 小结 {#summary}

IoC 把「谁创建对象、谁装配依赖」的控制权从代码转移到了容器，是实现解耦的核心机制。下一章将学习建立在 IoC 之上的 AOP。
