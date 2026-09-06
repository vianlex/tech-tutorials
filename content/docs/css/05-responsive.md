---
title: 第五章：响应式与变量
linkTitle: 响应式与变量
description: 媒体查询、rem/vw 单位、CSS 变量、工程化最佳实践
weight: 181
---

# 响应式与变量

写完布局后，还要让页面**适配不同屏幕**，并让样式**可维护**。这一章讲响应式设计、CSS 单位和变量。

## 一、媒体查询（Media Query）

媒体查询根据**视口宽度、设备特性**等条件应用不同样式，是响应式的核心。

```css
/* 宽度 ≤ 768px 时生效 */
@media (max-width: 768px) {
  .nav {
    display: none;      /* 小屏隐藏导航 */
  }
}

/* 宽度 ≥ 1024px 时生效 */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
  }
}

/* 组合条件：768~1024 之间 */
@media (min-width: 768px) and (max-width: 1024px) { }
```

### 移动优先 vs 桌面优先

- **移动优先**：先写小屏样式，用 `min-width` 逐步增强。现代推荐做法。

```css
/* 移动优先：基础样式就是小屏 */
.box { width: 100%; }

@media (min-width: 768px) {
  .box { width: 50%; }   /* 平板两列 */
}

@media (min-width: 1024px) {
  .box { width: 25%; }   /* 桌面四列 */
}
```

- **桌面优先**：先写大屏，用 `max-width` 逐步降级。

### 常见断点

| 断点 | 设备 |
| --- | --- |
| 576px | 大屏手机 |
| 768px | 平板 |
| 992px | 小屏笔记本 |
| 1200px | 大屏桌面 |

> 断点应基于**内容**而非设备（内容在这个宽度下放不下就断），不要机械照搬。

### 其他媒体特性

```css
@media (orientation: landscape) { }   /* 横屏 */
@media (prefers-color-scheme: dark) { }   /* 深色模式 */
@media (prefers-reduced-motion: reduce) { }  /* 用户减少动画偏好 */
```

## 二、响应式单位

### 1. 相对字体单位 rem / em

- `em`：相对**父元素**字号，会逐级累乘，容易失控。
- `rem`：相对**根元素（`<html>`）字号**，默认 16px，全局统一，**响应式首选**。

```css
html { font-size: 16px; }
.box {
  width: 10rem;      /* 160px */
  font-size: 1.5rem; /* 24px */
}
```

配合媒体查询，改变根字号即可**整体缩放**：

```css
html { font-size: 16px; }
@media (max-width: 768px) {
  html { font-size: 14px; }   /* 小屏整体缩小 */
}
```

### 2. 视口单位 vw / vh / vmin / vmax

- `vw`：1% 视口宽度；`vh`：1% 视口高度。
- `vmin`：vw 和 vh 中较小者；`vmax`：较大者。

```css
.hero {
  height: 100vh;       /* 全屏高度 */
  font-size: 5vw;      /* 字体随视口缩放 */
}
```

> 移动端 `100vh` 会因地址栏遮挡出现滚动，可用 `100dvh`（动态视口高度）规避，现代浏览器已支持。

## 三、CSS 变量（自定义属性）

CSS 变量让颜色、间距等**值可复用、可统一修改**，是设计系统（design token）的基础。

### 声明与使用

```css
:root {
  --primary: #3b82f6;
  --gap: 16px;
  --radius: 8px;
}

.button {
  background: var(--primary);
  margin: var(--gap);
  border-radius: var(--radius);
}
```

### 特点

- **作用域**：定义在 `:root` 是全局，定义在某选择器内则只在该元素及其后代生效。
- **可设默认值**：`var(--color, #333)` 当 `--color` 未定义时用 `#333`。
- **可继承、可被 JS 动态改**：这是 CSS 变量相比预处理器变量的最大优势。

```javascript
// 动态切换主题色
document.documentElement.style.setProperty('--primary', '#ef4444');
```

### 实战：主题切换

```css
:root {
  --bg: #fff;
  --text: #222;
}
[data-theme="dark"] {
  --bg: #1a1a1a;
  --text: #eee;
}
body {
  background: var(--bg);
  color: var(--text);
}
```

```javascript
// 一行切换深色模式
document.documentElement.setAttribute('data-theme', 'dark');
```

## 四、工程化最佳实践

1. **全局 `box-sizing: border-box`**：几乎所有项目的第一行重置。
2. **用 CSS 变量统一设计 token**：颜色、间距、圆角、字体都抽成变量，改一处全站生效。
3. **移动优先 + 内容断点**：先写小屏，用 `min-width` 增强。
4. **`rem` 为主 + 视口单位辅助**：布局用 `rem`/`%`，全屏区块用 `vh`/`vw`。
5. **善用现代布局**：能用 Flex/Grid 就别再用 float 和绝对定位硬凑。
6. **统一命名规范**：如 BEM（Block__Element--Modifier），避免类名冲突。

```css
/* BEM 示例 */
.card { }               /* Block */
.card__title { }        /* Element */
.card--featured { }     /* Modifier */
```

## 小结

- 媒体查询是响应式核心，推荐**移动优先 + min-width**。
- `rem` 相对根字号、`vw/vh` 相对视口，是响应式主力单位。
- CSS 变量可复用、可继承、**可被 JS 动态修改**，是设计系统的基础。
- 工程化要点：全局 border-box、设计 token 变量化、移动优先、现代布局、BEM 命名。
