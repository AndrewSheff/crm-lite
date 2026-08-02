import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { getErrorMessage } from "@/lib/api-error"
import {
  completeActivity,
  createActivity,
  deleteActivity,
  getActivities,
} from "@/api/activities"
import type { ActivityCreateData, ActivityFilters } from "@/api/activities"

export function useActivities(filters: ActivityFilters = {}) {
  return useQuery({
    queryKey: ["activities", filters],
    queryFn: () => getActivities(filters),
    enabled: !!(filters.client_id || filters.deal_id),
  })
}

export function useCreateActivity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ActivityCreateData) => createActivity(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["activities"] })
      toast.success("Активность создана")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка создания активности")),
  })
}

export function useCompleteActivity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => completeActivity(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["activities"] })
      toast.success("Активность завершена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка завершения активности")),
  })
}

export function useDeleteActivity() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["activities"] })
      toast.success("Активность удалена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка удаления активности")),
  })
}
