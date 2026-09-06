---
title: 第四章 Spring Boot 快速上手
linkTitle: Spring Boot
description: Spring Boot 自动配置原理、起步依赖、配置体系、内嵌服务器与 Actuator、Spring Boot 3 新特性、Native Image、配置元数据、优雅停机
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

## Spring Boot 3.x 重大变化与新特性 {#spring-boot-3}

Spring Boot 3.x（搭配 Spring Framework 6.x）是当下主流，了解这一代的特性非常必要。

### 与 2.x 的核心差异

```text
┌──────────────────────────────────────────────────────────┐
│ Spring Boot 2.x           │ Spring Boot 3.x             │
├──────────────────────────────────────────────────────────┤
│ Java 8+                   │ Java 17+                    │
│ javax.servlet / jpa       │ jakarta.servlet / jpa       │
│ spring.factories 自动配置 │ imports 文件                │
│ Logback 1.2               │ Logback 1.4                 │
│ HikariCP 4.x              │ HikariCP 5.x                │
│ Spring Security 5.x       │ Spring Security 6.x         │
│ 支持 WebFlux              │ WebFlux 增强 + RSocket      │
└──────────────────────────────────────────────────────────┘
```

**命名空间迁移**是最大破坏性变更：所有 `javax.*` 替换为 `jakarta.*`。Maven 全局替换：

```bash
# 老项目升级时
find . -name "*.java" -exec sed -i 's/javax\./jakarta\./g' {} +
```

### GraalVM Native Image

Spring Boot 3 与 GraalVM 深度集成，能把应用编译成**原生可执行文件**：

```bash
# 启动比 JVM 快 10-100 倍，内存占用降至 1/10
mvn -Pnative native:compile
./target/demo
```

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.graalvm.buildtools</groupId>
            <artifactId>native-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

适用场景：Serverless、冷启动敏感、内存受限的边缘计算。**注意事项**：反射、动态代理、classpath 扫描等需要显式配置（多数已自动处理，少数需要 `reflect-config.json`）。

### AOT（Ahead-of-Time）处理

Spring 6 引入的 AOT 引擎对 Bean 进行**预先解析**，把运行时的反射调用转成直接的 Java 调用，是 Native Image 能工作的关键：

```java
// 由 AOT 阶段生成的代码（自动）
RuntimeHints hints = RuntimeHints.register();
hints.reflection().registerType(User.class, MemberCategory.INVOKE_DECLARED_METHODS);
```

## 配置元数据 spring-configuration-metadata.json {#config-metadata}

为 `@ConfigurationProperties` 自动生成 IDE 提示（输入即提示、自动补全、文档悬浮）：

```xml
<!-- 引入处理器 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-configuration-processor</artifactId>
    <optional>true</optional>
</dependency>
```

```java
@ConfigurationProperties(prefix = "app.cache")
public class CacheProperties {

    /** 缓存 TTL（秒） */
    private int ttl = 300;

    /** 最大缓存条目 */
    private int maxSize = 10_000;

    // getters / setters
}
```

构建后 `META-INF/spring-configuration-metadata.json` 自动生成，`application.yml` 写 `app.cache.ttl` 就有提示了。

```yaml
# 写配置时 IDE 自动补全 + 悬浮文档
app:
  cache:
    ttl: 600
    max-size: 50000
```

## 配置文件加密 {#config-encrypt}

生产数据库密码等敏感配置不应明文写在 `application.yml`。**jasypt-spring-boot-starter** 是最常用的加密方案：

```xml
<dependency>
    <groupId>com.github.ulisesbocchio</groupId>
    <artifactId>jasypt-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

```yaml
jasypt:
  encryptor:
    password: ${JASYPT_PASSWORD}    # 主密码从环境变量读，不入库

spring:
  datasource:
    password: ENC(AbCdEf123...加密结果...)
