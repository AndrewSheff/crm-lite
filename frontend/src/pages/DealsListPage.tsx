import { useState } from "react"
import { Link, useNavigate } from "react-router"
import { format } from "date-fns"
import { Download, Kanban, Plus, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { exportDeals, downloadBlob } from "@/api/export"
import { useDeals, useDeleteDeal } from "@/hooks/useDeals"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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

import { priorityLabels } from "@/lib/constants"

export default function DealsListPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const [priority, setPriority] = useState<string>("all")
  const [sortBy, setSortBy] = useState("created_at")

  const { data, isLoading } = useDeals({
    page,
    per_page: 20,
    priority: priority === "all" ? undefined : priority,
    sort_by: sortBy,
    sort_order: "desc",
  })
  const deleteMutation = useDeleteDeal()

  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Сделки</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={async () => {
              try {
                const blob = await exportDeals()
                downloadBlob(blob, "deals.xlsx")
                toast.success("Экспорт завершен")
              } catch {
                toast.error("Ошибка экспорта")
              }
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            Excel
          </Button>
          <Button variant="outline" asChild>
            <Link to="/deals">
              <Kanban className="mr-2 h-4 w-4" />
              Канбан
            </Link>
          </Button>
          <Button asChild>
            <Link to="/deals/new">
              <Plus className="mr-2 h-4 w-4" />
              Новая сделка
            </Link>
          </Button>
        </div>
      </div>

      <div className="flex gap-3">
        <Select value={priority} onValueChange={(v) => { setPriority(v); setPage(1) }}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Приоритет" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все приоритеты</SelectItem>
            <SelectItem value="urgent">Срочный</SelectItem>
            <SelectItem value="high">Высокий</SelectItem>
            <SelectItem value="medium">Средний</SelectItem>
            <SelectItem value="low">Низкий</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">По дате</SelectItem>
            <SelectItem value="amount">По сумме</SelectItem>
            <SelectItem value="title">По названию</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Сделка</TableHead>
              <TableHead>Клиент</TableHead>
              <TableHead>Стадия</TableHead>
              <TableHead>Сумма</TableHead>
              <TableHead>Приоритет</TableHead>
              <TableHead>Менеджер</TableHead>
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
                  Сделки не найдены
                </TableCell>
              </TableRow>
            ) : (
              data.items.map((deal) => (
                <TableRow key={deal.id} className="cursor-pointer" onClick={() => navigate(`/deals/${deal.id}`)}>
                  <TableCell className="font-medium">{deal.title}</TableCell>
                  <TableCell>{deal.client.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5">
                      <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: deal.stage.color }} />
                      {deal.stage.name}
                    </div>
                  </TableCell>
                  <TableCell>
                    {deal.amount
                      ? new Intl.NumberFormat("ru-RU", { style: "currency", currency: deal.currency, maximumFractionDigits: 0 }).format(deal.amount)
                      : "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{priorityLabels[deal.priority] || deal.priority}</Badge>
                  </TableCell>
                  <TableCell className="text-sm">{deal.owner.name}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {format(new Date(deal.created_at), "dd.MM.yyyy")}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation()
                        if (confirm("Удалить сделку?")) deleteMutation.mutate(deal.id)
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

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Назад
          </Button>
          <span className="text-sm text-muted-foreground">{page} / {totalPages}</span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Далее
          </Button>
        </div>
      )}
    </div>
  )
}
