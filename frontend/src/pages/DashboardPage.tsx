import { format } from "date-fns"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts"
import {
  Briefcase,
  DollarSign,
  TrendingUp,
  Users,
} from "lucide-react"
import { useStats, usePipeline, useRevenueChart, useActivityFeed } from "@/hooks/useDashboard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

function formatCurrency(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`
  return value.toString()
}

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useStats()
  const { data: pipeline } = usePipeline()
  const { data: revenue } = useRevenueChart()
  const { data: feed } = useActivityFeed()

  const kpiCards = [
    {
      title: "Клиенты",
      value: stats?.total_clients ?? 0,
      sub: `+${stats?.new_clients ?? 0} новых`,
      icon: <Users className="h-5 w-5" />,
    },
    {
      title: "Активные сделки",
      value: stats?.active_deals ?? 0,
      sub: `Выиграно: ${stats?.won_deals ?? 0}`,
      icon: <Briefcase className="h-5 w-5" />,
    },
    {
      title: "Выручка",
      value: stats ? formatCurrency(stats.total_revenue) : "0",
      sub: `Средний чек: ${stats ? formatCurrency(stats.avg_deal_size) : "0"}`,
      icon: <DollarSign className="h-5 w-5" />,
    },
    {
      title: "Конверсия",
      value: `${stats?.conversion_rate?.toFixed(1) ?? 0}%`,
      sub: `Цикл: ${stats?.avg_deal_cycle_days?.toFixed(0) ?? "—"} дн.`,
      icon: <TrendingUp className="h-5 w-5" />,
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Дашборд</h1>

      {/* KPI-карточки */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statsLoading
          ? [1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-28" />)
          : kpiCards.map((kpi) => (
              <Card key={kpi.title}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{kpi.title}</span>
                    <div className="text-muted-foreground">{kpi.icon}</div>
                  </div>
                  <div className="mt-2 text-2xl font-bold">{kpi.value}</div>
                  <div className="text-xs text-muted-foreground">{kpi.sub}</div>
                </CardContent>
              </Card>
            ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* воронка */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Воронка продаж</CardTitle>
          </CardHeader>
          <CardContent>
            {pipeline?.stages ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={pipeline.stages} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tickFormatter={formatCurrency} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: number) =>
                      new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(value)
                    }
                  />
                  <Bar dataKey="amount" fill="var(--chart-1)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Skeleton className="h-[250px]" />
            )}
          </CardContent>
        </Card>

        {/* график выручки */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Выручка по месяцам</CardTitle>
          </CardHeader>
          <CardContent>
            {revenue?.data ? (
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={revenue.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={formatCurrency} />
                  <Tooltip
                    formatter={(value: number) =>
                      new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(value)
                    }
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="var(--chart-2)"
                    fill="var(--chart-2)"
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <Skeleton className="h-[250px]" />
            )}
          </CardContent>
        </Card>
      </div>

      {/* лента активности */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Последние активности</CardTitle>
        </CardHeader>
        <CardContent>
          {feed?.items?.length ? (
            <div className="space-y-3">
              {feed.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between border-b pb-2 last:border-0">
                  <div>
                    <span className="text-sm font-medium">{item.title}</span>
                    <div className="text-xs text-muted-foreground">
                      {item.author.name} — {item.type}
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(item.created_at), "dd.MM HH:mm")}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Нет активностей</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
