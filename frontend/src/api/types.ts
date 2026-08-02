// --- общие типы ---

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
}

// --- пользователи ---

export interface User {
  id: string
  email: string
  name: string
  role: "admin" | "manager" | "viewer"
  is_active: boolean
  must_change_password: boolean
  avatar_url: string | null
  created_at: string
}

// --- авторизация ---

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

// --- теги ---

export interface Tag {
  id: string
  name: string
  color: string
}

// --- клиенты ---

export interface ClientOwner {
  id: string
  name: string
}

export interface Client {
  id: string
  name: string
  email: string | null
  phone: string | null
  company: string | null
  industry: string | null
  website: string | null
  address: string | null
  status: "lead" | "active" | "inactive"
  source: string | null
  owner: ClientOwner
  tags: Tag[]
  deals_count: number
  total_revenue: number
  created_at: string
  updated_at: string
}

// --- стадии ---

export interface Stage {
  id: string
  name: string
  position: number
  color: string
  is_won: boolean
  is_lost: boolean
}

// --- сделки ---

export interface Deal {
  id: string
  title: string
  client: { id: string; name: string }
  stage: Stage
  owner: ClientOwner
  amount: number | null
  currency: string
  probability: number
  expected_close_date: string | null
  priority: "low" | "medium" | "high" | "urgent"
  description: string | null
  position: number
  tags: Tag[]
  created_at: string
  updated_at: string
  closed_at: string | null
}

export interface KanbanCard {
  id: string
  title: string
  client: { id: string; name: string }
  owner: ClientOwner
  amount: number | null
  currency: string
  probability: number
  priority: "low" | "medium" | "high" | "urgent"
  expected_close_date: string | null
  position: number
  tags: Tag[]
}

export interface KanbanColumn {
  id: string
  name: string
  color: string
  position: number
  is_won: boolean
  is_lost: boolean
  deals: KanbanCard[]
  total_amount: number
  deals_count: number
}

export interface KanbanResponse {
  stages: KanbanColumn[]
}

// --- заметки ---

export interface Note {
  id: string
  content: string
  author: ClientOwner
  client_id: string | null
  deal_id: string | null
  is_pinned: boolean
  created_at: string
  updated_at: string
}

// --- активности ---

export interface Activity {
  id: string
  type: "call" | "meeting" | "email" | "task"
  title: string
  description: string | null
  author: ClientOwner
  client_id: string | null
  deal_id: string | null
  is_completed: boolean
  scheduled_at: string | null
  completed_at: string | null
  created_at: string
}

// --- дашборд ---

export interface DashboardStats {
  total_clients: number
  new_clients: number
  active_deals: number
  won_deals: number
  lost_deals: number
  total_revenue: number
  avg_deal_size: number
  conversion_rate: number
  avg_deal_cycle_days: number
}

export interface PipelineStage {
  name: string
  count: number
  amount: number
  color: string
}

export interface RevenueChartPoint {
  date: string
  revenue: number
  deals_count: number
}

export interface ActivityFeedItem {
  id: string
  type: string
  title: string
  author: ClientOwner
  created_at: string
}
