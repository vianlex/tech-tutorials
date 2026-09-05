---
title: 第五章 实战应用
linkTitle: 实战应用
description: Grape 依赖、脚本、Gradle 构建与 Jenkins Pipeline
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

## 编写脚本 {#script}

Groovy 脚本拥有隐式 `args`、`binding` 与可直接执行的语句：

```groovy
// analyze.groovy —— 统计文本文件词频
def file = args[0]                       // 命令行参数
def counts = [:]

new File(file).eachLine { line ->
    line.split(/\s+/).each { w ->
        if (w) counts[w] = (counts[w] ?: 0) + 1
    }
}

counts.sort { -it.value }.take(10).each {
    println "$it.key: $it.value"
}
```

运行：`groovy analyze.groovy data.txt`。脚本中未声明为 `def` 的变量会进入 `binding`，可在 `groovyShell` 中跨脚本共享。

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

## Jenkins Pipeline {#jenkins}

`Jenkinsfile` 用 Groovy 描述声明式流水线：

```groovy
pipeline {
    agent any                       // 任意可用节点执行
    stages {
        stage('构建') {
            steps {
                sh 'gradle build'   // 执行 Shell 命令
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
                // script 块可写任意 Groovy 逻辑
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

## 脚本化流水线 {#scripted}

老式脚本化流水线直接写 Groovy 流程控制：

```groovy
node {
    stage('检出') {
        checkout scm
    }
    stage('打包') {
        if (env.BRANCH_NAME == 'main') {
            sh 'gradle build'
        } else {
            echo '非主干分支，跳过构建'
        }
    }
}
```

## 小结 {#summary}

凭借 Grape 的即开即用依赖、简洁的脚本能力，以及作为 Gradle 与 Jenkins Pipeline 的支撑语言，Groovy 在构建与自动化领域不可替代。至此 Groovy 教程完结，建议从一个真实的 Gradle 项目或 Jenkinsfile 动手实践。
