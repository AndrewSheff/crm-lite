import { Link, Outlet, useLocation } from "react-router"
import {
  BarChart3,
  Briefcase,
  LogOut,
  Settings,
  Users,
  UserCircle,
} from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
  adminOnly?: boolean
}

const navItems: NavItem[] = [
  { label: "Дашборд", path: "/dashboard", icon: <BarChart3 className="h-5 w-5" /> },
  { label: "Клиенты", path: "/clients", icon: <UserCircle className="h-5 w-5" /> },
  { label: "Сделки", path: "/deals", icon: <Briefcase className="h-5 w-5" /> },
  { label: "Настройки", path: "/settings", icon: <Settings className="h-5 w-5" /> },
  { label: "Пользователи", path: "/users", icon: <Users className="h-5 w-5" />, adminOnly: true },
]

export default function AppLayout() {
  const { user, logout, isAdmin } = useAuth()
  const location = useLocation()

  const filteredNav = navItems.filter((item) => !item.adminOnly || isAdmin)

  return (
    <div className="flex h-screen">
      {/* сайдбар */}
      <aside className="flex w-60 flex-col border-r bg-sidebar text-sidebar-foreground">
        <div className="flex h-14 items-center px-4">
          <Link to="/dashboard" className="text-lg font-bold tracking-tight">
            CRM Lite
          </Link>
        </div>
        <Separator />
        <nav className="flex-1 space-y-1 p-3">
          {filteredNav.map((item) => {
            const active = location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground",
                )}
              >
                {item.icon}
                {item.label}
              </Link>
            )
          })}
        </nav>
        <Separator />
        <div className="p-3">
          <div className="mb-2 truncate px-3 text-xs text-muted-foreground">
            {user?.name}
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start gap-3 text-muted-foreground"
            onClick={logout}
          >
            <LogOut className="h-4 w-4" />
            Выйти
          </Button>
        </div>
      </aside>

      {/* основное содержимое */}
      <main className="flex-1 overflow-auto bg-background">
        <Outlet />
      </main>
    </div>
  )
}
