"""Схемы дашборда — статистика, воронка, график выручки, лента активности."""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_clients: int = 0
    new_clients: int = 0
    active_deals: int = 0
    won_deals: int = 0
    lost_deals: int = 0
    total_revenue: float = 0.0
    avg_deal_size: float = 0.0
    conversion_rate: float = 0.0
    avg_deal_cycle_days: int = 0


class PipelineStage(BaseModel):
    name: str
    count: int
    amount: float
    color: str


class PipelineResponse(BaseModel):
    stages: list[PipelineStage]


class RevenueChartPoint(BaseModel):
    date: str
    revenue: float
    deals_count: int


class RevenueChartResponse(BaseModel):
    data: list[RevenueChartPoint]


class ActivityFeedItem(BaseModel):
    id: str
    type: str
    title: str
    author_name: str
    created_at: str


class ActivityFeedResponse(BaseModel):
    items: list[ActivityFeedItem]
