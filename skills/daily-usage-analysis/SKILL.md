---
name: daily-usage-analysis
description: Generate a professional single-page HTML analytics report from poco_analytics daily metrics at company and user levels, primarily for Agent platform usage analysis. Use when asked to analyze daily runs/sessions/duration, token usage, USD cost, scenario composition, risk signals, and optimization actions for a specified date and timezone.
---

# Daily Usage Analysis — Multi-Dimensional Intelligence Report

## Objective

Produce one professional **single-page HTML dashboard report** for a specified day.

The report MUST deliver **four analysis layers** with rich inline SVG/CSS visualizations:

1. **Company Dimension** — Platform-level health, workload, cost, and statistical distribution.
2. **User Dimension** — Contribution ranking, proficiency tiers, personas, and outlier detection.
3. **Scenario & Content Dimension** — Scene taxonomy, tag intelligence, and topic clustering.
4. **Cross-Dimensional Analysis** — Causal links between user behavior, scenarios, and company-level signals.

The final output must look and feel like a **product-grade BI dashboard**, not a plain text report.

---

## Scope

- **Include:** data retrieval, statistical computation, multi-dimensional analysis, risk diagnosis, visualization, and actionable recommendations.
- **Exclude:** any write / configuration / management operation.

---

## Inputs

| Parameter | Required | Default | Notes |
|---|---|---|---|
| `day` | Yes | — | `YYYY-MM-DD` |
| `timezone` | No | `Asia/Shanghai` | IANA timezone name |
| `top_limit` | No | 20 | Top-N for scenario/tag/user lists |
| `user_limit` | No | 100 | Number of users to fetch |
| `user_offset` | No | 0 | Pagination offset |

---

## Preconditions

- MCP request must carry admin-scope credential.
- If credential is unavailable, stop and return a clear error immediately.

---

## Tools

**Primary (always call first):**

- `analysis_get_daily_report_dataset` — Fetches all dimensions in one call.

**Supplementary (call when primary data is incomplete or deeper drill-down is needed):**

| Tool | Use When |
|---|---|
| `analysis_get_company_daily_usage` | Company-level totals missing or stale |
| `analysis_get_user_daily_usage` | User list incomplete or pagination needed |
| `analysis_get_usage_scenarios` | Scenario breakdown missing at company or per-user level |
| `analysis_get_daily_analysis_brief` | AI-generated narrative needed for executive section |
| `analysis_get_daily_content_taxonomy` | Content category and tag distribution missing |
| `analysis_get_daily_user_proficiency` | Proficiency scores/tiers missing |
| `analysis_get_daily_user_personas` | Behavioral persona tags missing |

---

## Execution Workflow

### Step 1 — Data Collection

```
call analysis_get_daily_report_dataset(day, timezone, top_limit=20, user_limit=100)
```

If any module is absent or inconsistent, backfill via the corresponding supplementary tool.

### Step 2 — Data Validation & Reconciliation

Verify before proceeding:

- Company total runs ≈ Σ user runs (tolerance ≤ 2%).
- Company total tokens ≈ Σ user tokens.
- Scenario totals ≈ content taxonomy category totals.
- If discrepancy > 2%, note inline as `⚠ 数据差异 X%，以公司维度为准`.

### Step 3 — Statistical Pre-computation

Compute the following derived metrics from raw data before writing any analysis prose:

#### 3A. Percentile Distribution (per user, on cost and tokens/run)

Rank all users by cost and tokens/run, then compute:

- P50 (median), P75, P90, P99 for both metrics.
- Use these to identify outliers: any user > P90 cost is a **high-cost outlier**.

#### 3B. Gini Coefficient (usage inequality)

Compute Gini from user cost shares:

```
Sort users by cost ascending: c₁ ≤ c₂ ≤ ... ≤ cₙ
Gini = 1 - (2/n²·mean) × Σᵢ(n-i+1)·cᵢ   [simplified approximation]
```

Interpretation:
- Gini < 0.4 → balanced distribution (healthy).
- 0.4–0.6 → moderate concentration (monitor).
- Gini > 0.6 → high concentration (risk flag: **"使用权重严重不均"**).

#### 3C. Pareto Check (80/20 rule)

- Compute what share of users drives 80% of total cost/runs.
- If top 20% users drive > 80% → confirm Pareto holds → **"符合幂律分布"**.
- If top 5% users drive > 80% → extreme concentration → **"超幂律集中，平台普及度严重不足"**.

