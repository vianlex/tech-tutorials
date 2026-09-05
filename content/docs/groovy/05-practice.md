---
title: 第五章 实战应用
linkTitle: 实战应用
description: Grape 依赖、文件 IO、脚本嵌入、Gradle/Jenkins 高频场景与 Spock 测试
weight: 85
---

# 实战应用

## Grape 依赖管理 {#grape}

Grape 让你在单个脚本里声明第三方依赖，无需构建工具：

```groovy
@Grab('org.apache.commons:commons-lang3:3.14.0')
import org.apache.commons.lang3.StringUtils

println StringUtils.capitalize("hello")    // Hello

// 指定仓库（默认 Maven Central）
@GrabResolver(name='restlet', root='https://maven.restlet.com')
@Grab('org.restlet:org.restlet:2.4.3')
import org.restlet.*

// 多个依赖与排除
@Grab('com.google.code.gson:gson:2.10.1')
@GrabExclude('org.apache.httpcomponents:httpclient')
```

运行：`groovy script.groovy`，Grape 会自动下载并加入 classpath。

**Grape 的坑（生产环境务必注意）**：

- **需要 `systemClassLoader=true` 的场景**：某些库（如 JDBC 驱动、需要放进系统 classpath 的 SPI 实现）必须加 `@GrabConfig(systemClassLoader=true)`，否则 `Class.forName` / `ServiceLoader` 找不到类：

```groovy
@GrabConfig(systemClassLoader=true)
@Grab('org.postgresql:postgresql:42.7.3')
import java.sql.DriverManager
```

- **离线模式**：CI/离线环境首次运行会联网下载；可用 `groovy -Dgrape.offline=true` 强制走本地缓存（`~/.groovy/grapes`），或提前 `go offline`。
- **依赖版本冲突**：Grape 按"先声明先得"解析，两个 `@Grab` 传递依赖同一库的不同版本时容易 `NoSuchMethodError`；脚本里难以精细控制，复杂依赖请用 Gradle 打 **fat jar**。
- **生产环境不推荐**：Grape 会把依赖下载到用户目录、运行时才解析，且无法锁定可复现构建。真实服务/工具**应改用 Gradle 打 fat jar**（用 `shadow` 插件）分发，而非依赖 `@Grab` 脚本。

## 编写脚本 {#script}

Groovy 脚本拥有隐式 `args`、`binding` 与可直接执行的语句：

```groovy
// analyze.groovy —— 统计文本文件词频
def file = args[0]                       // 命令行参数
def counts = [:]                        // 注意：这里没写 def 的 counts 会进 binding

new File(file).eachLine { line ->
    line.split(/\s+/).each { w ->
        if (w) counts[w] = (counts[w] ?: 0) + 1
    }
}

counts.sort { -it.value }.take(10).each {
    println "$it.key: $it.value"
}
```

运行：`groovy analyze.groovy data.txt`。脚本中未声明为 `def` 的变量会进入 `binding`，可在 `groovyShell` 中跨脚本共享——这也意味着**脚本里误漏 `def` 会污染 binding**，建议脚本顶层变量都显式加 `def`。

## 脚本与类混用 {#script-class}

```groovy
// 脚本顶层代码可直接引用同文件中的类
class WordCounter {
    static def count(List words) {
        words.groupBy { it }.collectEntries { k, v -> [(k): v.size()] }
    }
}

def result = WordCounter.count(["a", "b", "a"])
println result        // [a:2, b:1]
```

补充：Groovy 脚本在编译后其实是一个继承 `groovy.lang.Script` 的类，顶层语句在 `run()` 方法里执行，所以用 `static` 方法或独立类来组织逻辑，比把所有代码堆在顶层更清晰、更易测试。

## 文件与 IO 常用写法 {#io}

Groovy 大幅简化了 Java 的 IO 样板：

```groovy
// 逐行读取
new File('data.txt').eachLine { line ->
    println line
}

// 一次性读全部文本（小文件）
def text = new File('data.txt').text

// 写文件（自动刷新/关闭）
new File('out.txt').withWriter { w -> w << "hello\n" }

// << 追加文本（其实就是 leftShift，自动创建/追加）
new File('log.txt') << "一行日志\n"

// 递归遍历目录
new File('src').eachFileRecurse { f ->
    if (f.isFile()) println f.name
}

// 读取网页（URL 直接 .text）
def page = new URL('https://example.com').text
println page.size()
```

