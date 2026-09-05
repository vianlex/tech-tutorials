---
title: 第五章 实战与常见问题
linkTitle: 实战与常见问题
description: 打包可执行 jar、跳过测试、profile 多环境、常用属性、跳过与离线模式、高频排坑
weight: 90
---

# 实战与常见问题

前四章掌握了 Maven 的理论模型，本章聚焦日常开发中的高频实战技巧与那些「一看就会、一踩就懵」的坑。

## 打包可执行 jar {#executable-jar}

### 普通项目：maven-assembly / shade

普通 jar 默认**不包含依赖**，直接 `java -jar` 会报 `ClassNotFoundException`。要打「带依赖的可执行 fat jar」，用 `maven-assembly-plugin` 或 `maven-shade-plugin`：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.2</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals><goal>shade</goal></goals>
            <configuration>
                <transformers>
                    <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                        <mainClass>com.example.Main</mainClass>  <!-- 指定入口类 -->
                    </transformer>
                </transformers>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### Spring Boot：spring-boot-maven-plugin

Spring Boot 项目则用官方插件直接打可执行 fat jar：

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <version>3.2.0</version>
    <executions>
        <execution>
            <goals><goal>repackage</goal></goals>  <!-- 重打包成可执行 jar -->
        </execution>
    </executions>
</plugin>
```

```bash
mvn clean package
java -jar target/app.jar
```

> [!TIP]
> 普通 jar 与 fat jar 的区别：普通 jar 只含自己的 class；fat jar 把依赖也「打进去」，因此体积大但可独立运行。生产部署常用 fat jar，因为不需要服务器预装依赖。

## 跳过测试 {#skip-tests}

构建时跳过测试是高频需求，但两个参数有微妙区别：

```bash
mvn package -DskipTests        # 跳过「运行」测试，但仍编译测试代码
mvn package -Dmaven.test.skip=true   # 跳过测试的编译和运行
```

| 参数 | 编译测试代码 | 运行测试 |
|------|:---:|:---:|
| `-DskipTests` | ✓ | ✗ |
| `-Dmaven.test.skip=true` | ✗ | ✗ |

> [!WARNING]
> CI（持续集成）里**不要无条件跳过测试**，否则测试形同虚设。跳过测试只应用于本地快速验证、或明确的发布前临时构建。

## profile 多环境 {#profile}

不同环境（开发/测试/生产）配置不同，用 `<profiles>` 按需切换：

```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>development</env>
            <db.url>jdbc:mysql://localhost:3306/dev_db</db.url>
        </properties>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <env>production</env>
            <db.url>jdbc:mysql://prod-host:3306/prod_db</db.url>
        </properties>
    </profile>
</profiles>
```

激活方式：

```bash
mvn package -P prod                 # 命令行激活
mvn package -P prod,!dev            # 激活 prod、关闭 dev
```

也可在 `settings.xml` 里用 `<activeProfiles>` 设置默认激活，或用 `<activation>` 按 JDK 版本、系统属性等自动激活。

> [!NOTE]
> 属性占位符配合资源过滤，可把 `db.url` 这类值注入配置文件。需开启资源过滤：

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>  <!-- 开启 @xxx@ 占位符替换 -->
        </resource>
    </resources>
</build>
```

配置文件中用 `@db.url@`，构建时会被替换为对应 profile 的值。

## 常用内置属性 {#properties}

Maven 提供一批可直接引用的内置属性：

| 属性 | 含义 |
|------|------|
| `${project.version}` | 当前项目版本 |
| `${project.groupId}` | 当前 groupId |
| `${project.artifactId}` | 当前 artifactId |
| `${project.build.directory}` | 构建输出目录（默认 `target`） |
| `${basedir}` | 项目根目录 |
| `${maven.build.timestamp}` | 构建时间戳 |

自定义属性在 `<properties>` 里声明，如 `<java.version>17</java.version>`，后续用 `${java.version}` 引用。

## 离线与强制更新 {#offline}

```bash
mvn package -o          # 离线模式：只从本地仓库解析，不联网（依赖已缓存时很快）
mvn package -U          # 强制检查远程仓库是否有更新（解决 SNAPSHOT 不更新问题）
```

## 高频排坑清单 {#pitfalls}

### 1. 依赖下载失败 / 连不上仓库

```bash
# 检查是否配置了镜像；清理本地损坏缓存后重试
mvn -U clean package
```

本地仓库某 jar 损坏（如网络中断下载一半），会导致 `Could not resolve`。定位到对应 `~/.m2/repository/.../xxx` 目录删除后重新下载即可。

### 2. 类找不到 / NoSuchMethodError

通常是**依赖版本冲突**：运行时的版本和你编译时的版本不一致。用 `mvn dependency:tree` 定位冲突，显式声明正确版本。

### 3. 编译报「找不到符号」但 IDE 正常

通常是 IDE 用了与 Maven 不同的 JDK/依赖版本。执行 `mvn clean compile` 以 Maven 为准排查；检查 `maven-compiler-plugin` 的 `release` 配置。

### 4. 改了依赖不生效

SNAPSHOT 依赖缓存问题，用 `-U` 强制更新；或检查是否改错了 profile/scope。

### 5. 本地仓库膨胀

```bash
# 查看某个依赖为什么被引入
mvn dependency:tree -Dincludes=com.fasterxml.jackson.core

# 分析未使用/重复的依赖
mvn dependency:analyze
```

> [!TIP]
> 养成习惯：遇到任何依赖相关问题，第一反应是 `mvn dependency:tree` 看依赖树，而不是盲目猜测。它能直观展示「谁引入了什么、什么版本」。

## 小结 {#summary}

本章落地了 Maven 的实战技能：打可执行 fat jar（普通项目用 shade/assembly，Spring Boot 用官方插件）、跳过测试的两个参数区别、profile 多环境与资源过滤、内置属性、离线/强制更新，以及依赖冲突、类找不到等高频坑的排查思路。至此 Maven 教程五章结束，配合前面的坐标、依赖、生命周期、多模块，足以应对日常到工程化的绝大多数场景。