#### 3D. Efficiency Score per User

```
Efficiency Score = (1 / avg_tokens_per_run) × 1000   [higher = more efficient]
```

Rank users by Efficiency Score. Note top-5 most efficient and bottom-5 least efficient.

#### 3E. Cost Anomaly Z-Score

```
z = (user_cost - mean_cost) / std_cost
```

Flag any user with z > 2.5 as a **statistical cost anomaly**. List them for governance review.

### Step 4 — Company Dimension Analysis

Compute and record all of the following:

**Workload KPIs:**
- Total runs, sessions, active users, total duration (min/hr).
- Active user rate: active users ÷ registered users (if available).
- Runs per active user (intensity index).
- Sessions per active user.

**Token KPIs:**
- Input tokens, output tokens, total tokens.
- Input/Output ratio (high ratio = document-heavy; low ratio = chat-heavy).
- Avg tokens/run (platform efficiency baseline).
- Avg tokens/session.

**Cost KPIs:**
- Total cost (USD), avg cost/run, avg cost/session, avg cost/active user.
- Day-over-day delta for total cost (▲/▼ with % and absolute value).
- Day-over-day delta for runs and tokens.
- Cost per 1k tokens (implied rate).

**Distribution KPIs (from Step 3):**
- P50 / P90 / P99 user cost.
- Gini coefficient.
- Pareto ratio (% users → 80% cost).

**Scenario Concentration:**
- Top-1 scenario share (%) of total runs and cost.
- Top-3 cumulative share.
- HHI (Herfindahl–Hirschman Index) for scenario distribution:
  ```
  HHI = Σ (scenario_share%)²   [0–10000; < 1500 = competitive, > 2500 = concentrated]
  ```

### Step 5 — User Dimension Analysis

For each user in the dataset:

| Metric | Computation |
|---|---|
| Proficiency tier | Expert / Advanced / Intermediate / Beginner |
| Run share | user_runs ÷ company_runs (%) |
| Cost share | user_cost ÷ company_cost (%) |
| Token efficiency | user_tokens ÷ user_runs |
| Efficiency score | from Step 3D |
| Cost z-score | from Step 3E |
| Dominant scenario | top-1 scene by run count |
| Persona tags | from persona data |
| Risk flag | High-Cost Outlier / Misaligned Persona / Over-Concentrated / Normal |

Aggregate tier-level statistics:

| Tier | Count | % of Users | Run Share | Cost Share | Avg Tokens/Run | Avg Efficiency Score |
|---|---|---|---|---|---|---|
| Expert | | | | | | |
| Advanced | | | | | | |
| Intermediate | | | | | | |
| Beginner | | | | | | |

### Step 6 — Scenario & Content Dimension Analysis

**Scenario analysis:**
- Distribution table: scenario / runs / cost / run_share / cost_share / top_user.
- Scenario HHI (from Step 4).
- Scene growth signal: if delta available, flag growing vs declining scenes.

**Tag analysis:**
- Top-20 tags by run count with share %.
- Tag-to-tier mapping: for each top-10 tag, which proficiency tier uses it most?
- Tag co-occurrence note: identify any 2–3 frequently paired tags (if data allows).

**Content category clustering:**
- Group tags into 4–6 meta-categories (e.g., 工业生产 / 数据分析 / 文档协作 / 代码开发 / 其他).
- Compute each meta-category's share of total cost.

### Step 7 — Cross-Dimensional Analysis (CRITICAL LAYER)

For each axis below, produce a **named finding card** with: metric values, classification badge (Positive / Alert / Risk / Insight), and one recommended action.

#### 7A. Cost Driver Attribution

- Identify Top-5 users by cost share.
- Compute their collective cost share.
- Map each to their dominant scenario.
- Compute cost HHI at user level.
- Flag if Top-3 users > 50% cost → **"成本高度集中 [Risk]"**.
- Determine if cost concentration correlates with scenario concentration or is user-behavior driven.

#### 7B. Scenario × User Dependency Matrix

- For each Top-5 scenario: list Top-3 contributing users and their shares.
- Compute per-scenario HHI (user concentration within scene).
- If per-scenario HHI > 5000 → **"场景单点依赖 [Risk]"**.
- Identify scenarios with **zero Expert/Advanced** users → **"高价值场景人才空白 [Alert]"**.
- Identify scenarios used by 10+ users → **"场景已规模化普及 [Positive]"**.

