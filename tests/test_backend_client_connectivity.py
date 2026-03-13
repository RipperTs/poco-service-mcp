from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from app.clients.backend_client import BackendAnalyticsClient
from app.core.settings import Settings


def _build_settings(
    *,
    admin_key: str = "sk-admin-fallback",
    global_key: str = "",
) -> Settings:
    base = Settings()
    return base.model_copy(
        update={
            "backend_base_url": "http://127.0.0.1:8000/api/v1",
            "backend_admin_api_key": admin_key,
            "backend_global_api_key": global_key,
            "backend_timeout_seconds": 3,
        }
    )


class _FakeResponse:
    def __init__(self) -> None:
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "code": 0,
            "message": "OK",
            "data": {"ok": True},
        }


class TestBackendAnalyticsClientConnectivity:
    def test_build_headers_prefers_admin_key_header(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = _build_settings(admin_key="sk-admin-fallback")
        client = BackendAnalyticsClient(settings)

        monkeypatch.setattr(
            "app.clients.backend_client.get_http_request",
            lambda: SimpleNamespace(
                headers={
                    "BACKEND_ADMIN_API_KEY": "sk-admin-from-header",
                    "Authorization": "Bearer should-not-win",
                }
            ),
        )

        headers = client._build_auth_headers(required_scope="admin")
        assert headers["Authorization"] == "Bearer sk-admin-from-header"

    def test_build_headers_uses_global_then_admin_for_global_scope(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = _build_settings(admin_key="sk-admin-fallback", global_key="sk-global-fallback")
        client = BackendAnalyticsClient(settings)

        monkeypatch.setattr(
            "app.clients.backend_client.get_http_request",
            lambda: SimpleNamespace(
                headers={
                    "BACKEND_GLOBAL_API_KEY": "sk-global-from-header",
                    "BACKEND_ADMIN_API_KEY": "sk-admin-from-header",
                }
            ),
        )
        headers = client._build_auth_headers(required_scope="global")
        assert headers["Authorization"] == "Bearer sk-global-from-header"

        monkeypatch.setattr(
            "app.clients.backend_client.get_http_request",
            lambda: SimpleNamespace(
                headers={
                    "BACKEND_ADMIN_API_KEY": "sk-admin-from-header",
                }
            ),
        )
        headers = client._build_auth_headers(required_scope="global")
        assert headers["Authorization"] == "Bearer sk-admin-from-header"

    def test_build_headers_fallback_when_no_http_context(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = _build_settings(admin_key="sk-admin-fallback", global_key="sk-global-fallback")
        client = BackendAnalyticsClient(settings)

        def _raise_runtime_error() -> None:
            raise RuntimeError("No active HTTP request found.")

        monkeypatch.setattr("app.clients.backend_client.get_http_request", _raise_runtime_error)

        admin_headers = client._build_auth_headers(required_scope="admin")
        assert admin_headers["Authorization"] == "Bearer sk-admin-fallback"

        global_headers = client._build_auth_headers(required_scope="global")
        assert global_headers["Authorization"] == "Bearer sk-global-fallback"

    @pytest.mark.asyncio
    async def test_request_connectivity_uses_selected_header(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = _build_settings(admin_key="sk-admin-fallback")
        client = BackendAnalyticsClient(settings)
        captured: dict = {}

        class _FakeAsyncClient:
            def __init__(self, timeout: float) -> None:
                captured["timeout"] = timeout

            async def __aenter__(self) -> _FakeAsyncClient:
                return self

            async def __aexit__(self, exc_type, exc, tb) -> bool:
                return False

            async def get(self, url: str, params: dict, headers: dict) -> _FakeResponse:
                captured["url"] = url
                captured["params"] = params
                captured["headers"] = headers
                return _FakeResponse()

        monkeypatch.setattr(
            "app.clients.backend_client.get_http_request",
            lambda: SimpleNamespace(
                headers={
                    "BACKEND_ADMIN_API_KEY": "sk-admin-from-header",
                }
            ),
        )
        monkeypatch.setattr("app.clients.backend_client.httpx.AsyncClient", _FakeAsyncClient)

        payload = await client.get_daily_overview(
            day=date(2026, 3, 12),
            timezone_name="Asia/Shanghai",
            top_limit=5,
        )

        assert payload == {"ok": True}
        assert captured["url"] == "http://127.0.0.1:8000/api/v1/admin/analytics/daily-overview"
        assert captured["params"]["day"] == "2026-03-12"
        assert captured["headers"]["Authorization"] == "Bearer sk-admin-from-header"

    @pytest.mark.asyncio
    async def test_request_fails_without_any_credential(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = _build_settings(admin_key="", global_key="")
        client = BackendAnalyticsClient(settings)

        def _raise_runtime_error() -> None:
            raise RuntimeError("No active HTTP request found.")

        monkeypatch.setattr("app.clients.backend_client.get_http_request", _raise_runtime_error)

        with pytest.raises(RuntimeError, match="Missing admin API key"):
            await client.get_daily_overview(
                day=date(2026, 3, 12),
                timezone_name="Asia/Shanghai",
                top_limit=5,
            )

    @pytest.mark.asyncio
    async def test_request_taxonomy_and_report_dataset_paths(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        settings = _build_settings(admin_key="sk-admin-fallback")
        client = BackendAnalyticsClient(settings)
        captured_urls: list[str] = []

        class _FakeAsyncClient:
            def __init__(self, timeout: float) -> None:
                self.timeout = timeout

            async def __aenter__(self) -> _FakeAsyncClient:
                return self

            async def __aexit__(self, exc_type, exc, tb) -> bool:
                return False

            async def get(self, url: str, params: dict, headers: dict) -> _FakeResponse:
                captured_urls.append(url)
                assert headers["Authorization"] == "Bearer sk-admin-from-header"
                assert "day" in params
                return _FakeResponse()

        monkeypatch.setattr(
            "app.clients.backend_client.get_http_request",
            lambda: SimpleNamespace(
                headers={
                    "BACKEND_ADMIN_API_KEY": "sk-admin-from-header",
                }
            ),
        )
        monkeypatch.setattr("app.clients.backend_client.httpx.AsyncClient", _FakeAsyncClient)

        await client.get_daily_content_taxonomy(
            day=date(2026, 3, 12),
            timezone_name="Asia/Shanghai",
            top_limit=10,
            user_id=None,
        )
        await client.get_daily_report_dataset(
            day=date(2026, 3, 12),
            timezone_name="Asia/Shanghai",
            top_limit=10,
            user_limit=100,
            user_offset=0,
        )

        assert captured_urls == [
            "http://127.0.0.1:8000/api/v1/admin/analytics/daily-content-taxonomy",
            "http://127.0.0.1:8000/api/v1/admin/analytics/daily-report-dataset",
        ]
