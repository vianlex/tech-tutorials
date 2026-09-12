---
title: DeepSeek Harness 使用教程
linkTitle: DeepSeek Harness
description: DeepSeek Harness 开源 Agent 框架从入门、插件开发到多用户服务化部署的完整教程
weight: 130
---

# DeepSeek Harness 使用教程

DeepSeek Harness（简称 **dsh**）是 DeepSeek 开源的 Agent 框架，核心公式 **Agent = Model + Harness**：模型是可替换的部件，Harness 负责工具注册、任务规划、沙箱与会话存储等模型之外的一切。它构建在 Cordis 元框架之上，slogan「一切皆插件」——模型适配器、工具集、沙箱、agent 循环本身都是可热插拔的插件。

## 章节 {.cards}

- [第一章：简介与安装](/docs/deepseek-harness/01-intro-install/) — 是什么、核心公式、与成品编码工具的区别、三种安装方式与版本验证
- [第二章：快速上手](/docs/deepseek-harness/02-getting-started/) — 启动 Web UI、配置模型 API Key、选择 workspace、第一个会话与四种模式
- [第三章：核心概念](/docs/deepseek-harness/03-core-concepts/) — plugin/profile/bundle/patch、配置层叠顺序、--dump-config 与 DSH_HOME
- [第四章：插件开发入门](/docs/deepseek-harness/04-plugin-dev/) — apply(ctx)/inject/ctx.effect、三种写法、defineTool 工具与加载三步闭环
- [第五章：进阶与最佳实践](/docs/deepseek-harness/05-advanced/) — PTC 模式、Python SDK、自定义 agent preset、headless 批处理与实践建议
- [第六章：多用户部署与密码认证](/docs/deepseek-harness/06-multiuser-deploy/) — 四个安全硬约束、认证与隔离的分层设计、四条基础路线加一条 SSO 叠加层、认证网关核心实现与每用户独立实例的落地命令
- [第七章：租户隔离与规模化加固](/docs/deepseek-harness/07-isolation-and-scaling/) — 回环租户隔离的陷阱与 O(n) 实现、容器化两种形态的坑、千用户规模选型与容量规划、按需启停策略