坑点：

- `.text` 会把**整个文件读进内存**，大文件要用 `eachLine` 或 `withReader` 流式处理，否则 OOM。
- `new URL(...).text` 方便但**无超时、无重试**，生产代码应改用带超时设置的 `HttpURLConnection` 或 `HttpClient`/`OkHttp`。
- `withWriter`/`withReader`/`withStream` 会自动 `close()`，优先用它们代替手动 `new` + `close`。

## 在 Java 应用中嵌入 Groovy {#embed}

把 Groovy 作为"可热更新的脚本引擎"嵌进 Java 应用，是 Groovy 的独特价值：

```groovy
// GroovyShell：执行字符串/脚本
def shell = new GroovyShell()
def result = shell.evaluate('3 + 4 * 2')      // 11
shell.setVariable('name', 'Alice')
println shell.evaluate('"Hi, $name"')          // Hi, Alice

// GroovyClassLoader：加载 .groovy 源文件为 Class
def gcl = new GroovyClassLoader()
def clazz = gcl.parseClass(new File('Plugin.groovy'))
def plugin = clazz.newInstance()
plugin.run()

// GroovyScriptEngine：从目录/URL 加载，支持热更新
def engine = new GroovyScriptEngine(['file:///path/to/scripts/'] as String[])
def binding = new Binding()
engine.run('reloadable.groovy', binding)       // 文件改动后自动重新加载
```

注意点：

- 频繁用 `GroovyShell.evaluate` 解析同一条脚本会**重复编译**，应缓存 `Script` 实例或编译成 `Class` 复用。
- `GroovyClassLoader` 每次 `parseClass` 会生成新的 `ClassLoader`，旧类不会被 GC（类元数据泄漏）——长期热部署应周期性丢弃旧 `GroovyClassLoader`，或用 `GroovyScriptEngine` 管理。这是嵌入 Groovy 最常见的内存泄漏来源。

## Gradle 构建脚本 {#gradle}

Gradle 的 `build.gradle` 即 Groovy DSL 脚本：

```groovy
plugins {
    id 'java'
    id 'application'
}

repositories {
    mavenCentral()        // 依赖仓库
}

dependencies {
    implementation 'com.google.guava:guava:32.1.3-jre'
    testImplementation 'junit:junit:4.13.2'
}

application {
    mainClass = 'com.demo.App'
}

tasks.register('greet') {
    doLast {
        println "Hello from Gradle + Groovy DSL"
    }
}
```

常用命令：`gradle build`、`gradle run`、`gradle greet`。

**Gradle 里的 Groovy 语法糖（深入）**：

- `dependencies { ... }`、`repositories { ... }` 都是**闭包委托**：花括号里的代码在对应容器的 delegate 上下文中执行，所以 `implementation 'x'` 实际是容器的方法调用。
- **省略括号**是常态：`id 'java'` 等价于 `id('java')`；方法调用在参数紧跟闭包时可省括号，如 `tasks.register('greet') { ... }`。
- **`ext` 扩展属性**：在 `build.gradle` 里定义可跨项目/任务共享的变量：

```groovy
ext {
    appVersion = '1.2.3'
}
println project.appVersion

// gradle.properties 里也能定义，自动成为 project 属性
// version=1.2.3  ->  project.version
```

- **Groovy DSL vs Kotlin DSL 的选择**：Kotlin DSL（`build.gradle.kts`）类型安全、IDE 补全更好，但语法更啰嗦；Groovy DSL 灵活、可读性强、生态成熟。新项目偏向 Kotlin DSL，但**理解 Groovy DSL 仍是读存量 Gradle 项目的硬需求**（大量现有项目仍是 `.gradle`）。
- 坑：`build.gradle` 里 `def` 声明的变量**只在该脚本作用域**，不会成为 `project` 属性；要跨脚本/子项目共享必须用 `ext` 或 `gradle.properties`。

## Jenkins Pipeline {#jenkins}

`Jenkinsfile` 用 Groovy 描述声明式流水线：

