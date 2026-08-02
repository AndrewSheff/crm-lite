import { useQuery } from "@tanstack/react-query"
import {
  getActivityFeed,
  getPipeline,
  getRevenueChart,
  getStats,
} from "@/api/dashboard"

export function useStats(periodDays = 30) {
  return useQuery({
    queryKey: ["dashboard", "stats", periodDays],
    queryFn: () => getStats(periodDays),
  })
}

export function usePipeline() {
  return useQuery({
    queryKey: ["dashboard", "pipeline"],
    queryFn: getPipeline,
  })
}

export function useRevenueChart(periodDays = 90) {
  return useQuery({
    queryKey: ["dashboard", "revenue-chart", periodDays],
    queryFn: () => getRevenueChart(periodDays),
  })
}

export function useActivityFeed(limit = 10) {
  return useQuery({
    queryKey: ["dashboard", "activity-feed", limit],
    queryFn: () => getActivityFeed(limit),
  })
}
