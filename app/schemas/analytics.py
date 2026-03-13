from __future__ import annotations

from pydantic import BaseModel


class DailyBriefResponse(BaseModel):
    day: str
    timezone: str
    summary: dict
    scenarios: list[dict]
    key_findings: list[str]
    recommendations: list[str]
