import apiClient from "./client"
import type { Client, PaginatedResponse } from "./types"

export interface ClientFilters {
  page?: number
  per_page?: number
  search?: string
  status?: string
  owner_id?: string
  tag_id?: string
  sort_by?: string
  sort_order?: string
}

export interface ClientCreateData {
  name: string
  email?: string
  phone?: string
  company?: string
  industry?: string
  website?: string
  address?: string
  status?: string
  source?: string
  tag_ids?: string[]
}

export type ClientUpdateData = Partial<ClientCreateData>

export async function getClients(filters: ClientFilters = {}): Promise<PaginatedResponse<Client>> {
  const res = await apiClient.get<PaginatedResponse<Client>>("/clients", { params: filters })
  return res.data
}

export async function getClient(id: string): Promise<Client> {
  const res = await apiClient.get<Client>(`/clients/${id}`)
  return res.data
}

export async function createClient(data: ClientCreateData): Promise<Client> {
  const res = await apiClient.post<Client>("/clients", data)
  return res.data
}

export async function updateClient(id: string, data: ClientUpdateData): Promise<Client> {
  const res = await apiClient.put<Client>(`/clients/${id}`, data)
  return res.data
}

export async function deleteClient(id: string): Promise<void> {
  await apiClient.delete(`/clients/${id}`)
}
