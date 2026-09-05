---
title: 第四章 Spring Boot 快速上手
linkTitle: Spring Boot
description: Spring Boot 的自动配置、起步依赖与快速搭建项目
weight: 14
---

# Spring Boot 快速上手

## 什么是 Spring Boot {#what-is-boot}

Spring Boot 是 Spring 的**快速开发框架**，核心目标是「约定优于配置」，让开发者用最少的配置快速创建独立运行的生产级应用。

## 核心特性 {#features}

- **自动配置（Auto-configuration）**：根据依赖自动配置 Spring 和第三方库。
- **起步依赖（Starters）**：一组预定义的依赖集合，如 `spring-boot-starter-web`。
- **内嵌服务器**：内置 Tomcat / Jetty，无需单独部署 WAR。

## 创建项目 {#create-project}

使用 [Spring Initializr](https://start.spring.io/) 或 IDE 向导创建，或手动编写：

```xml
<!-- pom.xml 关键依赖 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
</dependencies>
```

## 启动类 {#main-class}

```java
@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

`@SpringBootApplication` 是以下三个注解的组合：

```java
@SpringBootConfiguration
@EnableAutoConfiguration  // 自动配置的核心
@ComponentScan
```

## 配置文件 {#config}

```yaml
# application.yml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo
    username: root
    password: secret
```

## 自定义配置类 {#custom-config}

```java
@ConfigurationProperties(prefix = "app")
public record AppProperties(String name, int timeout) {}
```

## 小结 {#summary}

Spring Boot 通过自动配置和起步依赖，把 Spring 的复杂度封装起来。下一章学习数据访问与事务管理。
