from __future__ import annotations

from datetime import datetime, timezone

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from app.core.settings import Settings

_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def create_management_server(settings: Settings) -> FastMCP:
    server = FastMCP("Poco Management Tools")

    @server.tool(
        description="返回 MCP 服务健康状态与 UTC 时间戳，用于连通性检查。",
        tags={"management", "health", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    def ping() -> dict:
        """Health check for MCP service readiness."""
        return {
            "status": "ok",
            "service": settings.mcp_service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @server.tool(
        description="返回 MCP 服务运行配置摘要，包括传输方式、后端地址和默认时区。",
        tags={"management", "config", "read"},
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    def describe_service() -> dict:
        """Describe MCP service transport and backend connectivity config."""
        return {
            "service": settings.mcp_service_name,
            "transport": settings.mcp_transport,
            "backend_base_url": settings.backend_base_url,
            "default_timezone": settings.analytics_default_timezone,
        }

    return server
