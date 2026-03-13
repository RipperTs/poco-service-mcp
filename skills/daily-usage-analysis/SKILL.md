---
name: daily-usage-analysis
description: >
  Agent 平台使用分析技能。凡涉及 Agent 平台的使用情况分析，均必须优先触发此技能，包括但不限于：
  查看/分析今日、昨日、本周、上周、本月、某天、某段时间的 runs/sessions/时长、Token 用量、USD 成本、
  场景分布、用户排行、使用趋势、环比对比、风险诊断、优化建议等。
  支持两种模式：
  (1) 单日模式 — 指定某一天，生成多维度 HTML 智能日报（公司维度 + 用户维度 + 场景标签 + 交叉分析 + 健康评分 + 风险矩阵）；
  (2) 区间模式 — 指定日期范围（如本周、本月、任意起止日），逐日拉取数据，汇总趋势并生成 HTML 区间分析报告。
  TRIGGER EXAMPLES: "分析今天的使用情况", "本周 agent 用了多少", "上个月成本怎么样", "看看用户使用趋势",
  "帮我出一份日报", "哪些场景用得最多", "有没有异常用户", "token 消耗情况".
---

# Agent 平台使用分析

## 模式判断

根据用户请求自动选择模式：

| 用户意图 | 模式 | 参考文档 |
|---|---|---|
| 某一天（今天/昨天/具体日期） | **单日模式** | [single-day-workflow.md](references/single-day-workflow.md) |
| 时间段（本周/上周/本月/起止日期） | **区间模式** | [range-analysis.md](references/range-analysis.md) |

日期模糊时，优先询问或合理推断（如"本周"= 周一至今）。

## 默认参数

| 参数 | 默认值 |
|---|---|
| `timezone` | `Asia/Shanghai` |
| `top_limit` | `20` |
| `user_limit` | `100` |

## 工具清单

**主工具（优先调用）：**
- `analysis_get_daily_report_dataset` — 单日全量数据一次性拉取

**补充工具：**

| 工具 | 用途 |
|---|---|
| `analysis_get_company_daily_usage` | 公司级汇总（区间模式逐日调用此工具） |
| `analysis_get_user_daily_usage` | 用户列表 |
| `analysis_get_usage_scenarios` | 场景分布 |
| `analysis_get_daily_analysis_brief` | AI 叙述摘要 |
| `analysis_get_daily_content_taxonomy` | 内容标签分布 |
| `analysis_get_daily_user_proficiency` | 熟练度评分 |
| `analysis_get_daily_user_personas` | 用户画像标签 |

## 输出要求

- 所有分析结果必须以**自包含单页 HTML 文档**输出，保存到 `/workspace/`
- **绝对禁止**只返回 Markdown 文字分析而不产出 HTML 文件，无论用户是否明确说"生成报告"
- 文件命名：`agent_report_<日期或区间>_<生成时间戳>.html`
- HTML 规范见 [html-report-spec.md](references/html-report-spec.md)
- 产出 HTML 后，必须在回复中告知文件路径

## 执行入口

- **第一步（必须）**：读取对应的参考文档，严格按工作流执行，不得跳过
- **单日分析** → 读取 [references/single-day-workflow.md](references/single-day-workflow.md)，执行 Step 1–10
- **区间分析** → 读取 [references/range-analysis.md](references/range-analysis.md)，执行区间工作流

## 常见错误（必须避免）

1. ❌ 直接手动调用 analytics 工具后返回 Markdown 分析 — 必须走技能流程产出 HTML
2. ❌ HTML 的 body 同时设置 `display:grid` 且 sidebar 用 `position:fixed` — 会导致内容区被压缩至极窄（见 html-report-spec.md 布局规范）
3. ❌ 未读参考文档就开始写 HTML — 必须先读规范再动手
