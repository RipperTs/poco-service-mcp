from __future__ import annotations

from datetime import date
from typing import Annotated

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from app.services.analytics_service import AnalyticsToolService

_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def create_analysis_server(
    service: AnalyticsToolService,
) -> FastMCP:
    server = FastMCP("Poco Analytics Tools")

    @server.tool(
        description=(
            "汇总指定日期的公司级使用情况，返回工作量、Token、成本、环比变化与主要场景。"
        ),
        tags={"analytics", "daily", "company", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_company_daily_usage(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        top_limit: Annotated[
            int | None,
            Field(
                default=None,
                ge=1,
                le=50,
                description="返回的高占比场景数量上限，范围 1-50；为空时使用默认值。",
            ),
        ] = None,
    ) -> dict:
        """Get company-level daily usage summary, deltas, and top scenarios."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_company_daily_usage(
            day=parsed_day,
            timezone_name=timezone,
            top_limit=top_limit,
        )
        return data

    @server.tool(
        description=(
            "查询指定日期的用户使用明细列表，包含每个用户的调用量、Token 和成本占比。"
        ),
        tags={"analytics", "daily", "user", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_user_daily_usage(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                default=50,
                ge=1,
                le=500,
                description="分页大小，范围 1-500。",
            ),
        ] = 50,
        offset: Annotated[
            int,
            Field(
                default=0,
                ge=0,
                description="分页偏移量，从 0 开始。",
            ),
        ] = 0,
    ) -> dict:
        """Get user-level daily usage list with cost and token shares."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_user_daily_usage(
            day=parsed_day,
            timezone_name=timezone,
            limit=limit,
            offset=offset,
        )
        return data

    @server.tool(
        description=(
            "获取指定日期的场景分布，可按公司维度或指定 user_id 维度查看场景贡献。"
        ),
        tags={"analytics", "daily", "scenario", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_usage_scenarios(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        user_id: Annotated[
            str | None,
            Field(
                default=None,
                description="可选用户 ID；不传则返回公司整体场景分布。",
            ),
        ] = None,
        top_limit: Annotated[
            int | None,
            Field(
                default=None,
                ge=1,
                le=50,
                description="返回场景数量上限，范围 1-50；为空时使用默认值。",
            ),
        ] = None,
    ) -> dict:
        """Get scenario distribution for a specific day (company or one user)."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_usage_scenarios(
            day=parsed_day,
            timezone_name=timezone,
            user_id=user_id,
            top_limit=top_limit,
        )
        return data

    @server.tool(
        description=(
            "生成指定日期的专业日报分析摘要，包含关键发现与可执行优化建议。"
        ),
        tags={"analytics", "daily", "report", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_daily_analysis_brief(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        top_limit: Annotated[
            int | None,
            Field(
                default=None,
                ge=1,
                le=50,
                description="分析时使用的主要场景数量上限，范围 1-50；为空时使用默认值。",
            ),
        ] = None,
    ) -> dict:
        """Generate a concise daily analysis brief with findings and recommendations."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_daily_analysis_brief(
            day=parsed_day,
            timezone_name=timezone,
            top_limit=top_limit,
        )
        return data

    @server.tool(
        description=(
            "分析指定日期的内容分类与标签分布，输出公司或指定用户的场景分类、标签占比和用户偏好。"
        ),
        tags={"analytics", "daily", "taxonomy", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_daily_content_taxonomy(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        user_id: Annotated[
            str | None,
            Field(
                default=None,
                description="可选用户 ID；不传则返回公司整体分类标签分析。",
            ),
        ] = None,
        top_limit: Annotated[
            int | None,
            Field(
                default=None,
                ge=1,
                le=50,
                description="返回分类/标签 Top 数量上限，范围 1-50；为空时使用默认值。",
            ),
        ] = None,
    ) -> dict:
        """Get daily content taxonomy and label distribution."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_daily_content_taxonomy(
            day=parsed_day,
            timezone_name=timezone,
            user_id=user_id,
            top_limit=top_limit,
        )
        return data

    @server.tool(
        description=(
            "输出指定日期的用户熟练度评估，包含评分、分层、主导场景、标签偏好和改进建议。"
        ),
        tags={"analytics", "daily", "proficiency", "user", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_daily_user_proficiency(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                default=50,
                ge=1,
                le=500,
                description="分页大小，范围 1-500。",
            ),
        ] = 50,
        offset: Annotated[
            int,
            Field(
                default=0,
                ge=0,
                description="分页偏移量，从 0 开始。",
            ),
        ] = 0,
    ) -> dict:
        """Get daily user proficiency ranking and scoring details."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_daily_user_proficiency(
            day=parsed_day,
            timezone_name=timezone,
            limit=limit,
            offset=offset,
        )
        return data

    @server.tool(
        description=(
            "输出指定日期的用户行为画像，包含画像标签、活跃时段、行为信号和风险提示。"
        ),
        tags={"analytics", "daily", "persona", "user", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_daily_user_personas(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                default=50,
                ge=1,
                le=500,
                description="分页大小，范围 1-500。",
            ),
        ] = 50,
        offset: Annotated[
            int,
            Field(
                default=0,
                ge=0,
                description="分页偏移量，从 0 开始。",
            ),
        ] = 0,
    ) -> dict:
        """Get daily user personas and behavior insights."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_daily_user_personas(
            day=parsed_day,
            timezone_name=timezone,
            limit=limit,
            offset=offset,
        )
        return data

    @server.tool(
        description=(
            "一次返回日报分析所需数据集，包含公司维度、用户维度、场景分类、标签、熟练度和画像。"
        ),
        tags={"analytics", "daily", "report", "dataset", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    async def get_daily_report_dataset(
        day: Annotated[
            str,
            Field(description="统计日期，ISO 格式 YYYY-MM-DD。"),
        ],
        timezone: Annotated[
            str | None,
            Field(
                default=None,
                description="IANA 时区名称，例如 Asia/Shanghai；为空时使用服务默认时区。",
            ),
        ] = None,
        top_limit: Annotated[
            int | None,
            Field(
                default=None,
                ge=1,
                le=50,
                description="场景/标签 Top 数量上限，范围 1-50；为空时使用默认值。",
            ),
        ] = None,
        user_limit: Annotated[
            int,
            Field(
                default=100,
                ge=1,
                le=500,
                description="用户维度分页大小，范围 1-500。",
            ),
        ] = 100,
        user_offset: Annotated[
            int,
            Field(
                default=0,
                ge=0,
                description="用户维度分页偏移量，从 0 开始。",
            ),
        ] = 0,
    ) -> dict:
        """Get a full daily report dataset for professional HTML report generation."""
        parsed_day = date.fromisoformat(day)
        data = await service.get_daily_report_dataset(
            day=parsed_day,
            timezone_name=timezone,
            top_limit=top_limit,
            user_limit=user_limit,
            user_offset=user_offset,
        )
        return data

    return server
