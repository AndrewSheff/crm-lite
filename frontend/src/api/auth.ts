import apiClient from "./client"
import type { TokenResponse, User } from "./types"

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface UpdateProfileRequest {
  name?: string
}

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/login", data)
  return res.data
}

export async function register(data: RegisterRequest): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/register", data)
  return res.data
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>("/auth/refresh", { refresh_token })
  return res.data
}

export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  await apiClient.post("/auth/change-password", data)
}

export async function getMe(): Promise<User> {
  const res = await apiClient.get<User>("/auth/me")
  return res.data
}

export async function updateProfile(data: UpdateProfileRequest): Promise<User> {
  const res = await apiClient.put<User>("/auth/me", data)
  return res.data
}
