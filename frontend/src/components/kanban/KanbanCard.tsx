import { useSortable } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { useNavigate } from "react-router"
import type { KanbanCard as KanbanCardType } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

const priorityColors: Record<string, string> = {
  urgent: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-green-100 text-green-800",
}

const priorityLabels: Record<string, string> = {
  urgent: "Срочный",
  high: "Высокий",
  medium: "Средний",
  low: "Низкий",
}

interface Props {
  card: KanbanCardType
}

export default function KanbanCard({ card }: Props) {
  const navigate = useNavigate()
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: card.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Card
        className="cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow"
        onClick={() => navigate(`/deals/${card.id}`)}
      >
        <CardContent className="p-3 space-y-2">
          <div className="font-medium text-sm leading-tight">{card.title}</div>
          <div className="text-xs text-muted-foreground">{card.client.name}</div>
          <div className="flex items-center justify-between">
            {card.amount ? (
              <span className="text-sm font-semibold">
                {new Intl.NumberFormat("ru-RU", {
                  style: "currency",
                  currency: card.currency,
                  maximumFractionDigits: 0,
                }).format(card.amount)}
              </span>
            ) : (
              <span className="text-xs text-muted-foreground">—</span>
            )}
            <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ${priorityColors[card.priority] || ""}`}>
              {priorityLabels[card.priority] || card.priority}
            </span>
          </div>
          {card.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {card.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary" className="text-[10px] px-1 py-0">
                  {tag.name}
                </Badge>
              ))}
            </div>
          )}
          <div className="text-[11px] text-muted-foreground">{card.owner.name}</div>
        </CardContent>
      </Card>
    </div>
  )
}