#### 7C. Proficiency × Efficiency Gap Analysis

- Build a tier × efficiency matrix.
- Compute efficiency ratio: Expert avg / Beginner avg.
- If ratio > 1.5 → **"高阶用户效率优势显著，培训ROI可期 [Positive]"**.
- If ratio < 1.1 → **"效率分层不明显，培训价值待验证 [Alert]"**.
- Flag Beginner-tier users with cost z-score > 1.5 → **"初级用户异常高消耗 [Risk]"**.
- Compute: if all Beginners achieved Intermediate-level efficiency, estimated token/cost savings %.

#### 7D. Persona × Scenario Alignment Matrix

- Cross-map persona tags with dominant scenarios.
- Expected alignments (examples):
  - 深度使用者 → 高炉/炼钢/数据分析 (aligned).
  - 轻量探索者 → 日常办公 (aligned).
  - 轻量探索者 + top-5 cost → **"画像-消耗错位 [Alert]"**.
- List all 高风险用户 persona users with their scenarios for governance review.
- Note any 未分类 users (missing persona) as a data quality gap.

#### 7E. Active User Concentration & Platform Penetration

- Compute: top-10% users' share of total runs.
- Compute: users with 0 runs (inactive) if total registered is known.
- Pareto result from Step 3C.
- Gini result from Step 3B.
- Classification matrix:

| Gini | Pareto | Signal |
|---|---|---|
| < 0.4 | Top-20% < 60% | 健康分布 [Positive] |
| 0.4–0.6 | Top-20% 60–80% | 中度集中 [Alert] |
| > 0.6 | Top-20% > 80% | 严重集中 [Risk] |

#### 7F. Trend Attribution

- Day-over-day: which tier contributed most to run increase/decrease?
- If cost increased: correlate with (a) more users, (b) existing users doing more, or (c) token/run ratio increase.
- Label the primary driver: **Volume-Driven / Efficiency-Driven / New-User-Driven**.

#### 7G. Statistical Outlier Users

- List all users with cost z-score > 2.5 (from Step 3E).
- For each: cost, z-score, dominant scenario, persona tag, proficiency tier.
- These users require manual governance review.
- If 0 outliers → **"无统计异常用户 [Positive]"**.

#### 7H. Scenario ROI Proxy

- Assign each scenario a business value tier (industrial-critical / analytical / operational / exploratory) based on scene name:
  - industrial-critical: 高炉, 炼钢, 能源, 自动化运维
  - analytical: 数据分析
  - operational: 文档报告, 日常办公
  - exploratory: 代码开发, 其他
- Compute cost share per business value tier.
- Flag if > 40% cost in "exploratory" tier with < 20% users → **"高探索性消耗，业务价值待验证 [Alert]"**.
- Flag if industrial-critical tier < 20% of cost with relevant department present → **"核心业务场景渗透不足 [Risk]"**.

#### 7I. Efficiency Opportunity Quantification

- Identify users in bottom-25% efficiency with > 5% cost share.
- Estimate potential cost savings if these users improved to median efficiency:
  ```
  Savings = Σ (user_cost - user_runs × P50_tokens_per_run × cost_per_token)
  ```
- State estimated savings as `$X.XX / day` or `~X% of total cost`.

### Step 8 — Platform Health Score

Compute a composite **Platform Health Score (0–100)**:

| Dimension | Weight | Score Logic |
|---|---|---|
| Cost stability (DoD delta) | 20% | 100 if Δ < 5%; linear decay to 0 at Δ > 50% |
| User distribution (Gini) | 20% | 100 if Gini < 0.3; linear decay to 0 at Gini > 0.8 |
| Scenario diversity (HHI) | 15% | 100 if HHI < 1500; decay to 0 at HHI > 5000 |
| Expert tier cost share | 15% | 100 if Expert + Advanced > 50% cost |
| Outlier user count | 15% | 100 if 0 outliers; -20 per outlier up to -100 |
| Risk flag count | 15% | 100 if 0 Risk flags; -15 per Risk flag |

Display as a prominent gauge/score card with color:
- 80–100: 健康 (green)
- 60–79: 良好 (blue)
- 40–59: 待改善 (amber)
- < 40: 告警 (red)

