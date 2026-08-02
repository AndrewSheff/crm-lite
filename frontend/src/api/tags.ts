import apiClient from "./client"
import type { Tag } from "./types"

export async function getTags(): Promise<Tag[]> {
  const res = await apiClient.get<Tag[]>("/tags")
  return res.data
}

export async function createTag(data: { name: string; color?: string }): Promise<Tag> {
  const res = await apiClient.post<Tag>("/tags", data)
  return res.data
}

export async function deleteTag(id: string): Promise<void> {
  await apiClient.delete(`/tags/${id}`)
}
