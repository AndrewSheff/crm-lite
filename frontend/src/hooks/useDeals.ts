import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { getErrorMessage } from "@/lib/api-error"
import {
  createDeal,
  deleteDeal,
  getAiSummary,
  getDeal,
  getDeals,
  getKanban,
  moveStage,
  updateDeal,
} from "@/api/deals"
import type { DealCreateData, DealFilters, DealUpdateData } from "@/api/deals"

export function useDeals(filters: DealFilters = {}) {
  return useQuery({
    queryKey: ["deals", filters],
    queryFn: () => getDeals(filters),
  })
}

export function useDeal(id: string) {
  return useQuery({
    queryKey: ["deals", id],
    queryFn: () => getDeal(id),
    enabled: !!id,
  })
}

export function useKanban(params?: { owner_id?: string; client_id?: string; priority?: string }) {
  return useQuery({
    queryKey: ["kanban", params],
    queryFn: () => getKanban(params),
  })
}

export function useCreateDeal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: DealCreateData) => createDeal(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deals"] })
      qc.invalidateQueries({ queryKey: ["kanban"] })
      toast.success("Сделка создана")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка создания сделки")),
  })
}

export function useUpdateDeal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DealUpdateData }) => updateDeal(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deals"] })
      qc.invalidateQueries({ queryKey: ["kanban"] })
      toast.success("Сделка обновлена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка обновления сделки")),
  })
}

export function useDeleteDeal() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteDeal(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deals"] })
      qc.invalidateQueries({ queryKey: ["kanban"] })
      toast.success("Сделка удалена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка удаления сделки")),
  })
}

export function useMoveStage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, stage_id, position }: { id: string; stage_id: string; position: number }) =>
      moveStage(id, stage_id, position),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["kanban"] })
      qc.invalidateQueries({ queryKey: ["deals"] })
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка перемещения сделки")),
  })
}

export function useAiSummary() {
  return useMutation({
    mutationFn: (id: string) => getAiSummary(id),
    onError: (e) => toast.error(getErrorMessage(e, "Не удалось сгенерировать AI-резюме")),
  })
}
