---
title: 第四章 Spring Boot 快速上手
linkTitle: Spring Boot
description: Spring Boot 自动配置原理、起步依赖、配置体系、内嵌服务器与 Actuator 健康检查
weight: 14
---

# Spring Boot 快速上手

## 什么是 Spring Boot {#what-is-boot}

Spring Boot 是 Spring 的**快速开发框架**，核心目标是「约定优于配置（Convention over Configuration）」，让开发者用最少的配置快速创建独立运行的生产级应用。它把 Spring Framework 的复杂度封装进「自动配置 + 起步依赖」两张牌里：你加依赖，它就替你配好；你想改，再覆盖默认。

> [!NOTE]
> Spring Boot 不是取代 Spring Framework，而是**运行在它之上**的封装层。本教程基于 Spring Boot 3.x（要求 Java 17+，底层 Spring Framework 6.x，Jakarta EE 9+ 命名空间）。

## 核心特性 {#features}

- **自动配置（Auto-configuration）**：根据 classpath 上的依赖，自动装配合理的默认 Bean。
- **起步依赖（Starters）**：一组「功能导向」的依赖集合，如 `spring-boot-starter-web` 一次性引入 Tomcat + Spring MVC + Jackson。
- **内嵌服务器**：内置 Tomcat / Jetty / Undertow，打出的 jar 用 `java -jar` 直接运行，无需外部容器。
- **Actuator**：生产级健康检查、指标、环境信息端点。
- **外部化配置**：统一的 `application.yml` + 多环境 + 命令行/环境变量覆盖。

## 创建项目 {#create-project}

使用 [Spring Initializr](https://start.spring.io/) 或 IDE 向导，也可手动编写 Maven 构建文件：

```xml
<!-- pom.xml 关键依赖 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <!-- web 起步依赖：自动带来 Tomcat + MVC + Jackson + 校验 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <!-- 测试起步依赖 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

`spring-boot-starter-parent` 提供了依赖版本管理、默认插件与资源过滤，让你几乎不必写版本号。

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
@SpringBootConfiguration      // 标记这是配置类（本质是 @Configuration）
@EnableAutoConfiguration       // 自动配置的核心开关
@ComponentScan                 // 扫描主类所在包及其子包
```

`SpringApplication.run(...)` 做了什么（启动流程简述）：

1. 推断应用类型（Servlet / Reactive / 普通）。
2. 从 `META-INF/spring.factories`（旧）或 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（新）加载**自动配置类**候选清单。
3. 创建 `Environment`，加载 `application.yml` 等外部化配置。
4. 实例化 `ApplicationContext`，触发组件扫描与自动配置（条件注解过滤）。
5. 执行 `ApplicationRunner` / `CommandLineRunner`，触发 `ApplicationReadyEvent`，应用就绪。

```java
// 想干预启动过程，可实现 Runner
@Component
public class InitRunner implements ApplicationRunner {
    public void run(ApplicationArguments args) {
        log.info("应用启动完成，收到的参数：{}", args.getOptionNames());
    }
}
```

## 自动配置原理 {#auto-config}

「为什么我只加了 `spring-boot-starter-web`，Tomcat 和 MVC 就自动就绪了？」答案在自动配置机制里。

核心链路：

```text
@EnableAutoConfiguration
   ↓ 导入
AutoConfigurationImportSelector
   ↓ 读取
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
   ↓ 经过条件注解过滤（@ConditionalOnXxx）
真正生效的自动配置类（如 WebMvcAutoConfiguration、DataSourceAutoConfiguration）
   ↓ 注册默认 Bean
开箱即用
```

SpringBoot 2.7 起废弃 `spring.factories`，改为 `META-INF/spring/...AutoConfiguration.imports` 列出所有自动配置全限定名；每个配置类都被 `@ConditionalOnClass`、`@ConditionalOnMissingBean` 等保护，只有「依赖存在且用户未自定义」时才生效。

## 自定义 starter 完整示例 {#custom-starter}

理解自动配置的最佳方式，是写一个自己的 starter（例如一个统一的「幂等注解」组件）。

**1) 自动配置类**：

```java
// 自动配置类：在用户未自定义 IdempotentManager 时生效
@AutoConfiguration
@ConditionalOnClass(IdempotentManager.class)
@EnableConfigurationProperties(IdempotentProperties.class)
public class IdempotentAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public IdempotentManager idempotentManager(IdempotentProperties props) {
        return new IdempotentManager(props.getPrefix());
    }
}
```

**2) 配置属性绑定类**：

```java
@ConfigurationProperties(prefix = "idempotent")
public record IdempotentProperties(String prefix) {
    public IdempotentProperties { prefix = prefix == null ? "idem:" : prefix; }
}
```

**3) 注册自动配置**（在 starter 的 `resources/META-INF/spring/` 下建文件）：

```text
# org.springframework.boot.autoconfigure.AutoConfiguration.imports
com.example.idempotent.IdempotentAutoConfiguration
```

**4) 用户侧使用**：只需引入你的 starter 依赖，并在 `application.yml` 写：

```yaml
idempotent:
  prefix: order:idem:
```

`IdempotentManager` 即被自动装配，无需任何 `@Configuration`。这正是 Spring Boot「可插拔能力」的精髓。

