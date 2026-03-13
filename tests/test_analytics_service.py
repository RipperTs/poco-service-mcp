from __future__ import annotations

from datetime import date, timedelta

import httpx
import pytest
from fastmcp import FastMCP

from app.clients.backend_client import BackendAnalyticsClient
from app.core.settings import Settings
from app.services.analytics_service import AnalyticsToolService
from app.tools.admin_tools import create_management_server
from app.tools.analysis_tools import create_analysis_server


def _resolve_settings() -> Settings:
    return Settings()


def _probe_admin_analytics_access(settings: Settings) -> tuple[bool, str]:
    api_key = settings.backend_admin_api_key.strip()
    if not api_key:
        return False, "missing BACKEND_ADMIN_API_KEY"

    headers = {"Authorization": f"Bearer {api_key}"}

    url = f"{settings.backend_base_url.rstrip('/')}/admin/analytics/daily-overview"
    params = {
        "day": _build_test_day(),
        "timezone": settings.analytics_default_timezone,
        "top_limit": 1,
    }
    try:
        response = httpx.get(
            url,
            params=params,
            headers=headers,
            timeout=float(settings.backend_timeout_seconds),
        )
    except httpx.HTTPError as exc:
        return False, f"backend unavailable: {exc}"

    if response.status_code == 200:
        return True, ""
    return False, f"{response.status_code} {response.text[:200]}"


def _build_mcp_server(settings: Settings) -> FastMCP:
    client = BackendAnalyticsClient(settings)
    service = AnalyticsToolService(client, settings)

    root = FastMCP(settings.mcp_service_name)
    root.mount(create_analysis_server(service), namespace="analysis")
    root.mount(create_management_server(settings), namespace="management")
    return root


def _build_test_day() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


async def _call_tool(server: FastMCP, *, name: str, arguments: dict) -> dict:
    result = await server.call_tool(name, arguments)
    payload = result.structured_content
    assert isinstance(payload, dict), f"Tool {name} should return dict payload"
    return payload


@pytest.fixture(scope="module")
def settings() -> Settings:
    settings = _resolve_settings()
    if not settings.backend_admin_api_key.strip():
        pytest.fail("BACKEND_ADMIN_API_KEY is required for integration tests")

    ok, reason = _probe_admin_analytics_access(settings)
    if not ok:
        pytest.fail(f"Admin analytics probe failed with current key/token: {reason}")
    return settings


@pytest.fixture(scope="module")
def mcp_server(settings: Settings) -> FastMCP:
    return _build_mcp_server(settings)


@pytest.mark.asyncio
async def test_list_all_exposed_tools(mcp_server: FastMCP) -> None:
    tools = await mcp_server.list_tools()
    tool_names = {item.name for item in tools}
    assert tool_names >= {
        "analysis_get_company_daily_usage",
        "analysis_get_user_daily_usage",
        "analysis_get_usage_scenarios",
        "analysis_get_daily_analysis_brief",
        "analysis_get_daily_content_taxonomy",
        "analysis_get_daily_user_proficiency",
        "analysis_get_daily_user_personas",
        "analysis_get_daily_report_dataset",
        "management_ping",
        "management_describe_service",
    }


@pytest.mark.asyncio
async def test_management_ping(mcp_server: FastMCP, settings: Settings) -> None:
    data = await _call_tool(
        mcp_server,
        name="management_ping",
        arguments={},
    )
    assert data["status"] == "ok"
    assert data["service"] == settings.mcp_service_name
    assert isinstance(data["timestamp"], str)


@pytest.mark.asyncio
async def test_management_describe_service(mcp_server: FastMCP, settings: Settings) -> None:
    data = await _call_tool(
        mcp_server,
        name="management_describe_service",
        arguments={},
    )
    assert data["service"] == settings.mcp_service_name
    assert data["transport"] == settings.mcp_transport
    assert data["backend_base_url"] == settings.backend_base_url
    assert data["default_timezone"] == settings.analytics_default_timezone


@pytest.mark.asyncio
async def test_analysis_get_company_daily_usage(mcp_server: FastMCP, settings: Settings) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_company_daily_usage",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "top_limit": 5,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert isinstance(data["summary"], dict)
    assert isinstance(data["delta"], dict)
    assert isinstance(data["top_scenarios"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_user_daily_usage(mcp_server: FastMCP, settings: Settings) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_user_daily_usage",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "limit": 20,
            "offset": 0,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert isinstance(data["total"], int)
    assert isinstance(data["users"], list)


@pytest.mark.asyncio
async def test_analysis_get_usage_scenarios_company_scope(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_usage_scenarios",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "top_limit": 10,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["user_id"] is None
    assert isinstance(data["scenarios"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_usage_scenarios_user_scope(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    users_data = await _call_tool(
        mcp_server,
        name="analysis_get_user_daily_usage",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "limit": 1,
            "offset": 0,
        },
    )
    users = users_data.get("users") or []
    user_id = str(users[0]["user_id"]) if users else "00000000-0000-0000-0000-000000000000"

    data = await _call_tool(
        mcp_server,
        name="analysis_get_usage_scenarios",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "user_id": user_id,
            "top_limit": 10,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["user_id"] == user_id
    assert isinstance(data["scenarios"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_daily_analysis_brief(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_daily_analysis_brief",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "top_limit": 5,
        },
    )

    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert isinstance(data["summary"], dict)
    assert isinstance(data["scenarios"], list)
    assert isinstance(data["key_findings"], list)
    assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_analysis_get_daily_content_taxonomy(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_daily_content_taxonomy",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "top_limit": 10,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["user_id"] is None
    assert isinstance(data["categories"], list)
    assert isinstance(data["tags"], list)
    assert isinstance(data["user_preferences"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_daily_user_proficiency(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_daily_user_proficiency",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "limit": 20,
            "offset": 0,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert isinstance(data["total"], int)
    assert isinstance(data["users"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_daily_user_personas(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_daily_user_personas",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "limit": 20,
            "offset": 0,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert isinstance(data["total"], int)
    assert isinstance(data["personas"], list)
    assert isinstance(data["insights"], list)


@pytest.mark.asyncio
async def test_analysis_get_daily_report_dataset(
    mcp_server: FastMCP, settings: Settings
) -> None:
    test_day = _build_test_day()
    data = await _call_tool(
        mcp_server,
        name="analysis_get_daily_report_dataset",
        arguments={
            "day": test_day,
            "timezone": settings.analytics_default_timezone,
            "top_limit": 10,
            "user_limit": 50,
            "user_offset": 0,
        },
    )
    assert data["day"] == test_day
    assert data["timezone"] == settings.analytics_default_timezone
    assert isinstance(data["company_overview"], dict)
    assert isinstance(data["user_overview"], dict)
    assert isinstance(data["scenario_overview"], dict)
    assert isinstance(data["taxonomy"], dict)
    assert isinstance(data["user_proficiency"], dict)
    assert isinstance(data["user_personas"], dict)
