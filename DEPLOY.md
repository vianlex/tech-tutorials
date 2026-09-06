# Cloudflare Pages 部署指南

站点：技术学习博客 · 域名：`https://amias.icu/`

## 一、准备条件

- GitHub 账号
- Cloudflare 账号（已确认拥有）
- 域名 `amias.icu`（已在 Cloudflare 管理）

## 二、推送到 GitHub

1. 在 GitHub 创建新仓库，命名为 `learn-blog`（公开或私有均可）。
2. 修改 `hugo.yml` 中的 `github_repo`，把 `CHANGE-ME` 替换为你的 GitHub 用户名：
   ```yaml
   github_repo: https://github.com/你的用户名/learn-blog
   ```
3. 配置 git 身份并推送：
   ```bash
   git config --global user.name "你的名字"
   git config --global user.email "你的邮箱"
   git add -A
   git commit -m "init: learn-blog 技术学习博客"
   git remote add origin https://github.com/你的用户名/learn-blog.git
   git push -u origin main
   ```

## 三、Cloudflare Pages 配置（Git 集成，自动部署）

> 本仓库**统一使用 Cloudflare Git 集成自动部署**，不再使用 GitHub Actions。

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 左侧选择 **Workers & Pages → `tech-tutorials` 项目 → Settings → Build & deployments**。
3. 确认已通过 **Connect to Git** 连接 GitHub 仓库 `vianlex/tech-tutorials`。
4. 构建配置：
   - **Build command**：`hugo --gc --minify`
   - **Build output directory**：`public`
   - **环境变量（关键）**：`HUGO_VERSION` = `0.165.0`

> [!IMPORTANT]
> 必须显式设置 `HUGO_VERSION=0.165.0` 环境变量。Cloudflare 默认用的是旧版 Hugo（0.147.7），而 `docs-theme` 主题要求 Hugo ≥ 0.160.1，旧版会报 `failed to load translations: unsupported file format bool` 导致构建失败。

5. 推送 `main` 分支，Cloudflare 会自动拉取并构建部署。

## 四、绑定自定义域名 `amias.icu`

1. 在 Cloudflare Pages 项目 → **Custom domains** → **Set up a custom domain**。
2. 输入 `amias.icu`（或 `www.amias.icu`）。
3. 若域名已在 Cloudflare 托管，DNS 记录会自动添加；否则按提示到域名注册商处添加 CNAME 记录指向 `<项目名>.pages.dev`。
4. 等待 SSL 证书签发（通常几分钟）。

## 五、验证

- 访问 `https://amias.icu/` 确认首页正常。
- 检查教程页面、搜索、深色模式、语言切换是否正常。
- 修改任意文档 push 后，确认自动部署生效。

## 附：本地预览

```bash
hugo server --bind 127.0.0.1 --port 1313
```
