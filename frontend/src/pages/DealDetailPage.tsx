import { useState } from "react"
import { useNavigate, useParams } from "react-router"
import { format } from "date-fns"
import {
  CheckCircle,
  Edit,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react"
import { useAiSummary, useDeal } from "@/hooks/useDeals"
import { useNotes, useCreateNote, useDeleteNote } from "@/hooks/useNotes"
import { useActivities, useCreateActivity, useCompleteActivity, useDeleteActivity } from "@/hooks/useActivities"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"

import { actTypeLabels, priorityLabels } from "@/lib/constants"

export default function DealDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: deal, isLoading } = useDeal(id!)
  const aiSummary = useAiSummary()

  const { data: notesData } = useNotes({ deal_id: id })
  const { data: activitiesData } = useActivities({ deal_id: id })
  const createNote = useCreateNote()
  const deleteNote = useDeleteNote()
  const createActivity = useCreateActivity()
  const completeAct = useCompleteActivity()
  const deleteActivity = useDeleteActivity()

  const [noteText, setNoteText] = useState("")
  const [actTitle, setActTitle] = useState("")
  const [actType, setActType] = useState("call")
  const [summary, setSummary] = useState("")

  const handleAddNote = async () => {
    if (!noteText.trim()) return
    await createNote.mutateAsync({ content: noteText, deal_id: id })
    setNoteText("")
  }

  const handleAddActivity = async () => {
    if (!actTitle.trim()) return
    await createActivity.mutateAsync({
      type: actType as "call" | "meeting" | "email" | "task",
      title: actTitle,
      deal_id: id,
    })
    setActTitle("")
  }

  const handleAiSummary = async () => {
    const result = await aiSummary.mutateAsync(id!)
    setSummary(result.summary)
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!deal) {
    return <div className="p-6 text-muted-foreground">Сделка не найдена</div>
  }

  return (
    <div className="space-y-6 p-6">
      {/* шапка */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{deal.title}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
            <span>{deal.client.name}</span>
            <div className="flex items-center gap-1">
              <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: deal.stage.color }} />
              {deal.stage.name}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleAiSummary} disabled={aiSummary.isPending}>
            <Sparkles className="mr-2 h-4 w-4" />
            {aiSummary.isPending ? "Генерация..." : "AI-резюме"}
          </Button>
          <Button variant="outline" onClick={() => navigate(`/deals/${id}/edit`)}>
            <Edit className="mr-2 h-4 w-4" />
            Редактировать
          </Button>
        </div>
      </div>

      {/* AI-резюме */}
      {summary && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              AI-резюме
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{summary}</p>
          </CardContent>
        </Card>
      )}

      {/* инфо */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-4 space-y-2 text-sm">
            <div>
              Сумма:{" "}
              <strong>
                {deal.amount
                  ? new Intl.NumberFormat("ru-RU", { style: "currency", currency: deal.currency, maximumFractionDigits: 0 }).format(deal.amount)
                  : "—"}
              </strong>
            </div>
            <div>Вероятность: <strong>{deal.probability}%</strong></div>
            <div>Приоритет: <Badge variant="outline">{priorityLabels[deal.priority]}</Badge></div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 space-y-2 text-sm">
            <div>Менеджер: {deal.owner.name}</div>
            {deal.expected_close_date && (
              <div>Закрытие: {format(new Date(deal.expected_close_date), "dd.MM.yyyy")}</div>
            )}
            {deal.closed_at && (
              <div>Закрыта: {format(new Date(deal.closed_at), "dd.MM.yyyy")}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 space-y-2 text-sm">
            <div>Создана: {format(new Date(deal.created_at), "dd.MM.yyyy")}</div>
            <div className="flex flex-wrap gap-1">
              {deal.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary" style={{ borderColor: tag.color }}>
                  {tag.name}
                </Badge>
              ))}
            </div>
            {deal.description && <p className="text-muted-foreground">{deal.description}</p>}
          </CardContent>
        </Card>
      </div>

      {/* табы */}
      <Tabs defaultValue="notes">
        <TabsList>
          <TabsTrigger value="notes">Заметки ({notesData?.total || 0})</TabsTrigger>
          <TabsTrigger value="activities">Активности ({activitiesData?.total || 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="notes" className="space-y-3">
          <div className="flex gap-2">
            <Textarea
              placeholder="Добавить заметку..."
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              rows={2}
              className="flex-1"
            />
            <Button onClick={handleAddNote} disabled={createNote.isPending}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          {notesData?.items.map((note) => (
            <Card key={note.id}>
              <CardContent className="pt-4">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>{note.author.name}</span>
                  <span>{format(new Date(note.created_at), "dd.MM.yyyy HH:mm")}</span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{note.content}</p>
                <div className="mt-2 flex justify-end">
                  <Button variant="ghost" size="sm" onClick={() => deleteNote.mutate(note.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="activities" className="space-y-3">
          <div className="flex gap-2">
            <Select value={actType} onValueChange={setActType}>
              <SelectTrigger className="w-[130px]"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="call">Звонок</SelectItem>
                <SelectItem value="meeting">Встреча</SelectItem>
                <SelectItem value="email">Письмо</SelectItem>
                <SelectItem value="task">Задача</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder="Название..."
              value={actTitle}
              onChange={(e) => setActTitle(e.target.value)}
              className="flex-1"
            />
            <Button onClick={handleAddActivity} disabled={createActivity.isPending}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          {activitiesData?.items.map((act) => (
            <Card key={act.id}>
              <CardContent className="pt-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{actTypeLabels[act.type] || act.type}</Badge>
                    <span className={`text-sm font-medium ${act.is_completed ? "line-through text-muted-foreground" : ""}`}>
                      {act.title}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {act.author.name} — {format(new Date(act.created_at), "dd.MM.yyyy")}
                  </div>
                </div>
                <div className="flex gap-1">
                  {!act.is_completed && (
                    <Button variant="ghost" size="sm" onClick={() => completeAct.mutate(act.id)}>
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => deleteActivity.mutate(act.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
