import apiClient from "./client"
import type { Activity, PaginatedResponse } from "./types"

export interface ActivityFilters {
  client_id?: string
  deal_id?: string
  page?: number
  per_page?: number
}

export interface ActivityCreateData {
  type: "call" | "meeting" | "email" | "task"
  title: string
  description?: string
  client_id?: string
  deal_id?: string
  scheduled_at?: string
}

export async function getActivities(filters: ActivityFilters = {}): Promise<PaginatedResponse<Activity>> {
  const res = await apiClient.get<PaginatedResponse<Activity>>("/activities", { params: filters })
  return res.data
}

export async function createActivity(data: ActivityCreateData): Promise<Activity> {
  const res = await apiClient.post<Activity>("/activities", data)
  return res.data
}

export async function completeActivity(id: string): Promise<Activity> {
  const res = await apiClient.patch<Activity>(`/activities/${id}/complete`)
  return res.data
}

export async function deleteActivity(id: string): Promise<void> {
  await apiClient.delete(`/activities/${id}`)
}