## 配置体系 {#config}

Spring Boot 配置分为「读取」与「绑定」两层。

**多环境配置**：主文件 + 环境片段文件，按 `spring.profiles.active` 激活：

```yaml
# application.yml
spring:
  profiles:
    active: dev
---
# application-dev.yml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:h2:mem:testdb
---
# application-prod.yml
server:
  port: 80
spring:
  datasource:
    url: ${DB_URL}   # 用环境变量注入生产库地址
```

**两种绑定方式对比**：

| 方式 | 写法 | 推荐度 | 说明 |
|------|------|--------|------|
| `@Value` | `@Value("${app.name}")` | ❌ 零散 | 不支持类型安全、难校验、难提示 |
| `@ConfigurationProperties` | 前缀 + 类型绑定 | ✅ 推荐 | 类型安全、自动校验、IDE 提示 |

```java
@ConfigurationProperties(prefix = "app")   // 绑定 app.* 下所有配置
@Validated
public record AppProperties(
        @NotBlank String name,
        @Min(1) int timeout,
        List<String> hosts) {}
```

**配置优先级（由低到高，高者覆盖低者）**：

```text
1. 默认属性（SpringApplication.setDefaultProperties）
2. application.yml（含多环境片段）
3. 操作系统环境变量
4. 命令行参数（--app.timeout=5000）
5. 测试中的 @TestPropertySource / @DynamicPropertySource
```

> [!TIP]
> 命令行参数优先级很高，常用于容器/云环境注入数据库地址等敏感配置（避免写进仓库）。这也体现了「外部化配置」原则：构建一次、到处运行。

## 内嵌服务器原理与定制 {#embedded-server}

Spring Boot 把 Tomcat（默认）/ Jetty / Undertow 作为**依赖**引入，启动时在进程内 `new` 出一个服务器并部署 DispatcherServlet，因此打成 `jar` 即可 `java -jar` 运行，无需独立 WAR 容器。

定制方式一：配置文件

```yaml
server:
  port: 8080
  tomcat:
    threads:
      max: 200          # 最大工作线程
      min-spare: 10     # 最小空闲线程
    max-connections: 10000
    accept-count: 100   # 等待队列长度
```

定制方式二：编程式（WebServerFactoryCustomizer）

```java
@Bean
public WebServerFactoryCustomizer<TomcatServletWebServerFactory> tomcatCustomizer() {
    return factory -> {
        factory.setPort(8080);
        factory.addConnectorCustomizers(connector -> {
            // 例如调整 keep-alive、压缩等
        });
    };
}
```

> [!WARNING]
> 默认 Tomcat 线程数很小（200），高并发接口需按压测结果调大 `threads.max`；但线程数不是越大越好，需匹配 CPU、下游（DB/远程调用）并发能力，避免线程堆积。

## 条件注解组合与 `@Profile` {#conditional-profile}

自动配置靠条件注解工作，业务代码同样可用它们做「按需装配」：

```java
@Configuration
public class FeatureConfig {

    @Bean
    @Profile("dev")                 // 仅 dev 环境
    public MockPaymentClient mockPayment() { return new MockPaymentClient(); }

    @Bean
    @Profile("!dev")                // 非 dev（prod/test）环境
    public RealPaymentClient realPayment() { return new RealPaymentClient(); }

    @Bean
    @ConditionalOnProperty(name = "feature.mq.enabled", havingValue = "true")
    public MqPublisher mqPublisher() { return new MqPublisher(); }

    @Bean
    @ConditionalOnMissingBean
    public CacheManager cacheManager() { return new SimpleCacheManager(); }
}
```

常用条件注解：`@ConditionalOnClass`、`@ConditionalOnMissingBean`、`@ConditionalOnProperty`、`@ConditionalOnWebApplication`、`@Profile`、`@ConditionalOnExpression`（SpEL 表达式）。组合使用可表达复杂装配逻辑。

## Actuator 健康检查与指标 {#actuator}

Actuator 暴露运行期端点，是生产可观测性的第一道入口。引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

配置暴露与安全：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env   # 谨慎暴露 env（含敏感配置）
  endpoint:
    health:
      show-details: when_authorized         # 详情仅对授权用户展示
    health:
      probes:
        enabled: true                        # 启用 k8s 存活/就绪探针
```

常用端点：

- `/actuator/health`：应用健康（磁盘、数据库、Redis 等上游状态聚合）。
- `/actuator/metrics`：JVM、HTTP 请求数、线程池等指标。
- `/actuator/info`：自定义 `info.*` 应用信息。
- `/actuator/prometheus`：对接 Prometheus 采集（需 `micrometer-registry-prometheus`）。

> [!WARNING]
> `env`、`configprops`、`heapdump` 等端点会泄露配置与内存，生产环境务必**只暴露必要端点**并叠加 Spring Security 鉴权，否则等于把服务器钥匙挂在门口。

## 小结 {#summary}

Spring Boot 用「自动配置 + 起步依赖 + 外部化配置」把 Spring 的复杂度封装为开箱即用，并通过内嵌服务器与 Actuator 补齐运行与运维能力。理解了自动配置原理，你也能写出自己的 starter。下一章学习数据访问与事务——这是企业应用真正落地持久化与一致性的关键。
