import type { AxiosError } from "axios"

// вытаскиваем человеческое сообщение из ответа сервера
export function getErrorMessage(error: unknown, fallback: string): string {
  const axiosError = error as AxiosError<{ detail?: string }>
  return axiosError?.response?.data?.detail || fallback
}
