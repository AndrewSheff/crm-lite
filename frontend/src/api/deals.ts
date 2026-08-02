import apiClient from "./client"
import type { Deal, KanbanResponse, PaginatedResponse } from "./types"

export interface DealFilters {
  page?: number
  per_page?: number
  client_id?: string
  stage_id?: string
  owner_id?: string
  priority?: string
  sort_by?: string
  sort_order?: string
}

export interface DealCreateData {
  title: string
  client_id: string
  stage_id: string
  amount?: number
  probability?: number
  expected_close_date?: string
  priority?: string
  description?: string
  tag_ids?: string[]
}

export type DealUpdateData = Partial<DealCreateData>

export async function getDeals(filters: DealFilters = {}): Promise<PaginatedResponse<Deal>> {
  const res = await apiClient.get<PaginatedResponse<Deal>>("/deals", { params: filters })
  return res.data
}

export async function getDeal(id: string): Promise<Deal> {
  const res = await apiClient.get<Deal>(`/deals/${id}`)
  return res.data
}

export async function getKanban(params?: {
  owner_id?: string
  client_id?: string
  priority?: string
}): Promise<KanbanResponse> {
  const res = await apiClient.get<KanbanResponse>("/deals/kanban", { params })
  return res.data
}

export async function createDeal(data: DealCreateData): Promise<Deal> {
  const res = await apiClient.post<Deal>("/deals", data)
  return res.data
}

export async function updateDeal(id: string, data: DealUpdateData): Promise<Deal> {
  const res = await apiClient.put<Deal>(`/deals/${id}`, data)
  return res.data
}

export async function deleteDeal(id: string): Promise<void> {
  await apiClient.delete(`/deals/${id}`)
}

export async function moveStage(
  id: string,
  stage_id: string,
  position: number,
): Promise<Deal> {
  const res = await apiClient.patch<Deal>(`/deals/${id}/stage`, { stage_id, position })
  return res.data
}

export async function getAiSummary(id: string): Promise<{ summary: string }> {
  const res = await apiClient.post<{ summary: string }>(`/deals/${id}/ai-summary`)
  return res.data
}
