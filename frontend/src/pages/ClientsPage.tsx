import { useState } from "react"
import { Link, useNavigate } from "react-router"
import { format } from "date-fns"
import { Download, Plus, Search, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { exportClients, downloadBlob } from "@/api/export"
import { useClients, useDeleteClient } from "@/hooks/useClients"
import { useTags } from "@/hooks/useTags"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import { statusLabels } from "@/lib/constants"

const statusColors: Record<string, string> = {
  lead: "bg-blue-100 text-blue-800",
  active: "bg-green-100 text-green-800",
  churned: "bg-red-100 text-red-800",
  inactive: "bg-gray-100 text-gray-800",
}

export default function ClientsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState<string>("all")
  const [tagId, setTagId] = useState<string>("all")

  const { data, isLoading } = useClients({
    page,
    per_page: 20,
    search: search || undefined,
    status: status === "all" ? undefined : status,
    tag_id: tagId === "all" ? undefined : tagId,
  })
  const { data: tags } = useTags()
  const deleteMutation = useDeleteClient()

  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Клиенты</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={async () => {
              try {
                const blob = await exportClients()
                downloadBlob(blob, "clients.xlsx")
                toast.success("Экспорт завершен")
              } catch {
                toast.error("Ошибка экспорта")
              }
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            Excel
          </Button>
          <Button onClick={() => navigate("/clients/new")}>
            <Plus className="mr-2 h-4 w-4" />
            Новый клиент
          </Button>
        </div>
      </div>

      {/* фильтры */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Поиск по имени, email, телефону..."
            className="pl-9"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          />
        </div>
        <Select value={status} onValueChange={(v) => { setStatus(v); setPage(1) }}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Статус" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все статусы</SelectItem>
            <SelectItem value="lead">Лид</SelectItem>
            <SelectItem value="active">Активный</SelectItem>
            <SelectItem value="churned">Ушел</SelectItem>
            <SelectItem value="inactive">Неактивный</SelectItem>
          </SelectContent>
        </Select>
        <Select value={tagId} onValueChange={(v) => { setTagId(v); setPage(1) }}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Тег" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все теги</SelectItem>
            {tags?.map((tag) => (
              <SelectItem key={tag.id} value={tag.id}>{tag.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* таблица */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Имя</TableHead>
              <TableHead>Компания</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead>Теги</TableHead>
              <TableHead>Сделки</TableHead>
              <TableHead>Выручка</TableHead>
              <TableHead>Дата</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  Загрузка...
                </TableCell>
              </TableRow>
            ) : !data?.items.length ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  Клиенты не найдены
                </TableCell>
              </TableRow>
            ) : (
              data.items.map((client) => (
                <TableRow key={client.id} className="cursor-pointer" onClick={() => navigate(`/clients/${client.id}`)}>
                  <TableCell className="font-medium">
                    <Link to={`/clients/${client.id}`} className="hover:underline" onClick={(e) => e.stopPropagation()}>
                      {client.name}
                    </Link>
                    {client.email && (
                      <div className="text-xs text-muted-foreground">{client.email}</div>
                    )}
                  </TableCell>
                  <TableCell>{client.company || "—"}</TableCell>
                  <TableCell>
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[client.status] || ""}`}>
                      {statusLabels[client.status] || client.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {client.tags.map((tag) => (
                        <Badge key={tag.id} variant="secondary" className="text-xs" style={{ borderColor: tag.color }}>
                          {tag.name}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>{client.deals_count}</TableCell>
                  <TableCell>
                    {client.total_revenue
                      ? new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(client.total_revenue)
                      : "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {format(new Date(client.created_at), "dd.MM.yyyy")}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (confirm("Удалить клиента?")) deleteMutation.mutate(client.id)
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* пагинация */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Назад
          </Button>
          <span className="text-sm text-muted-foreground">
            {page} / {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Далее
          </Button>
        </div>
      )}
    </div>
  )
}