### Step 9 — Risk & Action Matrix

Consolidate all flagged risks from Steps 4–7 into one table:

| Risk ID | Dimension | Risk Label | Metric Evidence | Severity | Impact | Action | Owner | Target Date |
|---|---|---|---|---|---|---|---|---|

Severity: P0 (today) / P1 (this week) / P2 (this month).
Impact: High / Medium / Low.

### Step 10 — HTML Report Assembly

Build the full single-page HTML document per the specification below.

---

## Visualization Specifications

All charts MUST be implemented with **pure inline SVG or CSS** (zero external dependencies).

### Chart 1 — KPI Trend Sparklines (per KPI card)

Each KPI card includes a 60×20px inline SVG sparkline showing the value trend (current day highlighted). If only single-day data is available, show a flat line with a dot.

```svg
<!-- Example sparkline skeleton -->
<svg width="60" height="20" viewBox="0 0 60 20">
  <polyline points="..." fill="none" stroke="#3b82f6" stroke-width="1.5"/>
  <circle cx="55" cy="Y" r="2.5" fill="#3b82f6"/>
</svg>
```

### Chart 2 — Scenario Distribution (SVG Horizontal Bar Chart)

- Width: 100% of container.
- Each bar: proportional to run share, labeled with scenario name + percentage.
- Color gradient: top scenario darkest, fading to lighter shades.
- Show cost share as a secondary thin bar underneath each primary bar (dual-bar pattern).

```svg
<svg width="100%" height="[dynamic]" viewBox="0 0 400 [dynamic]">
  <!-- For each scenario: -->
  <rect x="120" y="Y" width="[share%×240]" height="14" fill="#3b82f6" rx="2"/>
  <rect x="120" y="Y+16" width="[cost_share%×240]" height="6" fill="#93c5fd" rx="1"/>
  <text x="115" y="Y+11" text-anchor="end" font-size="11">场景名</text>
  <text x="[bar_end+4]" y="Y+11" font-size="10" fill="#6b7280">XX%</text>
</svg>
```

### Chart 3 — Proficiency Tier Donut Chart (SVG)

- 160×160px SVG donut (r=60, stroke-width=24).
- Four arcs, color-coded: Expert=#7c3aed, Advanced=#3b82f6, Intermediate=#10b981, Beginner=#f59e0b.
- Center label: total active user count.
- Legend below with tier name, count, and %.

```svg
<svg width="160" height="160" viewBox="0 0 160 160">
  <circle cx="80" cy="80" r="60" fill="none" stroke="#e5e7eb" stroke-width="24"/>
  <!-- Each tier arc via stroke-dasharray + stroke-dashoffset -->
  <circle cx="80" cy="80" r="60" fill="none" stroke="#7c3aed" stroke-width="24"
          stroke-dasharray="[arc_len] [remaining]" stroke-dashoffset="[offset]"
          transform="rotate(-90 80 80)"/>
  <!-- ... repeat for each tier ... -->
  <text x="80" y="85" text-anchor="middle" font-size="18" font-weight="700">[total]</text>
</svg>
```

### Chart 4 — User Cost Distribution (SVG Scatter Plot)

- 400×220px SVG.
- X-axis: avg tokens/run (efficiency, log scale if range > 10×).
- Y-axis: user cost (USD).
- Each user = one dot, colored by proficiency tier.
- Dot size proportional to run count.
- Quadrant lines at P50 for both axes, creating four zones:
  - Top-right: High-Cost Low-Efficiency (highlight in red border).
  - Bottom-left: Low-Cost High-Efficiency (highlight in green border).
- Label the top-5 cost users by name/ID.

### Chart 5 — Scenario × User Heatmap (HTML/CSS Grid)

- Rows = Top-8 scenarios, Columns = Top-10 users.
- Cell value: run count for that user × scenario combination.
- Cell background: white (0 runs) → blue gradient (high runs), intensity based on max cell value.
- Row and column headers with total annotations.
- Renders as `<table>` with inline `background-color` computed from data.

### Chart 6 — Cost Attribution Waterfall (SVG)

- Shows contribution of Top-5 users + "Others" to total cost.
- Horizontal stacked bar, each segment colored by proficiency tier.
- Width of each segment proportional to cost share.
- Labels: user ID + cost share %.
- Total bar length = 100% of container width.

