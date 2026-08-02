import apiClient from "./client"
import type {
  ActivityFeedItem,
  DashboardStats,
  PipelineStage,
  RevenueChartPoint,
} from "./types"

export async function getStats(period_days = 30): Promise<DashboardStats> {
  const res = await apiClient.get<DashboardStats>("/dashboard/stats", {
    params: { period_days },
  })
  return res.data
}

export async function getPipeline(): Promise<{ stages: PipelineStage[] }> {
  const res = await apiClient.get<{ stages: PipelineStage[] }>("/dashboard/pipeline")
  return res.data
}

export async function getRevenueChart(
  period_days = 90,
): Promise<{ data: RevenueChartPoint[] }> {
  const res = await apiClient.get<{ data: RevenueChartPoint[] }>("/dashboard/revenue-chart", {
    params: { period_days },
  })
  return res.data
}

export async function getActivityFeed(
  limit = 10,
): Promise<{ items: ActivityFeedItem[] }> {
  const res = await apiClient.get<{ items: ActivityFeedItem[] }>("/dashboard/activity-feed", {
    params: { limit },
  })
  return res.data
}
