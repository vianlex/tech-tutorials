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

## 三、Cloudflare Pages 配置（二选一）

### 方式 A：Git 集成（推荐，自动部署）

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 左侧选择 **Workers & Pages → Create → Pages → Connect to Git**。
3. 授权 GitHub，选择 `learn-blog` 仓库。
4. 构建配置：
   - **Framework preset**：Hugo
   - **Build command**：`hugo --gc --minify`
   - **Build output directory**：`public`
   - **环境变量**：`HUGO_VERSION` = `0.165.0`
5. 点击 **Save and Deploy**，等待首次构建完成。

> 用 Git 集成方式时，`.github/workflows/cloudflare-pages.yaml` 可删除（避免重复部署）。

### 方式 B：GitHub Actions + Wrangler Direct Upload

1. 在 Cloudflare 获取凭据：
   - **Account ID**：Dashboard 首页右侧，或 `workers.dev` 子域设置页。
   - **API Token**：My Profile → API Tokens → Create Token → 选「Cloudflare Pages: Edit」模板。
2. 在 GitHub 仓库 **Settings → Secrets and variables → Actions** 添加两个 secret：
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_API_TOKEN`
3. 推送 `main` 分支，workflow 会自动构建并部署。

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
