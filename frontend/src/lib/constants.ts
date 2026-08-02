// общие словари для UI — чтоб не дублировать в компонентах

export const roleLabels: Record<string, string> = {
  admin: "Администратор",
  manager: "Менеджер",
  viewer: "Наблюдатель",
}

export const statusLabels: Record<string, string> = {
  lead: "Лид",
  active: "Активный",
  churned: "Ушел",
  inactive: "Неактивный",
}

export const priorityLabels: Record<string, string> = {
  urgent: "Срочный",
  high: "Высокий",
  medium: "Средний",
  low: "Низкий",
}

export const actTypeLabels: Record<string, string> = {
  call: "Звонок",
  meeting: "Встреча",
  email: "Письмо",
  task: "Задача",
}