```svg
<svg width="100%" height="40" viewBox="0 0 400 40">
  <!-- Top user -->
  <rect x="0" y="8" width="[share1×400]" height="24" fill="[tier_color]"/>
  <text x="[midpoint1]" y="24" text-anchor="middle" font-size="10" fill="white">User A 32%</text>
  <!-- ... -->
</svg>
```

### Chart 7 — Platform Health Score Gauge (SVG)

- 200×120px SVG semicircle gauge.
- Arc from 180° to 0° (left to right).
- Score needle pointing to computed score position.
- Color zones: red (0–40), amber (40–60), blue (60–80), green (80–100).
- Large score number centered below arc.

```svg
<svg width="200" height="120" viewBox="0 0 200 120">
  <!-- Background arc zones -->
  <path d="M 20,100 A 80,80 0 0,1 180,100" fill="none" stroke="#ef4444" stroke-width="16" .../>
  <!-- ... amber, blue, green zones ... -->
  <!-- Needle -->
  <line x1="100" y1="100" x2="[needle_x]" y2="[needle_y]" stroke="#1f2937" stroke-width="3"/>
  <text x="100" y="90" text-anchor="middle" font-size="28" font-weight="700">[score]</text>
</svg>
```

### Chart 8 — Gini Lorenz Curve (SVG)

- 200×200px SVG.
- X-axis: cumulative % of users (sorted ascending by cost).
- Y-axis: cumulative % of total cost.
- Equality line (diagonal, dashed gray).
- Lorenz curve (actual distribution, blue fill area).
- Gini coefficient annotated on chart.

### Chart 9 — Tag Word Cloud (CSS Flexbox Simulation)

- Render top-20 tags as a flex-wrap container.
- Font-size proportional to run share: `font-size = 12 + (share% × 4)` px, capped at 28px.
- Color-coded by meta-category.
- Each tag clickable in concept but static in output.

### Chart 10 — Efficiency Tier Radar (SVG)

