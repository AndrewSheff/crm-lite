import { Link } from "react-router"
import { List, Plus } from "lucide-react"
import { useKanban } from "@/hooks/useDeals"
import KanbanBoard from "@/components/kanban/KanbanBoard"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function DealsPage() {
  const { data, isLoading } = useKanban()

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b">
        <h1 className="text-2xl font-bold">Канбан</h1>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/deals/list">
              <List className="mr-2 h-4 w-4" />
              Таблица
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
      <div className="flex-1 overflow-auto p-6">
        {isLoading ? (
          <div className="flex gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-96 w-72 flex-shrink-0" />
            ))}
          </div>
        ) : data?.stages ? (
          <KanbanBoard columns={data.stages} />
        ) : (
          <div className="text-muted-foreground text-center py-16">
            Нет данных для отображения
          </div>
        )}
      </div>
    </div>
  )
}
