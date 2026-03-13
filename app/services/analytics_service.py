from __future__ import annotations

from datetime import date

from app.clients.backend_client import BackendAnalyticsClient
from app.core.settings import Settings
from app.schemas.analytics import DailyBriefResponse


class AnalyticsToolService:
    """Domain service for MCP analytics tools."""

    def __init__(self, client: BackendAnalyticsClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def get_company_daily_usage(
        self,
        *,
        day: date,
        timezone_name: str | None,
        top_limit: int | None,
    ) -> dict:
        return await self._client.get_daily_overview(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            top_limit=self._resolve_top_limit(top_limit),
        )

    async def get_user_daily_usage(
        self,
        *,
        day: date,
        timezone_name: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._client.get_daily_users(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            limit=max(1, min(limit, 500)),
            offset=max(0, offset),
        )

    async def get_usage_scenarios(
        self,
        *,
        day: date,
        timezone_name: str | None,
        user_id: str | None,
        top_limit: int | None,
    ) -> dict:
        return await self._client.get_daily_scenarios(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            user_id=user_id,
            top_limit=self._resolve_top_limit(top_limit),
        )

    async def get_daily_analysis_brief(
        self,
        *,
        day: date,
        timezone_name: str | None,
        top_limit: int | None,
    ) -> dict:
        resolved_tz = self._resolve_timezone(timezone_name)
        resolved_top_limit = self._resolve_top_limit(top_limit)

        overview = await self._client.get_daily_overview(
            day=day,
            timezone_name=resolved_tz,
            top_limit=resolved_top_limit,
        )
        scenarios_resp = await self._client.get_daily_scenarios(
            day=day,
            timezone_name=resolved_tz,
            top_limit=resolved_top_limit,
            user_id=None,
        )

        summary = overview.get("summary") or {}
        delta = overview.get("delta") or {}
        scenarios = scenarios_resp.get("scenarios") or []
        key_findings = self._build_key_findings(
            summary=summary,
            delta=delta,
            scenarios=scenarios,
        )
        recommendations = self._build_recommendations(summary=summary, scenarios=scenarios)

        brief = DailyBriefResponse(
            day=day.isoformat(),
            timezone=resolved_tz,
            summary=summary,
            scenarios=scenarios,
            key_findings=key_findings,
            recommendations=recommendations,
        )
        return brief.model_dump()

    async def get_daily_content_taxonomy(
        self,
        *,
        day: date,
        timezone_name: str | None,
        user_id: str | None,
        top_limit: int | None,
    ) -> dict:
        return await self._client.get_daily_content_taxonomy(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            user_id=user_id,
            top_limit=self._resolve_top_limit(top_limit),
        )

    async def get_daily_user_proficiency(
        self,
        *,
        day: date,
        timezone_name: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._client.get_daily_user_proficiency(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            limit=max(1, min(limit, 500)),
            offset=max(0, offset),
        )

    async def get_daily_user_personas(
        self,
        *,
        day: date,
        timezone_name: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._client.get_daily_user_personas(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            limit=max(1, min(limit, 500)),
            offset=max(0, offset),
        )

    async def get_daily_report_dataset(
        self,
        *,
        day: date,
        timezone_name: str | None,
        top_limit: int | None,
        user_limit: int,
        user_offset: int,
    ) -> dict:
        return await self._client.get_daily_report_dataset(
            day=day,
            timezone_name=self._resolve_timezone(timezone_name),
            top_limit=self._resolve_top_limit(top_limit),
            user_limit=max(1, min(user_limit, 500)),
            user_offset=max(0, user_offset),
        )

    def _resolve_timezone(self, timezone_name: str | None) -> str:
        value = (timezone_name or "").strip()
        if value:
            return value
        return self._settings.analytics_default_timezone

    def _resolve_top_limit(self, top_limit: int | None) -> int:
        if top_limit is None:
            return max(1, min(self._settings.analytics_default_top_limit, 50))
        return max(1, min(top_limit, 50))

    @staticmethod
    def _build_key_findings(
        *,
        summary: dict,
        delta: dict,
        scenarios: list[dict],
    ) -> list[str]:
        findings: list[str] = []
        total_runs = int(summary.get("total_runs") or 0)
        active_users = int(summary.get("active_users") or 0)
        total_cost = float(summary.get("total_cost_usd") or 0.0)

        findings.append(
            f"当日总运行 {total_runs} 次，活跃用户 {active_users} 人，总成本 ${total_cost:.4f}。"
        )

        if scenarios:
            top_scene = scenarios[0]
            scene_name = str(top_scene.get("scene_name") or top_scene.get("scene_key") or "未知")
            cost_share = float(top_scene.get("cost_share_ratio") or 0.0)
            findings.append(f"成本占比最高场景是“{scene_name}”，占比 {cost_share:.1%}。")

        cost_delta = delta.get("cost_vs_prev_day_ratio")
        if isinstance(cost_delta, int | float):
            findings.append(f"成本较昨日变化 {float(cost_delta):+.1%}。")

        return findings

    @staticmethod
    def _build_recommendations(*, summary: dict, scenarios: list[dict]) -> list[str]:
        recommendations: list[str] = []

        avg_cost_per_run = float(summary.get("avg_cost_per_run_usd") or 0.0)
        if avg_cost_per_run >= 0.05:
            recommendations.append("建议排查高成本会话，优先优化提示词和上下文长度。")

        if scenarios:
            top_scene = scenarios[0]
            scene_name = str(top_scene.get("scene_name") or "未知")
            recommendations.append(
                f"针对“{scene_name}”建立标准化模板，降低重复输入并提高复用率。"
            )

        if not recommendations:
            recommendations.append("整体使用健康，建议持续观察连续 7 天趋势再做策略调整。")

        return recommendations