- 220×220px SVG pentagon/hexagon radar.
- Axes: avg tokens/run, cost/run, run count, session count, scenario diversity (# unique scenes).
- One polygon per proficiency tier (4 overlapping polygons, semi-transparent).
- Legend with tier color coding.

---

## Output Contract

Return a **valid, self-contained HTML document** (`<!doctype html>` through `</html>`).

### Navigation Structure

The page MUST have a **fixed left sidebar navigation** (collapsible on narrow screens) with anchor links to each section:

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

### Required Sections (in order)

1. **Report Header** — Title, day, timezone, generated timestamp (auto), report version.
2. **Executive Summary** — Platform health score gauge + 5–7 key findings (one per dimension), each with metric and classification badge.
3. **Platform Health Score** — Score card with breakdown table showing each dimension's sub-score.
4. **Company Dimension**
   - KPI cards grid (12 cards minimum, each with sparkline).
   - Statistical distribution panel: P50/P75/P90/P99 table + Gini + Pareto.
   - Trend delta panel: DoD comparison for runs, tokens, cost.
5. **User Dimension**
   - Proficiency tier donut chart + tier statistics table.
   - Top-20 users table with sortable columns: rank / user / tier / runs / cost / tokens/run / efficiency score / z-score / dominant scene / persona / risk flag.
   - User cost scatter plot (Chart 4).
   - Persona tag summary grid.
   - Efficiency outlier callout boxes (top-3 high-cost-low-efficiency users).
6. **Scenario & Tag Analysis**
   - Scenario horizontal bar chart (Chart 2, dual-bar runs + cost).
   - Scenario summary table: scene / runs / cost / run_share / cost_share / HHI / top_user / business_value_tier.
   - Tag word cloud (Chart 9).
   - Tag-to-tier mapping table.
   - Content meta-category pie breakdown.
7. **Cross-Dimensional Analysis**
   - Cost attribution waterfall (Chart 6).
   - Scenario × User heatmap (Chart 5).
   - Lorenz curve + Gini (Chart 8).
   - Efficiency radar (Chart 10).
   - One finding card per cross-axis 7A–7I. Card format:
     ```
     ┌─────────────────────────────────────────────┐
     │ [Icon] 7A. 成本驱动归因          [Risk Badge] │
     │ ─────────────────────────────────────────── │
     │ 发现: Top-3用户占总成本63%，主要场景：高炉     │
     │ 指标: HHI=4200, Top-3 cost share=63%        │
     │ 建议: 为高炉场景制定用量配额，目标Top-3<40%   │
     │ 责任人: 平台管理员   目标: 2026-03-20         │
     └─────────────────────────────────────────────┘
     ```
8. **Risk & Action Matrix** — Full color-coded table sorted by severity (P0 first). Include impact column.
9. **Metric Definitions** — Glossary table: metric name / formula / interpretation / good threshold.
10. **Report Footer** — Generation metadata, data source note, disclaimer.

---

## HTML & Visual Design Requirements

### Layout

- Full HTML document: `<!doctype html><html lang="zh-CN">`.
- **Layout:** CSS Grid with fixed left sidebar (240px) + main content area.
- Max content width: 1280px, centered.
- Embedded CSS only (no external CDN, no JavaScript frameworks).
- Minimal vanilla JS allowed for: sidebar toggle, table sort, section collapse/expand.

### Design System

```css
/* Color tokens */
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

### Component Specifications

**KPI Cards:**
- 3 or 4 columns grid.
- White background, subtle shadow, 12px border-radius.
- Metric value: 28px bold, primary color.
- Label: 12px, secondary color.
- Delta badge: inline chip, green/red background.
- Sparkline: bottom-right of card (60×20px).

**Data Tables:**
- Zebra striping (`#f8fafc` alternate rows).
- Sticky `<thead>` for tables > 10 rows.
- Right-align numeric columns.
- Sortable columns (▲▼ icons, JS onClick).
- Risk flag cells: colored chip (`border-radius: 4px; padding: 2px 6px`).
- Compact: `font-size: 13px`, `padding: 8px 12px`.

**Finding Cards (Cross-Dimensional):**
- Full-width card, left border 4px solid (green/amber/red by classification).
- Header row: icon + title + classification badge (right-aligned).
- Body: 发现 / 指标 / 建议 / 责任人+目标 in labeled rows.
- Subtle background tint matching border color (5% opacity).

**Classification Badges:**
```
Positive  → bg:#dcfce7 color:#166534 border:#bbf7d0
Alert     → bg:#fef9c3 color:#854d0e border:#fde68a
Risk      → bg:#fee2e2 color:#991b1b border:#fca5a5
Insight   → bg:#ede9fe color:#4c1d95 border:#c4b5fd
```

**Sidebar Navigation:**
- Dark background (`#1e293b`), white text.
- Active section highlighted with left border + lighter background.
- Indented sub-items for child sections.
- Smooth scroll anchors (CSS `scroll-behavior: smooth`).

**Section Headers:**
- Large section: `font-size: 20px`, bold, border-bottom 2px solid primary.
- Sub-section: `font-size: 15px`, medium weight, `color: var(--text-secondary)`.

**Print CSS:**
- `@media print` block: hide sidebar, make content full-width, page-break-before for major sections.

### Data Availability Rules

- If any metric is unavailable from API: render `—` with tooltip `title="数据缺失"`.
- If user count < 5: prepend a yellow banner at top: `⚠ 样本量偏小（N<5），分析结论仅供参考`.
- Charts with no data: show an empty state placeholder with icon and text.

---

## Quality Gates

Before finalizing, verify ALL of the following:

- [ ] All 10 required sections are present and non-empty.
- [ ] All 10 charts are rendered as inline SVG/CSS (no external images or CDN).
- [ ] All 9 cross-dimensional analyses (7A–7I) have metric values + classification + action.
- [ ] Platform Health Score is computed and displayed with sub-dimension breakdown.
- [ ] Gini coefficient is computed and shown with Lorenz curve.
- [ ] Pareto analysis result is stated with exact % values.
- [ ] P50/P75/P90/P99 percentiles are computed and shown in the distribution panel.
- [ ] All risk flags in the Risk Matrix have: severity, impact, action, owner, target date.
- [ ] User tier distribution covers all four tiers (count = 0 explicitly shown if absent).
- [ ] HTML is self-contained, renders without external resources, and passes basic W3C structure check.
- [ ] No hardcoded placeholder numbers — all figures from MCP tool responses.
- [ ] Sidebar navigation links all resolve to `id` anchors in the document.
- [ ] Tables with > 10 rows have sticky headers.
- [ ] Print CSS is present.
