import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { getErrorMessage } from "@/lib/api-error"
import {
  createClient,
  deleteClient,
  getClient,
  getClients,
  updateClient,
} from "@/api/clients"
import type { ClientCreateData, ClientFilters, ClientUpdateData } from "@/api/clients"

export function useClients(filters: ClientFilters = {}) {
  return useQuery({
    queryKey: ["clients", filters],
    queryFn: () => getClients(filters),
  })
}

export function useClient(id: string) {
  return useQuery({
    queryKey: ["clients", id],
    queryFn: () => getClient(id),
    enabled: !!id,
  })
}

export function useCreateClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ClientCreateData) => createClient(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["clients"] })
      toast.success("Клиент создан")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка создания клиента")),
  })
}

export function useUpdateClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ClientUpdateData }) =>
      updateClient(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["clients"] })
      toast.success("Клиент обновлен")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка обновления клиента")),
  })
}

export function useDeleteClient() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteClient(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["clients"] })
      toast.success("Клиент удален")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка удаления клиента")),
  })
}
