import apiClient from "./client"
import type { Stage } from "./types"

export async function getStages(): Promise<Stage[]> {
  const res = await apiClient.get<Stage[]>("/stages")
  return res.data
}

export async function createStage(data: {
  name: string
  color?: string
  is_won?: boolean
  is_lost?: boolean
}): Promise<Stage> {
  const res = await apiClient.post<Stage>("/stages", data)
  return res.data
}

export async function updateStage(
  id: string,
  data: Partial<{ name: string; color: string; is_won: boolean; is_lost: boolean }>,
): Promise<Stage> {
  const res = await apiClient.put<Stage>(`/stages/${id}`, data)
  return res.data
}

export async function deleteStage(id: string): Promise<void> {
  await apiClient.delete(`/stages/${id}`)
}

export async function reorderStages(ids: string[]): Promise<void> {
  await apiClient.post("/stages/reorder", { ids })
}
