import { useState } from "react"
import { Link } from "react-router"
import { toast } from "sonner"
import { updateProfile } from "@/api/auth"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import { roleLabels } from "@/lib/constants"

export default function SettingsPage() {
  const { user, reloadUser } = useAuth()
  const [name, setName] = useState(user?.name || "")
  const [loading, setLoading] = useState(false)

  const handleSave = async () => {
    setLoading(true)
    try {
      await updateProfile({ name })
      await reloadUser()
      toast.success("Профиль обновлен")
    } catch {
      toast.error("Ошибка обновления профиля")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-lg p-6 space-y-6">
      <h1 className="text-2xl font-bold">Настройки</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Профиль</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Имя</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={user?.email || ""} disabled />
          </div>
          <div className="space-y-2">
            <Label>Роль</Label>
            <Input value={roleLabels[user?.role || ""] || user?.role || ""} disabled />
          </div>
          <div className="flex items-center justify-between pt-2">
            <Button variant="outline" asChild>
              <Link to="/change-password">Сменить пароль</Link>
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              {loading ? "Сохранение..." : "Сохранить"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
