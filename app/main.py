from __future__ import annotations

from fastmcp import FastMCP

from app.clients.backend_client import BackendAnalyticsClient
from app.core.settings import get_settings
from app.services.analytics_service import AnalyticsToolService
from app.tools.admin_tools import create_management_server
from app.tools.analysis_tools import create_analysis_server


def create_mcp_server() -> FastMCP:
    settings = get_settings()

    client = BackendAnalyticsClient(settings)
    analytics_service = AnalyticsToolService(client, settings)

    root = FastMCP(settings.mcp_service_name)

    analysis_server = create_analysis_server(analytics_service)
    management_server = create_management_server(settings)

    root.mount(analysis_server, namespace="analysis")
    root.mount(management_server, namespace="management")

    return root


mcp = create_mcp_server()


if __name__ == "__main__":
    settings = get_settings()
    transport = settings.mcp_transport.lower().strip()

    if transport == "http":
        mcp.run(transport="http", host=settings.mcp_host, port=settings.mcp_port)
    else:
        mcp.run()
