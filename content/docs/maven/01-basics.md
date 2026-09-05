---
title: 第一章 基础与坐标
linkTitle: 基础与坐标
description: Maven 安装配置、标准目录约定、GAV 坐标三要素、仓库类型与 settings.xml 配置
weight: 86
---

# 基础与坐标

Maven 的核心思想是「**约定优于配置**」：只要按约定放置代码、声明坐标，Maven 就能自动完成编译、测试、打包、发布。先理解它最基本的几个概念，后面的依赖与生命周期才谈得上。

## 为什么需要 Maven {#why-maven}

在 Maven 出现前，Java 项目依赖管理靠「手动下载 jar 包放进 lib 目录」，构建靠 Ant 脚本，每个项目结构五花八门。这带来三大痛点：

1. **依赖混乱**：jar 版本冲突、传递依赖无从追踪、少一个包运行时才报 `ClassNotFoundException`。
2. **构建不统一**：每个团队一套 Ant 脚本，新人上手成本高。
3. **结构各异**：源码目录、测试目录没有规范，工具链难以复用。

Maven 用「统一的目录结构 + 声明式 POM + 约定好的生命周期」一次性解决了这些问题。

## 安装与验证 {#install}

Maven 依赖 JDK。安装后验证：

```bash
mvn -v
# Apache Maven 3.9.x
# Java version: 17.x, vendor: ...
# OS name: windows 11, arch: amd64
```

> [!NOTE]
> Maven 3.9+ 需要 JDK 8 以上；Maven 3.9 要求 Java 8，Maven 4.x 要求 Java 17。构建时的编译目标由 `<maven.compiler.source/target>` 或 `maven-compiler-plugin` 的 release 控制，与运行 Maven 本身的 JDK 版本无关。

## 标准目录约定 {#directory-convention}

Maven 约定了一套固定目录结构，这是「约定优于配置」最直观的体现：

```text
my-project/
├── pom.xml                 # 项目描述文件（核心）
└── src/
    ├── main/
    │   ├── java/           # 主代码（默认源目录）
    │   └── resources/      # 主资源（配置文件等，打包进 classpath）
    └── test/
        ├── java/           # 测试代码
        └── resources/      # 测试资源
```

> [!TIP]
> 只要遵守这套目录，Maven 无需任何配置就能找到源码与资源。这也是为什么打开一个 Maven 项目，往往能立刻猜到它是什么结构。

## POM 与 GAV 坐标 {#gav}

每个项目根目录的 `pom.xml` 是 Maven 的「说明书」。其中最重要的三要素构成项目的唯一坐标 **GAV**：

| 坐标 | 含义 | 示例 |
|------|------|------|
| **groupId** | 组织/团队标识（常用反域名） | `com.example` |
| **artifactId** | 项目/模块名 | `order-service` |
| **version** | 版本号 | `1.0.0` |

最小 `pom.xml`：

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>order-service</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
</project>
```

> [!NOTE]
> GAV 三要素在 Maven 仓库中确定了一个 jar 的**唯一位置**，等价于「命名空间：项目名：版本」。依赖某库、或发布自己的库，本质都是在引用/声明这套坐标。

### 版本号规范 {#version}

- 发布版：`1.0.0`（三段式，主.次.修订）
- 快照版：`1.0.0-SNAPSHOT`（开发中，每次构建可覆盖，用于团队内部迭代）

> [!WARNING]
> 正式环境**不要依赖 SNAPSHOT**：它不稳定、可被覆盖、且 Maven 会频繁检查远程仓库，导致构建变慢且结果不可复现。发布时要把版本改为正式版。

## 仓库（Repository） {#repository}

Maven 从「仓库」下载依赖、也向仓库发布产物。仓库分三类：

| 类型 | 说明 |
|------|------|
| **本地仓库** | 本机缓存，默认 `~/.m2/repository` |
| **远程（中央）仓库** | Maven Central（`repo.maven.apache.org`），默认从这里拉依赖 |
| **私服/镜像** | 公司内网 Nexus/Artifactory，或阿里云等镜像 |

依赖解析顺序：**本地仓库 → 私服/镜像 → 中央仓库**。找到即停，并缓存到本地。

```mermaid
flowchart LR
    A["pom.xml 声明依赖"] --> B{"本地仓库有？"}
    B -->|"有"| C["直接用"]
    B -->|"无"| D{"私服/镜像有？"}
    D -->|"有"| E["下载并缓存到本地"]
    D -->|"无"| F["中央仓库下载"]
    F --> E
    E --> C
```

## settings.xml 配置 {#settings}

Maven 有两份配置：项目级 `pom.xml`（随项目走），用户级 `settings.xml`（本机环境，默认 `~/.m2/settings.xml`）。后者主要配**镜像、私服认证、本地仓库路径、profile**。

### 配置国内镜像（加速） {#mirror}

中央仓库在国外，国内开发常配阿里云镜像：

```xml
<settings>
    <mirrors>
        <mirror>
            <id>aliyun</id>
            <name>Aliyun Maven</name>
            <url>https://maven.aliyun.com/repository/public</url>
            <mirrorOf>central</mirrorOf>   <!-- 拦截所有对 central 的请求 -->
        </mirror>
    </mirrors>
</settings>
```

### 配置私服认证 {#server}

发布到私服需要账号密码，放在 `settings.xml`（不随项目提交，避免泄露）：

```xml
<settings>
    <servers>
        <server>
            <id>my-nexus</id>              <!-- 对应 pom 里 distributionManagement 的 id -->
            <username>deployer</username>
            <password>***</password>
        </server>
    </servers>
</settings>
```

### 自定义本地仓库路径 {#local-repository}

```xml
<settings>
    <localRepository>D:/maven-repo</localRepository>
</settings>
```

> [!TIP]
> `settings.xml` 里放「环境相关」的敏感配置（账号、镜像、本地路径），`pom.xml` 放「项目相关」的声明。这个边界清晰，才能安全地开源项目而不泄露密码。

## 小结 {#summary}

本章建立了 Maven 的心智模型：统一目录结构是「约定」，GAV 坐标是「唯一标识」，仓库体系是「依赖与产物的存储与流转」。理解这三个基础概念后，下一章进入 Maven 最核心的价值——依赖管理。
