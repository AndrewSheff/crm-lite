import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { getErrorMessage } from "@/lib/api-error"
import { createNote, deleteNote, getNotes, updateNote } from "@/api/notes"
import type { NoteCreateData, NoteFilters } from "@/api/notes"

export function useNotes(filters: NoteFilters = {}) {
  return useQuery({
    queryKey: ["notes", filters],
    queryFn: () => getNotes(filters),
    enabled: !!(filters.client_id || filters.deal_id),
  })
}

export function useCreateNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: NoteCreateData) => createNote(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes"] })
      toast.success("Заметка добавлена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка добавления заметки")),
  })
}

export function useUpdateNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<NoteCreateData> }) =>
      updateNote(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes"] })
      toast.success("Заметка обновлена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка обновления заметки")),
  })
}

export function useDeleteNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteNote(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notes"] })
      toast.success("Заметка удалена")
    },
    onError: (e) => toast.error(getErrorMessage(e, "Ошибка удаления заметки")),
  })
}
