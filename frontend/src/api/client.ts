import axios from "axios"
import type { AxiosRequestConfig } from "axios"

// базовый HTTP-клиент — перехватчик для JWT и рефреша
const apiClient = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
})

// подставляем токен к каждому запросу
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// очередь запросов, ждущих рефреша токена
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((p) => {
    if (token) {
      p.resolve(token)
    } else {
      p.reject(error)
    }
  })
  failedQueue = []
}

// при 401 пытаемся обновить токен, иначе — на логин
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        // уже обновляем — ставим запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              original.headers = { ...original.headers, Authorization: `Bearer ${token}` }
              resolve(apiClient(original))
            },
            reject,
          })
        })
      }

      original._retry = true
      isRefreshing = true
      const refreshToken = localStorage.getItem("refresh_token")

      if (refreshToken) {
        try {
          const { data } = await axios.post("/api/v1/auth/refresh", {
            refresh_token: refreshToken,
          })
          localStorage.setItem("access_token", data.access_token)
          localStorage.setItem("refresh_token", data.refresh_token)
          processQueue(null, data.access_token)
          original.headers = { ...original.headers, Authorization: `Bearer ${data.access_token}` }
          return apiClient(original)
        } catch (refreshError) {
          processQueue(refreshError, null)
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
          window.location.href = "/login"
        } finally {
          isRefreshing = false
        }
      } else {
        isRefreshing = false
        window.location.href = "/login"
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
