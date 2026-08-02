import {
  DndContext,
  DragOverlay,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core"
import type { DragEndEvent, DragStartEvent } from "@dnd-kit/core"
import { useState } from "react"
import type { KanbanCard as KanbanCardType, KanbanColumn as KanbanColumnType } from "@/api/types"
import { useMoveStage } from "@/hooks/useDeals"
import KanbanCard from "./KanbanCard"
import KanbanColumn from "./KanbanColumn"

interface Props {
  columns: KanbanColumnType[]
}

export default function KanbanBoard({ columns }: Props) {
  const moveMutation = useMoveStage()
  const [activeCard, setActiveCard] = useState<KanbanCardType | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 5 },
    }),
  )

  const findCard = (id: string): KanbanCardType | undefined => {
    for (const col of columns) {
      const card = col.deals.find((d) => d.id === id)
      if (card) return card
    }
    return undefined
  }

  const findColumnByCard = (cardId: string): KanbanColumnType | undefined => {
    return columns.find((col) => col.deals.some((d) => d.id === cardId))
  }

  const handleDragStart = (event: DragStartEvent) => {
    const card = findCard(event.active.id as string)
    setActiveCard(card || null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveCard(null)
    const { active, over } = event
    if (!over) return

    const activeId = active.id as string
    const overId = over.id as string

    // определяем целевую колонку
    let targetColumn = columns.find((col) => col.id === overId)
    if (!targetColumn) {
      targetColumn = findColumnByCard(overId)
    }
    if (!targetColumn) return

    const sourceColumn = findColumnByCard(activeId)
    if (!sourceColumn) return

    // если перетащили в ту же колонку на то же место — игнорируем
    if (sourceColumn.id === targetColumn.id && activeId === overId) return

    // вычисляем позицию
    const overIndex = targetColumn.deals.findIndex((d) => d.id === overId)
    const position = overIndex >= 0 ? overIndex : targetColumn.deals.length

    moveMutation.mutate({
      id: activeId,
      stage_id: targetColumn.id,
      position,
    })
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <KanbanColumn key={column.id} column={column} />
        ))}
      </div>

      <DragOverlay>
        {activeCard ? (
          <div className="w-72 rotate-3">
            <KanbanCard card={activeCard} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}
