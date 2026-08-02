import apiClient from "./client"

export async function exportClients(): Promise<Blob> {
  const res = await apiClient.get("/export/clients", { responseType: "blob" })
  return res.data as Blob
}

export async function exportDeals(): Promise<Blob> {
  const res = await apiClient.get("/export/deals", { responseType: "blob" })
  return res.data as Blob
}

export async function importClients(file: File): Promise<{ created: number; skipped: number; errors: string[] }> {
  const formData = new FormData()
  formData.append("file", file)
  const res = await apiClient.post("/export/clients/import", formData)
  return res.data
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  // гарантируем очистку даже если скачивание не сработало
  setTimeout(() => URL.revokeObjectURL(url), 500)
}