```groovy
pipeline {
    agent any                       // 任意可用节点执行
    environment {
        REPO = 'my-app'            // 流水线级环境变量
    }
    stages {
        stage('构建') {
            steps {
                sh 'gradle build'   // 执行 Shell 命令
                echo "构建完成：${REPO}"
            }
        }
        stage('测试') {
            steps {
                sh 'gradle test'
                junit 'build/test-results/**/*.xml'
            }
        }
        stage('部署') {
            steps {
                script {
                    def env = 'prod'
                    echo "部署到 ${env}"
                }
            }
        }
    }
    post {
        always {
            echo '流水线结束'
        }
    }
}
```

**声明式 vs 脚本式流水线**：

- **声明式**（上述 `pipeline { }`）：结构固定、可读性好、官方推荐，复杂逻辑用 `script { }` 块写 Groovy。
- **脚本式**（老式 `node { }` + 原生 Groovy 流程控制）：灵活但难维护，逐渐边缘化。

**Jenkins Pipeline 的 Groovy 沙箱限制（极重要的坑）**：

Jenkins Pipeline 运行在 **Groovy 沙箱（sandbox）** 中，并非完整的 Groovy 环境：

- **不能用 `@Grab`**：Jenkins 不通过 Grape 解析依赖，需要的功能要靠插件/Jenkins 自带类库。
- **部分反射、`System.exit`、修改 `metaClass` 等被禁止**：沙箱会拦截高危调用，未授权的方法会抛 `RejectedAccessException`。
- **需要管理员审批**：非沙箱模式（关闭 sandbox）运行任意 Groovy 需管理员在 "Script Approval" 中逐条批准，存在安全风险。
- **不是标准 Groovy 语义**：`@CompileStatic`、某些动态特性、复杂的 MOP 在 Pipeline 里不可靠；写 Jenkinsfile 应坚持"简单、声明式、少用魔法"。
- 环境变量用 `env.MY_VAR`（写入 `env.MY_VAR = 'x'`），`credentials` 步骤安全注入密钥，避免把密码硬编码进脚本。

```groovy
// 正确使用环境变量与凭据
pipeline {
    agent any
    environment {
        TOKEN = credentials('my-token-id')   // 从 Jenkins 凭据系统注入
    }
    stages {
        stage('发布') {
            steps {
                sh 'curl -H "Token: $TOKEN" https://api.example.com/deploy'
            }
        }
    }
}
```

## Spock 测试框架 {#spock}

Spock 是 Groovy 生态里**最流行**的测试框架，用 `given/when/then` 块组织用例，可读性极高（类似 BDD）：

```groovy
import spock.lang.*

class CalculatorSpec extends Specification {
    def "加法应该返回两数之和"() {
        given: "准备一个计算器"
        def calc = new Calculator()

        when: "调用 add"
        def result = calc.add(2, 3)

        then: "结果应为 5"
        result == 5
    }

    // 数据驱动测试：where 块提供多组参数
    def "两数相加的数据表"() {
        expect:
        new Calculator().add(a, b) == sum

        where:
        a | b || sum
        1 | 2 || 3
        0 | 0 || 0
        -1 | 1 || 0
    }
}
```

要点：

- Spock 基于 JUnit Runner，**Groovy 编写、运行在 JVM**，可与 Java 项目共存；Maven/Gradle 引入 `org.spockframework:spock-core` 即可。
- `given/when/then/and/expect/where` 是标签化的文档化测试；`where` 块做数据驱动，避免写 N 个重复用例。
- 断言用 Groovy 的 `==`（即 `equals`），失败信息自动展示期望值/实际值，比 JUnit `assertEquals` 友好太多。
- 它是 Groovy 开发**必知**的框架：大量 Gradle/Jenkins 相关的代码质量、验收测试都用 Spock 写。

## 小结 {#summary}

Groovy 在真实工程里是"粘合层"与"脚本层"的多面手：Grape 适合一次性脚本但生产应改 Gradle fat jar，文件 IO 与脚本嵌入让自动化触手可及，而 Gradle DSL、Jenkins Pipeline（务必避开沙箱限制）、Spock 测试则是日常开发绕不开的高频场景。至此 Groovy 教程完结——建议从一个真实的 Gradle 项目 + Jenkinsfile + Spock 测试动手实践，把这些特性真正用起来。
