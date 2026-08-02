import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { getErrorMessage } from "@/lib/api-error"
import { blockUser, createUser, getUsers } from "@/api/users"
import type { UserCreateData } from "@/api/users"

export function useUsers(params?: { page?: number; per_page?: number }) {
  return useQuery({
    queryKey: ["users", params],
    queryFn: () => getUsers(params),
  })
}

export function useCreateUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: UserCreateData) => createUser(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] })
      toast.success("Пользователь создан")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка создания пользователя")),
  })
}

export function useBlockUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => blockUser(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] })
      toast.success("Статус пользователя изменен")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка блокировки пользователя")),
  })
}
