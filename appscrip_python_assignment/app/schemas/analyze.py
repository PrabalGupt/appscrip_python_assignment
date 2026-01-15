from typing import List, Literal, Optional
from pydantic import BaseModel, HttpUrl, Field


class MarketItem(BaseModel):
    title: str
    url: Optional[HttpUrl] = None
    snippet: str = ""


class CollectedData(BaseModel):
    sector: str
    country: str = "India"
    source: Literal["duckduckgo", "fallback"] = "duckduckgo"
    items: List[MarketItem] = Field(default_factory=list)


class AIAnalysis(BaseModel):
    summary: str
    opportunities: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    time_horizon: Optional[str] = None  # e.g., "short-term 3-6 months"
    evidence_points: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    sector: str
    markdown_report: str
    generated_by: str = "Trade Opportunities API"
