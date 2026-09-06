---
title: Docker 使用教程
linkTitle: Docker 教程
description: Docker 容器化技术从入门到集群编排的完整教程，覆盖常用命令、镜像导入导出、网络模式原理与 Swarm 集群
weight: 30
---

# Docker 使用教程

Docker 是当下最主流的**容器化运行时**，它把应用及其依赖打包到标准化的「镜像」中，让「一次构建、到处运行」真正成为可能。本教程从概念讲起，覆盖日常命令、镜像构建与迁移、数据卷与网络原理，最后到 Docker Swarm 集群编排。

## 章节 {.cards}

- [第一章：Docker 概述与安装](/docs/docker/01-install-basics/) — 容器 vs 虚拟机、镜像与容器关系、Docker 引擎架构、各平台安装
- [第二章：容器与镜像常用命令](/docs/docker/02-container-commands/) — 生命周期命令、exec/cp/logs/stats、资源限制、清理与速查
- [第三章：镜像构建与导入导出](/docs/docker/03-images-import-export/) — Dockerfile 详解、commit、import/export、save/load、registry 推送、镜像瘦身
- [第四章：数据卷与 Docker 网络原理](/docs/docker/04-network/) — 卷与 bind mount、CNM 架构、bridge/host/none/container/overlay/macvlan 六种模式、DNS
- [第五章：Docker Compose 多服务编排](/docs/docker/05-compose/) — compose.yaml 详解、健康检查、网络与卷、env_file、profile
- [第六章：Docker Swarm 集群编排](/docs/docker/06-swarm/) — Swarm 架构、初始化集群、service/scale/rolling update、stack 部署、与 K8s 选型

## 学习路线建议

- **快速上手**：1 → 2 → 3 → 5（个人开发、小团队够用）
- **深入原理**：加 4（理解网络才能排查连接问题）
- **集群运维**：加 6（多机部署、滚动更新）
