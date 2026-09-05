# 技术学习博客 (tech-tutorials)

基于 Hugo + [OINK 主题](https://github.com/pgsty/oink) 搭建的个人技术教程站点，部署在 Cloudflare Pages。

- **线上地址**：https://amias.icu/
- **仓库地址**：https://github.com/vianlex/tech-tutorials

## 内容

Spring、JavaScript、Golang、Python 从入门到进阶的教程与笔记，每套教程含 5 个章节。

```
content/
├── _index.md          # 首页
├── docs/              # 教程
│   ├── spring/
│   ├── javascript/
│   ├── golang/
│   └── python/
└── blog/              # 博客文章
```

## 技术栈

| 组件 | 说明 |
| --- | --- |
| [Hugo](https://gohugo.io/) | 静态站点生成器（v0.158+） |
| [OINK](https://github.com/pgsty/oink) | Hugo 文档主题（Docsy 分叉，v1.0.0，离线归档方式安装在 `themes/oink/`） |
| Cloudflare Pages | 托管与 CDN |
| GitHub Actions | 推送 main 分支自动部署（wrangler Direct Upload） |

## 本地开发

需要安装 [Hugo Extended](https://gohugo.io/installation/)（v0.158+）。

```bash
# 启动开发服务器
hugo server --bind 127.0.0.1 --port 1313

# 访问 http://127.0.0.1:1313
```

```bash
# 构建生产版本
hugo --gc --minify --printPathWarnings --panicOnWarning
```

构建产物输出到 `public/` 目录。

## 部署

推送到 `main` 分支即通过 GitHub Actions 自动部署到 Cloudflare Pages。首次配置（Cloudflare 项目、API Token、Secrets 等）详见 [DEPLOY.md](DEPLOY.md)。

## 写作约定

- 内容放在 `content/docs/<教程名>/` 下，每章一个 Markdown 文件
- 章节文件使用 front matter 的 `weight` 控制排序
- 站点配置集中在 `hugo.yml`（语言、菜单、主题参数等）
- 主题支持 `steps` / `cards` 等原生 Markdown 组件，用法参见 OINK 主题文档

## License

内容版权归作者所有，转载请注明出处。