```

加密过程（开发期执行一次）：

```java
StringPool stringEncryptor = new BasicStringEncryptor();
stringEncryptor.setPassword("my-secret-key");   // 与 jasypt.encryptor.password 一致
String encrypted = stringEncryptor.encrypt("real-db-password");
// 输出 ENC(AbCdEf123...) 填到配置文件
```

> [!TIP]
> 生产环境 `JASYPT_PASSWORD` 通过 K8s Secret、Vault、AWS Secrets Manager 等注入，避免硬编码在镜像或仓库。

## 启动监听器与 Runner {#startup-listener}

`ApplicationListener` 监听容器生命周期事件：

```java
@Component
public class StartupLogger implements ApplicationListener<ApplicationReadyEvent> {
    @Override
    public void onApplicationEvent(ApplicationReadyEvent event) {
        log.info("应用启动完成，耗时 {}ms", 
                 event.getApplicationContext().getStartupDate().getTime() - 
                 ManagementFactory.getRuntimeMXBean().getStartTime());
    }
}
```

**常用事件**：

| 事件 | 时机 |
|------|------|
| `ApplicationStartingEvent` | 最早：上下文创建前 |
| `ApplicationEnvironmentPreparedEvent` | 环境准备好 |
| `ApplicationPreparedEvent` | Bean 定义加载完 |
| `ContextRefreshedEvent` | 容器刷新完成（Bean 创建完） |
| `ApplicationStartedEvent` | Runner 执行前 |
| `ApplicationReadyEvent` | 应用就绪，可对外服务 |
| `ContextClosedEvent` | 容器关闭中 |
| `ContextStoppedEvent` / `ContextStoppedEvent` | 容器停止 |

`ApplicationRunner` / `CommandLineRunner` 在应用就绪后执行：

```java
@Component
@Order(1)
public class CacheWarmerRunner implements ApplicationRunner {
    @Override
    public void run(ApplicationArguments args) throws Exception {
        // 预热缓存、加载字典、初始化定时任务等
    }
}
```

## 优雅停机 {#graceful-shutdown}

容器关闭时，**正在处理的请求怎么办？** 默认会强制中断，导致用户看到 502。

```yaml
server:
  shutdown: graceful                # 启用优雅停机

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # 最多等待 30s
```

```mermaid
flowchart LR
    A["收到 SIGTERM"] --> B["停止接收新请求"]
    B --> C["等待正在处理的请求完成<br/>（最多 30s）"]
    C --> D{"完成？"}
    D -->|"是"| E["关闭线程池<br/>关闭容器"]
    D -->|"否（超时）"| E
```

> [!TIP]
> Kubernetes 部署时配合 `terminationGracePeriodSeconds: 35`（比 Spring 的 30s 多 5s），确保 Pod 被杀前 Spring 优雅退出。

## 启动优化：延迟初始化与运行期探针 {#startup-opt}

### 延迟初始化

```yaml
spring:
  main:
    lazy-initialization: true        # 所有 Bean 懒加载
```

**好处**：启动更快。**坏处**：把启动期错误延迟到第一次访问；隐式依赖更难发现（要启用再用）。**生产慎用**——除非启动时间真的成为瓶颈。

### 启动耗时探针

```yaml
spring:
  application:
    admin:
      enabled: true                  # 开启 Spring Boot Admin 端点
```

或用 **Spring Boot 3 + Actuator 的 `startup` 端点**：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: startup
  endpoint:
    startup:
      enabled: true
```

访问 `/actuator/startup` 拿到每个 Bean 的初始化耗时，定位启动慢的根因。

## Spring Modulith：模块化单体 {#modulith}

Spring Boot 3 引入的 **Modulith** 帮你把单体应用按"业务包"组织成模块，模块边界通过编译期 + 运行期双重校验：

```java
// com.example.orders.OrderModule
@ApplicationModule(
    displayName = "订单模块",
    allowedDependencies = {"customers", "invoices"}  // 只允许依赖这俩模块
)
package com.example.orders;
```

```java
// 在订单模块内访问客户模块：通过 Modulith API 显式暴露
public class OrderService {
    private final CustomerFacade customer;   // 门面，只暴露必要的 API

    public OrderService(CustomerFacade customer) {
        this.customer = customer;
    }
}
```

```bash
# 启动时 Modulith 会校验模块依赖图
mvn test -Dtest=ModulithTests
```

适用：**业务复杂、团队扩张** 的单体应用——既享受单体部署的简单，又保留模块边界的纪律。

## 小结（升级版） {#summary-updated}

Spring Boot 用「自动配置 + 起步依赖 + 外部化配置」把 Spring 的复杂度封装为开箱即用。本章进阶内容：

- **Spring Boot 3.x 重大变化**：Java 17+、jakarta 命名空间、imports 取代 spring.factories。
- **GraalVM Native Image**：编译成原生二进制，启动毫秒级、内存骤降。
- **AOT 处理**：把运行期反射转成编译期生成代码，是 Native 的基础。
- **配置元数据**：configuration-processor 生成 IDE 提示。
- **配置文件加密**：jasypt + 环境变量注入主密钥。
- **启动监听器**：7 类生命周期事件 + Runner 接口。
- **优雅停机**：`shutdown: graceful` + lifecycle timeout，避免请求被中断。
- **启动优化**：延迟初始化的利弊、Actuator startup 端点。
- **Spring Modulith**：模块化单体的工程实践。

下一章学习数据访问与事务——这是企业应用真正落地持久化与一致性的关键。
