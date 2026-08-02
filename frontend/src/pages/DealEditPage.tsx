import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router"
import { useClients } from "@/hooks/useClients"
import { useDeal, useUpdateDeal } from "@/hooks/useDeals"
import { useStages } from "@/hooks/useStages"
import { useTags } from "@/hooks/useTags"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"

export default function DealEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: deal, isLoading } = useDeal(id!)
  const updateMutation = useUpdateDeal()
  const { data: clientsData } = useClients({ per_page: 100 })
  const { data: stages } = useStages()
  const { data: tags } = useTags()

  const [title, setTitle] = useState("")
  const [clientId, setClientId] = useState("")
  const [stageId, setStageId] = useState("")
  const [amount, setAmount] = useState("")
  const [probability, setProbability] = useState("50")
  const [priority, setPriority] = useState("medium")
  const [expectedClose, setExpectedClose] = useState("")
  const [description, setDescription] = useState("")
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  useEffect(() => {
    if (deal) {
      setTitle(deal.title)
      setClientId(deal.client.id)
      setStageId(deal.stage.id)
      setAmount(deal.amount?.toString() || "")
      setProbability(deal.probability.toString())
      setPriority(deal.priority)
      setExpectedClose(deal.expected_close_date || "")
      setDescription(deal.description || "")
      setSelectedTags(deal.tags.map((t) => t.id))
    }
  }, [deal])

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((t) => t !== tagId) : [...prev, tagId],
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await updateMutation.mutateAsync({
        id: id!,
        data: {
          title,
          client_id: clientId,
          stage_id: stageId,
          amount: amount ? parseFloat(amount) : undefined,
          probability: parseInt(probability, 10) || 50,
          priority,
          expected_close_date: expectedClose || undefined,
          description: description || undefined,
          tag_ids: selectedTags,
        },
      })
      navigate(`/deals/${id}`)
    } catch {
      // ошибка обрабатывается в onError хука
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl p-6 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      <Card>
        <CardHeader>
          <CardTitle>Редактирование сделки</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Название *</Label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Клиент</Label>
                <Select value={clientId} onValueChange={setClientId}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {clientsData?.items.map((c) => (
                      <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Стадия</Label>
                <Select value={stageId} onValueChange={setStageId}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {stages?.map((s) => (
                      <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label>Сумма</Label>
                <Input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Вероятность, %</Label>
                <Input type="number" min={0} max={100} value={probability} onChange={(e) => setProbability(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Приоритет</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Низкий</SelectItem>
                    <SelectItem value="medium">Средний</SelectItem>
                    <SelectItem value="high">Высокий</SelectItem>
                    <SelectItem value="urgent">Срочный</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Ожидаемое закрытие</Label>
              <Input type="date" value={expectedClose} onChange={(e) => setExpectedClose(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Описание</Label>
              <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
            </div>
            <div className="space-y-2">
              <Label>Теги</Label>
              <div className="flex flex-wrap gap-2">
                {tags?.map((tag) => (
                  <Badge
                    key={tag.id}
                    variant={selectedTags.includes(tag.id) ? "default" : "outline"}
                    className="cursor-pointer"
                    style={selectedTags.includes(tag.id) ? { backgroundColor: tag.color } : {}}
                    onClick={() => toggleTag(tag.id)}
                  >
                    {tag.name}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="flex gap-3 justify-end pt-2">
              <Button type="button" variant="outline" onClick={() => navigate(`/deals/${id}`)}>
                Отмена
              </Button>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Сохранение..." : "Сохранить"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
