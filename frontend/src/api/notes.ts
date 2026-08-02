import apiClient from "./client"
import type { Note, PaginatedResponse } from "./types"

export interface NoteFilters {
  client_id?: string
  deal_id?: string
  page?: number
  per_page?: number
}

export interface NoteCreateData {
  content: string
  client_id?: string
  deal_id?: string
  is_pinned?: boolean
}

export async function getNotes(filters: NoteFilters = {}): Promise<PaginatedResponse<Note>> {
  const res = await apiClient.get<PaginatedResponse<Note>>("/notes", { params: filters })
  return res.data
}

export async function createNote(data: NoteCreateData): Promise<Note> {
  const res = await apiClient.post<Note>("/notes", data)
  return res.data
}

export async function updateNote(id: string, data: Partial<NoteCreateData>): Promise<Note> {
  const res = await apiClient.put<Note>(`/notes/${id}`, data)
  return res.data
}

export async function deleteNote(id: string): Promise<void> {
  await apiClient.delete(`/notes/${id}`)
}
