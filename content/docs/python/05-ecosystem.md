---
title: 第五章 标准库与常用生态
linkTitle: 标准库与生态
description: Python 常用标准库与主流第三方库
weight: 45
---

# 标准库与常用生态

## 常用标准库 {#stdlib}

```python
import os            # 操作系统接口
import sys           # 系统参数
import json          # JSON 处理
import re            # 正则表达式
import datetime      # 日期时间
import pathlib       # 路径操作（现代推荐）
import collections   # 高级容器
import itertools     # 迭代工具
import functools     # 函数工具
```

### 常用示例 {#examples}

```python
# JSON
data = {"name": "Alice", "age": 25}
text = json.dumps(data)          # 序列化
obj = json.loads(text)           # 反序列化

# 日期时间
from datetime import datetime
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))

# pathlib 路径操作
from pathlib import Path
p = Path("data") / "file.txt"    # 拼接路径
p.exists()                        # 是否存在
p.read_text(encoding="utf-8")     # 读文本
```

## 虚拟环境 {#venv}

隔离项目依赖是 Python 工程实践的基础：

```bash
# 创建虚拟环境
python -m venv venv

# 激活（Windows）
venv\Scripts\activate
# 激活（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install requests

# 导出依赖
pip freeze > requirements.txt

# 从文件安装
pip install -r requirements.txt
```

## 主流第三方库 {#third-party}

| 领域 | 库 | 说明 |
|------|-----|------|
| Web 框架 | Django / Flask / FastAPI | 从重量级到轻量级 |
| 数据分析 | pandas / numpy | 数据表与数值计算 |
| 可视化 | matplotlib / seaborn | 图表绘制 |
| 机器学习 | scikit-learn / PyTorch | 传统 ML 与深度学习 |
| 网络请求 | requests | 简洁的 HTTP 客户端 |
| 爬虫 | beautifulsoup4 / scrapy | 网页解析与爬取 |
| 自动化 | selenium / playwright | 浏览器自动化 |

### requests 示例 {#requests}

```python
import requests

resp = requests.get("https://api.example.com/users")
if resp.status_code == 200:
    users = resp.json()
    for u in users:
        print(u["name"])
```

## 小结 {#summary}

Python 生态庞大，标准库已覆盖大量需求，第三方库则提供了从 Web 到 AI 的全栈能力。至此 Python 教程完成，建议动手实践。
