# 单日分析工作流

## 目录
1. [数据采集](#step1)
2. [数据校验与对账](#step2)
3. [统计预计算](#step3)
4. [公司维度分析](#step4)
5. [用户维度分析](#step5)
6. [场景与标签分析](#step6)
7. [交叉维度分析](#step7)
8. [平台健康评分](#step8)
9. [风险与行动矩阵](#step9)
10. [HTML 报告组装](#step10)

---

## Step 1 — 数据采集 {#step1}

```
call analysis_get_daily_report_dataset(day, timezone, top_limit=20, user_limit=100)
```

如任何模块缺失或不一致，通过对应补充工具回填：
- 公司汇总缺失 → `analysis_get_company_daily_usage`
- 用户列表不完整 → `analysis_get_user_daily_usage`
- 场景缺失 → `analysis_get_usage_scenarios`
- 叙述摘要 → `analysis_get_daily_analysis_brief`
- 内容标签 → `analysis_get_daily_content_taxonomy`
- 熟练度 → `analysis_get_daily_user_proficiency`
- 用户画像 → `analysis_get_daily_user_personas`

---

## Step 2 — 数据校验与对账 {#step2}

- 公司总 runs ≈ Σ 用户 runs（容差 ≤ 2%）
- 公司总 tokens ≈ Σ 用户 tokens
- 场景合计 ≈ 内容分类合计
- 差异 > 2% 时，在报告中标注 `⚠ 数据差异 X%，以公司维度为准`

---

## Step 3 — 统计预计算 {#step3}

### 3A. 百分位分布（用户维度）
对所有用户的 cost 和 tokens/run 排序，计算：
- P50、P75、P90、P99
- P90 以上 cost 用户标记为**高成本异常**

### 3B. 基尼系数
```
Sort users by cost ascending: c₁ ≤ c₂ ≤ ... ≤ cₙ
Gini = 1 - (2/n²·mean) × Σᵢ(n-i+1)·cᵢ
```
- Gini < 0.4 → 均衡分布（健康）
- 0.4–0.6 → 中度集中（监控）
- Gini > 0.6 → 高集中（风险："使用权重严重不均"）

### 3C. Pareto 检验（80/20）
- Top 20% 用户驱动 > 80% 成本 → 符合幂律分布
- Top 5% 用户驱动 > 80% 成本 → 超幂律集中 → "平台普及度严重不足"

### 3D. 效率评分
```
Efficiency Score = (1 / avg_tokens_per_run) × 1000
```
标记效率最高 Top-5 和最低 Bottom-5 用户。

### 3E. 成本 Z-Score
```
z = (user_cost - mean_cost) / std_cost
```
z > 2.5 → 统计成本异常，列入治理审查。

---

## Step 4 — 公司维度分析 {#step4}

**工作负载 KPI：** 总 runs、sessions、活跃用户、总时长（min/hr）、人均 runs、人均 sessions

**Token KPI：** 输入/输出 tokens、I/O 比、avg tokens/run、avg tokens/session

**成本 KPI：** 总成本（USD）、avg cost/run、avg cost/session、avg cost/用户、DoD 环比（runs/tokens/cost）、千 token 成本

**分布 KPI（来自 Step 3）：** P50/P90/P99 用户成本、Gini 系数、Pareto 比率

**场景集中度：**
- Top-1 场景占比（runs 和 cost）
- Top-3 累计占比
- HHI 指数：`HHI = Σ (scenario_share%)²`（< 1500 = 多样，> 2500 = 集中）

---

## Step 5 — 用户维度分析 {#step5}

对每个用户计算：

| 指标 | 计算方式 |
|---|---|
| 熟练度分层 | Expert / Advanced / Intermediate / Beginner |
| Run 占比 | user_runs ÷ company_runs (%) |
| 成本占比 | user_cost ÷ company_cost (%) |
| Token 效率 | user_tokens ÷ user_runs |
| 效率评分 | Step 3D |
| Z-Score | Step 3E |
| 主要场景 | 按 run 数排名第一的场景 |
| 用户画像 | 来自 persona 数据 |
| 风险标签 | 高成本异常 / 画像错位 / 过度集中 / 正常 |

汇总分层统计表（Expert / Advanced / Intermediate / Beginner × 人数 / 占比 / Run 占比 / 成本占比 / 均 tokens/run / 效率评分均值）。

---

## Step 6 — 场景与标签分析 {#step6}

**场景分析：**
- 分布表：场景 / runs / cost / run_share / cost_share / top_user
- 场景 HHI（来自 Step 4）
- 增长信号：若有环比数据，标记增长 vs 下降场景

**标签分析：**
- Top-20 标签按 run 数排序及占比
- 标签 × 分层映射（每个 Top-10 标签主要被哪个熟练度层级使用）
- 标签共现提示（若数据允许，识别 2–3 个高频配对标签）

**内容分类聚合：**
- 将标签归入 4–6 个元类别（如：工业生产 / 数据分析 / 文档协作 / 代码开发 / 其他）
- 计算每个元类别的成本占比

---

## Step 7 — 交叉维度分析 {#step7}

每个维度产出一张**命名发现卡**（含指标值、分类徽章、推荐行动）：

### 7A. 成本驱动归因
- Top-5 用户成本占比 + 主要场景映射
- 用户级 HHI；Top-3 > 50% → "成本高度集中 [Risk]"

### 7B. 场景 × 用户依赖矩阵
- 每个 Top-5 场景：Top-3 贡献用户及其占比
- 场景内 HHI > 5000 → "场景单点依赖 [Risk]"
- 零 Expert/Advanced 用户的场景 → "高价值场景人才空白 [Alert]"
- 10+ 用户的场景 → "场景已规模化普及 [Positive]"

### 7C. 熟练度 × 效率差距
- Expert / Beginner 效率比
  - 比值 > 1.5 → "高阶用户效率优势显著 [Positive]"
  - 比值 < 1.1 → "效率分层不明显 [Alert]"
- Beginner z-score > 1.5 → "初级用户异常高消耗 [Risk]"
- 估算：若所有 Beginner 提升至 Intermediate 效率，可节省 tokens/成本多少

### 7D. 画像 × 场景对齐
- 交叉映射画像标签与主要场景
- 轻量探索者 + Top-5 成本 → "画像-消耗错位 [Alert]"
- 未分类用户（缺少画像）→ 数据质量缺口

### 7E. 活跃用户集中度与平台渗透
- Top-10% 用户 runs 占比
- Gini + Pareto 结果（来自 Step 3）
- 分类：Gini < 0.4 + Top-20% < 60% → 健康；Gini > 0.6 → 严重集中

### 7F. 趋势归因
- DoD 环比：哪个分层贡献了 runs 增/减？
- 成本增加驱动因素：(a) 更多用户 / (b) 已有用户更多使用 / (c) tokens/run 上升
- 标记主要驱动：Volume-Driven / Efficiency-Driven / New-User-Driven

### 7G. 统计异常用户
- 列出所有 z > 2.5 的用户（成本、场景、画像、分层）
- 0 异常 → "无统计异常用户 [Positive]"

### 7H. 场景 ROI 代理
- 按业务价值分层：industrial-critical / analytical / operational / exploratory
- exploratory > 40% 成本且用户 < 20% → "高探索性消耗 [Alert]"
- industrial-critical < 20% 且相关部门存在 → "核心业务场景渗透不足 [Risk]"

### 7I. 效率优化量化
- 底部 25% 效率 + 成本占比 > 5% 的用户
- 估算若提升至 P50 效率可节省：`$X.XX / day` 或 `~X%`

---

## Step 8 — 平台健康评分 {#step8}

| 维度 | 权重 | 评分逻辑 |
|---|---|---|
| 成本稳定性（DoD 变化） | 20% | 100 if Δ<5%；线性衰减至 Δ>50% 时为 0 |
| 用户分布（Gini） | 20% | 100 if Gini<0.3；线性衰减至 Gini>0.8 时为 0 |
| 场景多样性（HHI） | 15% | 100 if HHI<1500；衰减至 HHI>5000 时为 0 |
| 专家层成本占比 | 15% | 100 if Expert+Advanced > 50% 成本 |
| 异常用户数 | 15% | 100 if 0 个异常；每个异常 -20，最多 -100 |
| 风险标签数 | 15% | 100 if 0 个 Risk；每个 -15 |

颜色：80–100 = 健康(绿) / 60–79 = 良好(蓝) / 40–59 = 待改善(橙) / <40 = 告警(红)

---

## Step 9 — 风险与行动矩阵 {#step9}

整合 Step 4–7 所有风险标记为一张表：

| Risk ID | 维度 | 风险标签 | 指标依据 | 严重性 | 影响 | 行动 | 负责人 | 目标日期 |
|---|---|---|---|---|---|---|---|---|

严重性：P0（今日）/ P1（本周）/ P2（本月）
影响：High / Medium / Low

---

## Step 10 — HTML 报告组装 {#step10}

按 [html-report-spec.md](html-report-spec.md) 中的规范生成完整 HTML 文档。

**必检清单（输出前验证）：**
- [ ] 全部 10 个必需章节齐全
- [ ] 全部 10 个图表为内联 SVG/CSS（无外部依赖）
- [ ] 全部 9 个交叉分析（7A–7I）含指标值 + 分类 + 行动
- [ ] 平台健康评分已计算并展示分维度得分
- [ ] Gini 系数 + Lorenz 曲线已展示
- [ ] P50/P75/P90/P99 已计算并展示
- [ ] 风险矩阵所有条目含严重性/影响/行动/负责人/目标日期
- [ ] 用户分层覆盖全部四层（无数据显示 0）
- [ ] HTML 自包含，无外部资源
- [ ] 所有数值来自 MCP 工具返回，无硬编码
- [ ] 侧边栏导航链接全部对应文档内 `id` 锚点
- [ ] 超过 10 行的表格有固定表头
- [ ] 包含打印 CSS
