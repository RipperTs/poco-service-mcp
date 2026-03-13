from __future__ import annotations

from datetime import date
from typing import Literal

import httpx
from fastmcp.server.dependencies import get_http_request

from app.core.settings import Settings


class BackendAnalyticsClient:
    """HTTP client for backend admin analytics APIs."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.backend_base_url.rstrip("/")
        self._fallback_admin_api_key = settings.backend_admin_api_key.strip()
        self._fallback_global_api_key = settings.backend_global_api_key.strip()
        self._timeout = float(settings.backend_timeout_seconds)

    async def get_daily_overview(
        self,
        *,
        day: date,
        timezone_name: str,
        top_limit: int,
    ) -> dict:
        return await self._request(
            path="/admin/analytics/daily-overview",
            params={
                "day": day.isoformat(),
                "timezone": timezone_name,
                "top_limit": top_limit,
            },
        )

    async def get_daily_users(
        self,
        *,
        day: date,
        timezone_name: str,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._request(
            path="/admin/analytics/daily-users",
            params={
                "day": day.isoformat(),
                "timezone": timezone_name,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_daily_scenarios(
        self,
        *,
        day: date,
        timezone_name: str,
        top_limit: int,
        user_id: str | None = None,
    ) -> dict:
        params: dict[str, str | int] = {
            "day": day.isoformat(),
            "timezone": timezone_name,
            "top_limit": top_limit,
        }
        if user_id:
            params["user_id"] = user_id

        return await self._request(
            path="/admin/analytics/daily-scenarios",
            params=params,
        )

    async def get_daily_content_taxonomy(
        self,
        *,
        day: date,
        timezone_name: str,
        top_limit: int,
        user_id: str | None = None,
    ) -> dict:
        params: dict[str, str | int] = {
            "day": day.isoformat(),
            "timezone": timezone_name,
            "top_limit": top_limit,
        }
        if user_id:
            params["user_id"] = user_id
        return await self._request(
            path="/admin/analytics/daily-content-taxonomy",
            params=params,
        )

    async def get_daily_user_proficiency(
        self,
        *,
        day: date,
        timezone_name: str,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._request(
            path="/admin/analytics/daily-user-proficiency",
            params={
                "day": day.isoformat(),
                "timezone": timezone_name,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_daily_user_personas(
        self,
        *,
        day: date,
        timezone_name: str,
        limit: int,
        offset: int,
    ) -> dict:
        return await self._request(
            path="/admin/analytics/daily-user-personas",
            params={
                "day": day.isoformat(),
                "timezone": timezone_name,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_daily_report_dataset(
        self,
        *,
        day: date,
        timezone_name: str,
        top_limit: int,
        user_limit: int,
        user_offset: int,
    ) -> dict:
        return await self._request(
            path="/admin/analytics/daily-report-dataset",
            params={
                "day": day.isoformat(),
                "timezone": timezone_name,
                "top_limit": top_limit,
                "user_limit": user_limit,
                "user_offset": user_offset,
            },
        )

    async def _request(self, *, path: str, params: dict[str, str | int]) -> dict:
        headers = self._build_auth_headers(required_scope="admin")

        url = f"{self._base_url}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=params, headers=headers)

        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Invalid backend response payload")

        code = int(payload.get("code", -1))
        if code != 0:
            message = str(payload.get("message") or "Backend API error")
            raise RuntimeError(message)

        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Backend response data is empty")
        return data

    @staticmethod
    def _normalize_authorization(raw: str) -> str:
        value = raw.strip()
        if not value:
            return ""
        if value.lower().startswith("bearer "):
            return value
        return f"Bearer {value}"

    @staticmethod
    def _pick_header_value(request_headers: object, keys: list[str]) -> str:
        getter = getattr(request_headers, "get", None)
        if getter is None:
            return ""
        for key in keys:
            value = str(getter(key, "") or "").strip()
            if value:
                return value
        return ""

    def _build_auth_headers(
        self, *, required_scope: Literal["admin", "global"]
    ) -> dict[str, str]:
        request = None
        try:
            request = get_http_request()
        except RuntimeError:
            request = None

        if request is not None:
            inbound_admin_key = self._pick_header_value(
                request.headers,
                [
                    "BACKEND_ADMIN_API_KEY",
                    "X-BACKEND-ADMIN-API-KEY",
                ],
            )
            inbound_global_key = self._pick_header_value(
                request.headers,
                [
                    "BACKEND_GLOBAL_API_KEY",
                    "X-BACKEND-GLOBAL-API-KEY",
                ],
            )
            inbound_authorization = self._pick_header_value(
                request.headers,
                ["Authorization"],
            )

            if required_scope == "admin":
                if inbound_admin_key:
                    return {
                        "Authorization": self._normalize_authorization(inbound_admin_key)
                    }
                if inbound_authorization:
                    return {"Authorization": inbound_authorization}
            else:
                if inbound_global_key:
                    return {
                        "Authorization": self._normalize_authorization(inbound_global_key)
                    }
                if inbound_admin_key:
                    return {
                        "Authorization": self._normalize_authorization(inbound_admin_key)
                    }
                if inbound_authorization:
                    return {"Authorization": inbound_authorization}

        if required_scope == "admin":
            if self._fallback_admin_api_key:
                return {
                    "Authorization": self._normalize_authorization(
                        self._fallback_admin_api_key
                    )
                }
        else:
            if self._fallback_global_api_key:
                return {
                    "Authorization": self._normalize_authorization(
                        self._fallback_global_api_key
                    )
                }
            if self._fallback_admin_api_key:
                return {
                    "Authorization": self._normalize_authorization(
                        self._fallback_admin_api_key
                    )
                }

        if required_scope == "admin":
            raise RuntimeError(
                "Missing admin API key. Provide BACKEND_ADMIN_API_KEY header "
                "or fallback BACKEND_ADMIN_API_KEY env."
            )
        raise RuntimeError(
            "Missing global API key. Provide BACKEND_GLOBAL_API_KEY/BACKEND_ADMIN_API_KEY header "
            "or fallback BACKEND_GLOBAL_API_KEY/BACKEND_ADMIN_API_KEY env."
        )
