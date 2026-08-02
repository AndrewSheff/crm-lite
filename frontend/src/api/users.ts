import apiClient from "./client"
import type { PaginatedResponse, User } from "./types"

export interface UserCreateData {
  email: string
  name: string
  password: string
  role: "admin" | "manager" | "viewer"
}

export async function getUsers(params?: {
  page?: number
  per_page?: number
}): Promise<PaginatedResponse<User>> {
  const res = await apiClient.get<PaginatedResponse<User>>("/users", { params })
  return res.data
}

export async function createUser(data: UserCreateData): Promise<User> {
  const res = await apiClient.post<User>("/users", data)
  return res.data
}

export async function blockUser(id: string): Promise<User> {
  const res = await apiClient.patch<User>(`/users/${id}/block`)
  return res.data
}
