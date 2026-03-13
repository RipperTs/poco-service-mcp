# 区间分析工作流

适用于：本周、上周、本月、上月、任意起止日期等多日时间段分析。

## 目录
1. [日期解析](#step1)
2. [逐日数据采集](#step2)
3. [区间聚合计算](#step3)
4. [趋势分析](#step4)
5. [交叉对比分析](#step5)
6. [HTML 区间报告组装](#step6)

---

## Step 1 — 日期解析 {#step1}

将用户的自然语言时间表述转换为具体日期列表：

| 用户表述 | 解析规则 |
|---|---|
| 本周 | 本周周一 ~ 今天 |
| 上周 | 上周周一 ~ 上周周日 |
| 本月 | 本月 1 日 ~ 今天 |
| 上个月 | 上月 1 日 ~ 上月末 |
| 最近 N 天 | 今天往前推 N-1 天 ~ 今天 |
| 具体起止日 | 直接使用 |

超过 31 天的区间，询问用户是否确认（数据拉取量较大）。

---

## Step 2 — 逐日数据采集 {#step2}

对区间内**每一天**调用：
```
call analysis_get_company_daily_usage(day, timezone, top_limit=10)
```

并行调用以提升效率（若工具支持并发）。

对于**活跃用户数 > 0** 的日期，额外调用：
```
call analysis_get_daily_analysis_brief(day, timezone)
```

将每日结果按日期索引存储为结构化数据集：
```json
{
  "YYYY-MM-DD": {
    "runs": N,
    "sessions": N,
    "active_users": N,
    "duration_ms": N,
    "input_tokens": N,
    "output_tokens": N,
    "cost_usd": N,
    "top_scenarios": [...],
    "insights": [...]
  }
}
```

---

## Step 3 — 区间聚合计算 {#step3}

### 3A. 汇总指标

| 指标 | 计算方式 |
|---|---|
| 总 runs | Σ 各日 runs |
| 总 sessions | Σ 各日 sessions |
| 总时长 | Σ 各日 duration_ms，转换为 min/hr |
| 总成本 | Σ 各日 cost_usd |
| 总 tokens | Σ 各日 (input + output) tokens |
| 活跃用户（峰值） | max(各日 active_users) |
| 活跃天数 | COUNT(runs > 0 的天数) |
| 日均 runs | 总 runs ÷ 总天数 |
| 日均成本 | 总成本 ÷ 总天数 |
| avg cost/run（区间） | 总成本 ÷ 总 runs |

### 3B. 场景聚合

跨天合并场景数据：
```
For each day → for each scene in top_scenarios:
    merged[scene_key].runs += runs
    merged[scene_key].cost += cost
```
计算区间内各场景总 runs 和成本的占比排行。

### 3C. 有效工作日分析

- 识别无数据天（runs = 0）：区分周末 vs 工作日空白
- 计算使用密度：活跃天数 ÷ 总天数（%）

---

## Step 4 — 趋势分析 {#step4}

### 4A. 日趋势指标

对每日以下指标计算折线数据系列，供图表渲染：
- runs / day
- cost / day
- active_users / day
- avg_cost_per_run / day（总成本 ÷ 总 runs）

### 4B. 趋势方向判断

对每个指标计算线性回归斜率（简化版）：
```
slope ≈ (last_day_value - first_day_value) / (n - 1)
```
- slope > 0 且显著（> 10% 均值）→ "上升趋势 ↑"
- slope < 0 且显著 → "下降趋势 ↓"
- 否则 → "平稳 →"

### 4C. 峰谷识别

- 最高 runs 日 / 最高 cost 日
- 最低非零 runs 日 / 最低非零 cost 日
- 单日最大波动（当日 vs 前日 DoD 变化最大值）

### 4D. 周期模式（如区间 ≥ 14 天）

- 对比周内各工作日均值（周一均值 vs 周二均值 ... 等）
- 识别高频使用日（工作日 vs 周末差异）

### 4E. 环比对比（如适用）

若区间为完整的周/月，自动计算与上一个同等区间的对比：
- 本周 vs 上周：总 runs、总成本、日均活跃用户的 Δ%
- 本月 vs 上月：同上

---

## Step 5 — 交叉对比分析 {#step5}

### 5A. 成本结构分析
- 哪几天贡献了 80% 的成本（Pareto）
- 成本最高的场景跨天变化（是否稳定/偶发）

### 5B. 活跃度健康信号
- 连续使用天数最长的连续段
- 连续空白天数最长的段（潜在平台中断或节假日）
- 整体使用率（活跃天数 / 总天数）评级：
  - ≥ 80% → 高频使用 [Positive]
  - 50–79% → 中频使用 [Alert]
  - < 50% → 低频使用 [Risk]

### 5C. 成本效率趋势
- avg_cost_per_run 是否在区间内呈下降趋势（效率提升信号）
- 若 avg_cost_per_run 呈上升趋势 → "单次成本上升，需排查效率退化 [Alert]"

### 5D. 场景演变
- 对比区间前半段 vs 后半段的 Top-3 场景是否变化
- 新增场景 / 消失场景 → 标注为 "场景迁移信号 [Insight]"

---

## Step 6 — HTML 区间报告组装 {#step6}

HTML 规范见 [html-report-spec.md](html-report-spec.md)，区间报告在标准规范基础上调整以下内容：

### 报告标题
```
Agent 平台使用分析报告 — [start_date] 至 [end_date]（共 N 天）
```

### 必需章节（区间报告）

1. **报告头** — 标题、区间、时区、生成时间戳
2. **执行摘要** — 区间核心指标卡片 + 5–7 条关键发现 + 趋势方向
3. **区间汇总指标** — 总量 KPI 卡片（总 runs / 总 cost / 总 tokens / 活跃天数 / 日均）
4. **日趋势图表**（重点章节）：
   - Runs 日折线图（SVG，含峰谷标注）
   - Cost 日折线图（SVG，含 DoD 变化标注）
   - 活跃用户日折线图
   - 多指标叠加图（runs + cost 双 Y 轴）
5. **场景分析** — 区间累计场景占比（横向条形图）+ 场景演变对比表
6. **趋势洞察** — 趋势方向卡片（4A–4E 结论）+ 周期模式（若适用）
7. **交叉对比** — 5A–5D 发现卡（同单日 Finding Card 格式）
8. **环比对比**（若适用）— 本期 vs 上期对比表（runs / cost / 日均 DoD Δ%）
9. **逐日明细表** — 每行一天，含 runs / sessions / cost / 活跃用户 / Top 场景
10. **报告尾** — 生成元数据、数据来源说明

### 区间专属图表

**R1 — 多指标日趋势折线图（SVG）**
- 宽：100% 容器
- X 轴：日期（等间距）
- Y 轴左：runs；Y 轴右：cost (USD)（双轴）
- 颜色：runs=#3b82f6，cost=#f59e0b
- 峰值日标注圆点 + 数值标签
- 无数据日渲染为虚线断点

**R2 — 场景区间堆叠条形图（SVG）**
- 每行为一个场景，水平条表示区间总 runs 占比
- 次级细条显示成本占比（同单日 Chart 2）

**R3 — 环比变化柱状图（SVG，若适用）**
- 本期 vs 上期各指标并排柱（runs / cost / 活跃用户）
- 柱顶标注 Δ% 值，正增长绿色，负增长红色

**R4 — 活跃度日历热力图（HTML CSS Grid）**
- 按周排列日期（列=周，行=工作日）
- 单元格背景色：白(0 runs) → 深蓝(高 runs)，基于 max runs 归一化
- 悬停显示当日 runs + cost（title tooltip）

### 质检清单（区间报告）
- [ ] 逐日数据完整（有数据天数与实际请求天数匹配）
- [ ] 聚合合计与逐日之和一致（runs/cost 误差 ≤ 1%）
- [ ] 趋势方向判断每个指标均有明确标注
- [ ] 环比对比章节（若适用）展示 Δ% 值
- [ ] 逐日明细表行数与区间天数一致
- [ ] 活跃度热力图涵盖全部区间日期
- [ ] HTML 自包含，无外部资源依赖
- [ ] 文件保存至 `/workspace/agent_report_<start>_<end>_<timestamp>.html`
- [ ] **布局检查**：body 无 `display:grid`；sidebar 为 `position:fixed`；content 仅用 `margin-left:240px`（见 html-report-spec.md）
