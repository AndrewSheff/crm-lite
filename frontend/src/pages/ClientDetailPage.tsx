import { useState } from "react"
import { Link, useNavigate, useParams } from "react-router"
import { format } from "date-fns"
import {
  CheckCircle,
  Edit,
  Mail,
  Phone,
  Plus,
  Trash2,
} from "lucide-react"
import { useClient } from "@/hooks/useClients"
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

import { actTypeLabels, statusLabels } from "@/lib/constants"

export default function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: client, isLoading } = useClient(id!)
  const { data: notesData } = useNotes({ client_id: id })
  const { data: activitiesData } = useActivities({ client_id: id })

  const createNote = useCreateNote()
  const deleteNote = useDeleteNote()
  const createActivity = useCreateActivity()
  const completeAct = useCompleteActivity()
  const deleteActivity = useDeleteActivity()

  const [noteText, setNoteText] = useState("")
  const [actTitle, setActTitle] = useState("")
  const [actType, setActType] = useState<string>("call")

  const handleAddNote = async () => {
    if (!noteText.trim()) return
    await createNote.mutateAsync({ content: noteText, client_id: id })
    setNoteText("")
  }

  const handleAddActivity = async () => {
    if (!actTitle.trim()) return
    await createActivity.mutateAsync({
      type: actType as "call" | "meeting" | "email" | "task",
      title: actTitle,
      client_id: id,
    })
    setActTitle("")
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!client) {
    return <div className="p-6 text-muted-foreground">Клиент не найден</div>
  }

  return (
    <div className="space-y-6 p-6">
      {/* шапка */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{client.name}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
            {client.company && <span>{client.company}</span>}
            <span className="inline-block rounded-full bg-secondary px-2 py-0.5 text-xs">
              {statusLabels[client.status] || client.status}
            </span>
          </div>
        </div>
        <Button variant="outline" onClick={() => navigate(`/clients/${id}/edit`)}>
          <Edit className="mr-2 h-4 w-4" />
          Редактировать
        </Button>
      </div>

      {/* инфо-карточка */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-4 space-y-2 text-sm">
            {client.email && (
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                {client.email}
              </div>
            )}
            {client.phone && (
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                {client.phone}
              </div>
            )}
            {client.industry && <div>Отрасль: {client.industry}</div>}
            {client.source && <div>Источник: {client.source}</div>}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 space-y-1 text-sm">
            <div>Сделок: <strong>{client.deals_count}</strong></div>
            <div>
              Выручка:{" "}
              <strong>
                {client.total_revenue
                  ? new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(client.total_revenue)
                  : "0"}
              </strong>
            </div>
            <div>Менеджер: {client.owner.name}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 space-y-2 text-sm">
            <div>Создан: {format(new Date(client.created_at), "dd.MM.yyyy")}</div>
            <div className="flex flex-wrap gap-1">
              {client.tags.map((tag) => (
                <Badge key={tag.id} variant="secondary" style={{ borderColor: tag.color }}>
                  {tag.name}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* табы */}
      <Tabs defaultValue="notes">
        <TabsList>
          <TabsTrigger value="notes">Заметки ({notesData?.total || 0})</TabsTrigger>
          <TabsTrigger value="activities">Активности ({activitiesData?.total || 0})</TabsTrigger>
          <TabsTrigger value="deals">Сделки ({client.deals_count})</TabsTrigger>
        </TabsList>

        {/* заметки */}
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

        {/* активности */}
        <TabsContent value="activities" className="space-y-3">
          <div className="flex gap-2">
            <Select value={actType} onValueChange={setActType}>
              <SelectTrigger className="w-[130px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="call">Звонок</SelectItem>
                <SelectItem value="meeting">Встреча</SelectItem>
                <SelectItem value="email">Письмо</SelectItem>
                <SelectItem value="task">Задача</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder="Название активности..."
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

        {/* сделки */}
        <TabsContent value="deals">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Сделки клиента</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Перейдите в{" "}
                <Link to="/deals" className="text-primary hover:underline">
                  раздел сделок
                </Link>{" "}
                для просмотра и управления.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
