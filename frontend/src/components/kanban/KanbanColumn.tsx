import { useDroppable } from "@dnd-kit/core"
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable"
import type { KanbanColumn as KanbanColumnType } from "@/api/types"
import KanbanCard from "./KanbanCard"

interface Props {
  column: KanbanColumnType
}

export default function KanbanColumn({ column }: Props) {
  const { setNodeRef } = useDroppable({ id: column.id })

  const totalFormatted = column.total_amount
    ? new Intl.NumberFormat("ru-RU", {
        style: "currency",
        currency: "RUB",
        maximumFractionDigits: 0,
      }).format(column.total_amount)
    : "0"

  return (
    <div className="flex w-72 flex-shrink-0 flex-col rounded-lg bg-muted/50">
      {/* заголовок колонки */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b">
        <div
          className="h-3 w-3 rounded-full"
          style={{ backgroundColor: column.color }}
        />
        <span className="text-sm font-semibold flex-1">{column.name}</span>
        <span className="text-xs text-muted-foreground">
          {column.deals_count}
        </span>
      </div>
      <div className="px-2 py-1 text-xs text-muted-foreground border-b">
        {totalFormatted}
      </div>

      {/* карточки */}
      <div ref={setNodeRef} className="flex-1 space-y-2 p-2 min-h-[100px]">
        <SortableContext
          items={column.deals.map((d) => d.id)}
          strategy={verticalListSortingStrategy}
        >
          {column.deals.map((deal) => (
            <KanbanCard key={deal.id} card={deal} />
          ))}
        </SortableContext>
      </div>
    </div>
  )
}
