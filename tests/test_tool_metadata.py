from __future__ import annotations

import pytest
from fastmcp import FastMCP

from app.clients.backend_client import BackendAnalyticsClient
from app.core.settings import Settings
from app.services.analytics_service import AnalyticsToolService
from app.tools.admin_tools import create_management_server
from app.tools.analysis_tools import create_analysis_server


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="module")
def root_server(settings: Settings) -> FastMCP:
    client = BackendAnalyticsClient(settings)
    service = AnalyticsToolService(client, settings)

    root = FastMCP(settings.mcp_service_name)
    root.mount(create_analysis_server(service), namespace="analysis")
    root.mount(create_management_server(settings), namespace="management")
    return root


def _assert_readonly_annotations(tool_dump: dict) -> None:
    annotations = tool_dump.get("annotations") or {}
    assert annotations.get("readOnlyHint") is True
    assert annotations.get("destructiveHint") is False
    assert annotations.get("idempotentHint") is True
    assert annotations.get("openWorldHint") is False


def _assert_parameter_descriptions(tool_dump: dict, param_names: list[str]) -> None:
    parameters = tool_dump.get("parameters") or {}
    properties = parameters.get("properties") or {}
    for name in param_names:
        descriptor = properties.get(name) or {}
        description = str(descriptor.get("description") or "").strip()
        assert description, f"Parameter '{name}' should include description"


def _extract_numeric_limits(descriptor: dict) -> tuple[int | None, int | None]:
    minimum = descriptor.get("minimum")
    maximum = descriptor.get("maximum")
    if minimum is not None or maximum is not None:
        return minimum, maximum

    any_of = descriptor.get("anyOf") or []
    if isinstance(any_of, list):
        for schema in any_of:
            if not isinstance(schema, dict):
                continue
            candidate_min = schema.get("minimum")
            candidate_max = schema.get("maximum")
            if candidate_min is not None or candidate_max is not None:
                return candidate_min, candidate_max

    return None, None


@pytest.mark.asyncio
async def test_all_tools_expose_metadata(root_server: FastMCP) -> None:
    expected_tools: dict[str, dict[str, object]] = {
        "analysis_get_company_daily_usage": {
            "tags": {"analytics", "daily", "company", "read"},
            "params": ["day", "timezone", "top_limit"],
            "limits": {"top_limit": (1, 50)},
        },
        "analysis_get_user_daily_usage": {
            "tags": {"analytics", "daily", "user", "read"},
            "params": ["day", "timezone", "limit", "offset"],
            "limits": {"limit": (1, 500), "offset": (0, None)},
        },
        "analysis_get_usage_scenarios": {
            "tags": {"analytics", "daily", "scenario", "read"},
            "params": ["day", "timezone", "user_id", "top_limit"],
            "limits": {"top_limit": (1, 50)},
        },
        "analysis_get_daily_analysis_brief": {
            "tags": {"analytics", "daily", "report", "read"},
            "params": ["day", "timezone", "top_limit"],
            "limits": {"top_limit": (1, 50)},
        },
        "analysis_get_daily_content_taxonomy": {
            "tags": {"analytics", "daily", "taxonomy", "read"},
            "params": ["day", "timezone", "user_id", "top_limit"],
            "limits": {"top_limit": (1, 50)},
        },
        "analysis_get_daily_user_proficiency": {
            "tags": {"analytics", "daily", "proficiency", "user", "read"},
            "params": ["day", "timezone", "limit", "offset"],
            "limits": {"limit": (1, 500), "offset": (0, None)},
        },
        "analysis_get_daily_user_personas": {
            "tags": {"analytics", "daily", "persona", "user", "read"},
            "params": ["day", "timezone", "limit", "offset"],
            "limits": {"limit": (1, 500), "offset": (0, None)},
        },
        "analysis_get_daily_report_dataset": {
            "tags": {"analytics", "daily", "report", "dataset", "read"},
            "params": ["day", "timezone", "top_limit", "user_limit", "user_offset"],
            "limits": {
                "top_limit": (1, 50),
                "user_limit": (1, 500),
                "user_offset": (0, None),
            },
        },
        "management_ping": {
            "tags": {"management", "health", "read"},
            "params": [],
            "limits": {},
        },
        "management_describe_service": {
            "tags": {"management", "config", "read"},
            "params": [],
            "limits": {},
        },
    }

    tools = await root_server.list_tools()
    tool_dump_map = {tool.name: tool.model_dump() for tool in tools}

    for tool_name, expected in expected_tools.items():
        assert tool_name in tool_dump_map
        tool_dump = tool_dump_map[tool_name]

        description = str(tool_dump.get("description") or "").strip()
        assert description, f"Tool '{tool_name}' should include description"

        expected_tags = expected["tags"]
        actual_tags = set(tool_dump.get("tags") or set())
        assert expected_tags.issubset(actual_tags)

        _assert_readonly_annotations(tool_dump)

        expected_params: list[str] = expected["params"]
        _assert_parameter_descriptions(tool_dump, expected_params)

        properties = (tool_dump.get("parameters") or {}).get("properties") or {}
        limits: dict[str, tuple[int | None, int | None]] = expected["limits"]
        for param_name, (min_value, max_value) in limits.items():
            descriptor = properties.get(param_name) or {}
            actual_min, actual_max = _extract_numeric_limits(descriptor)
            if min_value is not None:
                assert actual_min == min_value
            if max_value is not None:
                assert actual_max == max_value
