import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { createTag, deleteTag, getTags } from "@/api/tags"

export function useTags() {
  return useQuery({
    queryKey: ["tags"],
    queryFn: getTags,
  })
}

export function useCreateTag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; color?: string }) => createTag(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tags"] })
      toast.success("Тег создан")
    },
    onError: () => toast.error("Ошибка создания тега"),
  })
}

export function useDeleteTag() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteTag(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tags"] })
      toast.success("Тег удален")
    },
    onError: () => toast.error("Ошибка удаления тега"),
  })
}
