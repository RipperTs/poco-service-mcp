# Poco MCP Service

独立 MCP 服务模块（目录内自洽），用于承载 Poco 的多类型 MCP 工具。

## 目录结构

- `app/core`：配置与基础设施
- `app/clients`：后端 API 客户端
- `app/schemas`：结构化输出模型
- `app/services`：工具编排与分析逻辑
- `app/tools`：MCP tools（按领域拆分）
- `app/main.py`：MCP 入口，挂载多子服务
- `skills`：面向 AI 的调用与分析技能文档

## 快速启动

```bash
cd mcp_service
uv sync
uv run python -m app.main
```

默认使用 `http` 传输（`0.0.0.0:8090`）。如需 `stdio`：

```bash
MCP_TRANSPORT=stdio uv run python -m app.main
```

认证建议：

- 推荐通过 MCP headers 透传用户自己的 API Key（可同时传 admin/global）。
- `BACKEND_ADMIN_API_KEY` 作为无 HTTP 请求上下文时的可选回退（例如本地直连测试）。
- 可选配置 `BACKEND_GLOBAL_API_KEY`（global-scope 工具或回退场景使用）。

## 可用工具（当前）

- `analysis_get_company_daily_usage`
- `analysis_get_user_daily_usage`
- `analysis_get_usage_scenarios`
- `analysis_get_daily_analysis_brief`
- `analysis_get_daily_content_taxonomy`
- `analysis_get_daily_user_proficiency`
- `analysis_get_daily_user_personas`
- `analysis_get_daily_report_dataset`
- `management_ping`
- `management_describe_service`

## MCP 服务配置示例
```json
{
  "mcpServers": {
    "poco_analytics": {
      "type": "http",
      "url": "${MCP_ANALYTICS_HTTP_URL:-http://host.docker.internal:8090/mcp}",
      "headers": {
        "BACKEND_ADMIN_API_KEY": "${MCP_ANALYTICS_ADMIN_API_KEY}",
        "BACKEND_GLOBAL_API_KEY": "${MCP_ANALYTICS_GLOBAL_API_KEY:-}"
      }
    }
  }
}
```

说明：
- `"/workspace/mcp_service"` 是 **容器内路径**，仅在 `stdio + command` 启动模式需要。
- 当前推荐 `http` 方式接入，不再需要在 MCP Server 配置里写 `command/args`。
- `MCP_ANALYTICS_ADMIN_API_KEY` / `MCP_ANALYTICS_GLOBAL_API_KEY` 建议配置为**用户级环境变量**。
- `mcp_service` 会优先读取来路 headers 中的 `BACKEND_ADMIN_API_KEY`、`BACKEND_GLOBAL_API_KEY`；同时兼容 `Authorization`。
- 仅在无 HTTP 请求上下文时，才回退 `BACKEND_ADMIN_API_KEY` / `BACKEND_GLOBAL_API_KEY`（便于本地直连测试）。
