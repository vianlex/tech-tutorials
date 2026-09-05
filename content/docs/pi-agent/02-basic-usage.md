---
title: 第二章 基本使用
linkTitle: 基本使用
description: Pi Agent 的 TUI 交互、快捷键、斜杠命令与会话管理
weight: 62
---

# 基本使用

## 交互模式与对话 {#interactive}

不带参数运行即进入交互式 TUI，直接输入自然语言指令：

```bash
# 交互模式（默认）
pi

# 直接把指令作为命令行参数
pi "帮我重构 src/utils.ts 中的 formatDate 函数"

# 读取管道 stdin（结合 -p 打印模式）
cat error.log | pi -p "解释这个错误并给出修复建议"
```

非交互 / 打印模式：

```bash
# -p / --print：回复后退出，不进入 TUI
pi -p "用一句话描述什么是闭包"

# 临时模式：不保存会话
pi --no-session "列出当前目录的 Go 文件"
```

## TUI 与快捷键 {#shortcuts}

编辑与导航常用快捷键：

```text
Enter          发送消息
Shift+Enter    换行（Ctrl+Enter 于 WSL）
Ctrl+W         向后删除一个单词
Ctrl+U         删除到行首
Ctrl+K         删除到行尾
Ctrl+A / Home  行首
Ctrl+E / End   行尾
↑              空行时浏览历史
Esc            取消补全 / 中止输出流
Ctrl+C         清空编辑器（再次按下退出）
Ctrl+G         调用外部编辑器（$VISUAL/$EDITOR）
```

模型与显示切换：

```text
Ctrl+P         循环模型（受 --models 约束）
Ctrl+O         展开 / 收起工具输出
Ctrl+T         切换思考块（thinking）可见性
Shift+Tab      循环思考级别
```

## 斜杠命令 {#slash}

在编辑器中输入 `/` 触发斜杠命令：

```text
/model        切换模型（模糊搜索，方向键 + Enter 选择）
/thinking     调整推理模型的思考级别：off/minimal/low/medium/high
/queue        设置消息队列模式：one-at-a-time（默认）/ all-at-once
/session      显示会话信息：路径、消息数、token、成本
/clear        清空上下文，开始全新会话
/copy         复制上一条 Agent 消息到剪贴板
/compact      手动压缩上下文（可带自定义指令）
/autocompact  开关自动压缩
/theme        选择配色主题
/export       将会话导出为自包含 HTML
/resume       浏览并切换到其他历史会话
/new          开始新会话
/name         设置当前会话的显示名
/tree         跳转到会话树的任意节点继续（支持搜索、分支、打标签）
/fork         从当前分支的某条消息创建新会话文件
/clone        将当前分支复制为新会话文件
/login        OAuth 登录订阅制模型
/logout       清除 OAuth 令牌
/reload       重新加载扩展、技能、提示、主题与上下文文件
/trust        保存项目信任决策（写入 trust.json，需重启生效）
```

## 文件引用与 Bash 模式 {#files-bash}

在对话中引用项目文件与执行命令：

```text
# 输入 @ 模糊搜索项目文件（遵循 .gitignore）
@src/server.ts 这个文件有性能问题吗？

# 以 ! 前缀直接执行 bash
!git status

# 拖拽文件到终端即可附加；多行粘贴自动折叠为 [paste #N lines]
```

命令行中也能用 `@` 把文件纳入消息：

```bash
# 让 Agent 基于 prompt.md 回答
pi @prompt.md "按这个模板生成代码"

# 附带图片（支持视觉模型）
pi -p @screenshot.png "图里是什么错误？"
```

## 会话管理 {#sessions}

会话默认以 JSONL 树状结构保存在 `~/.pi/agent/sessions/`（按工作目录组织）。

启动时的会话选项：

```bash
pi -c            # --continue：继续最近会话
pi -r            # --resume：浏览历史会话并选择
pi --session <id>   # 使用指定会话文件或 ID（支持部分 UUID）
pi --fork <id>      # 从指定会话 fork 出新会话
pi --name "重构登录" # -n：启动时命名会话
pi --session-dir ./sessions  # 自定义会话存储目录
```

交互模式中的分支与导出：

```text
/tree     在会话树中就地导航，回到任意历史节点继续
/fork     从某条用户消息派生新会话文件（保留原分支）
/clone    复制当前分支为新会话
/export my-session.html   导出为 HTML
/import session.jsonl     从 JSONL 导入恢复
/share    上传为私有 GitHub gist 并生成可分享链接
```

> 压缩是有损的，但完整历史保留在 JSONL 中，可用 `/tree` 随时回顾。

## 小结 {#summary}

通过快捷键、斜杠命令与 `@`/`!` 引用，Pi Agent 在终端里即可完成对话、命令执行与分支会话管理。下一章深入模型选择与 `settings.json` 配置。
