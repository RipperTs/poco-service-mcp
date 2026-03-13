# HTML 报告规范

## 目录
- [设计系统](#design)
- [布局结构](#layout)
- [图表规范](#charts)
- [组件规范](#components)
- [单日报告章节结构](#single-day-sections)
- [数据可用性规则](#data-rules)

---

## 设计系统 {#design}

```css
--primary: #3b82f6;
--primary-dark: #1d4ed8;
--success: #10b981;
--warning: #f59e0b;
--danger: #ef4444;
--purple: #7c3aed;
--bg-page: #f1f5f9;
--bg-card: #ffffff;
--bg-sidebar: #1e293b;
--text-primary: #0f172a;
--text-secondary: #64748b;
--border: #e2e8f0;
--shadow: 0 1px 3px rgba(0,0,0,.1), 0 1px 2px rgba(0,0,0,.06);
--shadow-md: 0 4px 6px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.06);
```

**分类徽章颜色：**
```
Positive → bg:#dcfce7  color:#166534  border:#bbf7d0
Alert    → bg:#fef9c3  color:#854d0e  border:#fde68a
Risk     → bg:#fee2e2  color:#991b1b  border:#fca5a5
Insight  → bg:#ede9fe  color:#4c1d95  border:#c4b5fd
```

---

## 布局结构 {#layout}

```html
<!doctype html><html lang="zh-CN">
<head>
  <!-- 嵌入 CSS，无外部 CDN -->
</head>
<body>
  <nav class="sidebar"><!-- 固定左侧导航 240px --></nav>
  <main class="content"><!-- 主内容区，max-width: 1280px --></main>
</body>
</html>
```

### ⚠️ 必须遵守的布局 CSS（禁止改动结构）

```css
/* body 只做背景/字体，绝对不能设 display:grid 或 display:flex */
body {
  font-family: ...;
  background: var(--bg-page);
  color: var(--text-primary);
  min-height: 100vh;
}

/* sidebar 用 position:fixed，脱离文档流 */
.sidebar {
  position: fixed;
  top: 0; left: 0;
  width: 240px;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
  background: var(--bg-sidebar);
}

/* content 只用 margin-left 偏移，不要再叠加 grid 列偏移 */
.content {
  margin-left: 240px;
  max-width: 1280px;
  padding: 32px 40px;
}
```

### ❌ 常见布局陷阱（会导致内容区被压缩到极窄）

```css
/* 错误示例：body 同时设了 grid，sidebar 又是 fixed，double-offset！*/
body {
  display: grid;                        /* ← 禁止 */
  grid-template-columns: 240px 1fr;     /* ← 禁止 */
}
.content {
  margin-left: 240px; /* grid 已偏移 240px，再加 margin 等于 480px 才开始渲染 */
}
```

**结论：sidebar 是 `position:fixed` → body 用普通块 → content 只用 `margin-left`，三者缺一不可，不可混用。**

- 最大内容宽度：1280px，居中
- 仅允许最小化原生 JS（侧边栏折叠、表格排序、章节展开/折叠）
- `@media print`：隐藏侧边栏，内容全宽，主章节前分页

---

## 图表规范 {#charts}

所有图表必须为**纯内联 SVG 或 CSS**（零外部依赖）。

### Chart 1 — KPI 趋势迷你图
每个 KPI 卡片内嵌 60×20px SVG 折线图（当日高亮）。单日数据时显示平线+圆点。

### Chart 2 — 场景分布（SVG 水平条形图）
- 宽 100%，每行主条（runs 占比）+ 细条（cost 占比）双条模式
- 颜色梯度：Top 场景最深，依次变浅

### Chart 3 — 熟练度分层甜甜圈（SVG）
- 160×160px，r=60，stroke-width=24
- 颜色：Expert=#7c3aed，Advanced=#3b82f6，Intermediate=#10b981，Beginner=#f59e0b
- 中心标注活跃用户总数

### Chart 4 — 用户成本散点图（SVG 400×220px）
- X 轴：avg tokens/run；Y 轴：user cost (USD)
- 按熟练度层级着色，点大小正比于 run 数
- P50 分位线将图分为四象限（高成本低效率区红色边框）
- 标注 Top-5 成本用户

### Chart 5 — 场景 × 用户热力图（HTML/CSS 表格）
- 行：Top-8 场景；列：Top-10 用户
- 单元格颜色：白(0) → 蓝色梯度（基于最大值归一化）

### Chart 6 — 成本归因瀑布图（SVG）
- Top-5 用户 + Others 水平堆叠条
- 各段按熟练度层级着色，标注用户 ID + 成本占比 %

### Chart 7 — 平台健康评分仪表盘（SVG 200×120px）
- 半圆弧仪表，颜色区间：红(0–40) / 橙(40–60) / 蓝(60–80) / 绿(80–100)
- 指针指向计算得分，中央大字显示分值

### Chart 8 — 基尼洛伦兹曲线（SVG 200×200px）
- X 轴：用户累计 %；Y 轴：成本累计 %
- 对角等分线（虚线灰色）+ 实际洛伦兹曲线（蓝色填充区域）
- 标注 Gini 系数值

### Chart 9 — 标签词云（CSS Flexbox 模拟）
- Top-20 标签，字号 = 12 + (share% × 4) px，上限 28px
- 按元类别着色

### Chart 10 — 效率分层雷达图（SVG 220×220px）
- 五轴/六轴雷达：avg tokens/run、cost/run、run 数、session 数、场景多样性
- 每个熟练度层级一个半透明多边形，共 4 层叠加

---

## 组件规范 {#components}

### KPI 卡片
- 3 或 4 列 Grid
- 白底，细阴影，12px 圆角
- 指标值：28px 粗体，主色
- 标签：12px，次要色
- 变化徽章：绿/红背景内联 chip
- 迷你图：卡片右下角（60×20px）

### 数据表格
- 斑马纹（交替行 #f8fafc）
- 超过 10 行启用固定表头（sticky thead）
- 数值列右对齐
- 可排序列（▲▼ 图标，JS onClick）
- 风险标签：有色 chip（border-radius: 4px; padding: 2px 6px）
- 紧凑：font-size: 13px，padding: 8px 12px

### 发现卡（交叉维度）
- 全宽卡片，左边框 4px solid（绿/橙/红按分类）
- 头行：图标 + 标题 + 分类徽章（右对齐）
- 正文：发现 / 指标 / 建议 / 负责人+目标 标签行
- 背景色与边框色一致（5% 透明度）

### 侧边栏导航
- 深色背景（#1e293b），白色文字
- 激活项：左边框高亮 + 浅色背景
- 子项缩进
- CSS `scroll-behavior: smooth`

---

## 单日报告章节结构 {#single-day-sections}

侧边栏导航结构：
```
▸ 执行摘要
▸ 平台健康评分
▸ 公司维度
  ▸ 核心指标
  ▸ 统计分布
▸ 用户维度
  ▸ 层级分布
  ▸ 用户排行
  ▸ 用户画像
▸ 场景与标签
  ▸ 场景分布
  ▸ 标签分析
▸ 交叉分析
  ▸ 成本归因
  ▸ 场景依赖
  ▸ 效率差距
  ▸ 画像对齐
  ▸ 集中度
  ▸ 趋势归因
  ▸ 异常用户
  ▸ 场景ROI
  ▸ 节省机会
▸ 风险矩阵
▸ 指标定义
```

必需章节（按序）：

1. **报告头** — 标题、日期、时区、生成时间戳、报告版本
2. **执行摘要** — 健康评分仪表盘 + 5–7 条关键发现（每条含指标 + 分类徽章）
3. **平台健康评分** — 评分卡 + 各子维度得分分解表
4. **公司维度** — KPI 卡片网格（≥12 张，含迷你图）+ 统计分布面板（P50/P75/P90/P99 + Gini + Pareto）+ 趋势环比面板
5. **用户维度** — 熟练度甜甜圈 + 分层统计表 + Top-20 用户表（含效率评分/Z-Score/风险标签）+ 散点图 + 画像网格 + 效率异常高亮框
6. **场景与标签** — 场景条形图（双条）+ 场景汇总表 + 标签词云 + 标签×分层映射表 + 内容元类别饼图
7. **交叉分析** — 成本瀑布图 + 场景×用户热力图 + 洛伦兹曲线 + 效率雷达 + 9 张发现卡（7A–7I）
8. **风险矩阵** — 全量彩色表格（P0 优先排序），含影响列
9. **指标定义** — 词汇表（指标名 / 公式 / 解释 / 良好阈值）
10. **报告尾** — 生成元数据、数据来源说明、免责声明

---

## 数据可用性规则 {#data-rules}

- 指标不可用 → 渲染 `—`，tooltip `title="数据缺失"`
- 用户数 < 5 → 顶部黄色横幅：`⚠ 样本量偏小（N<5），分析结论仅供参考`
- 无数据图表 → 显示空状态占位符（图标 + 提示文字）
