import { Navigate, Route, Routes } from "react-router"
import { useAuth } from "@/hooks/useAuth"
import AppLayout from "@/components/layout/AppLayout"
import LoginPage from "@/pages/LoginPage"
import RegisterPage from "@/pages/RegisterPage"
import ChangePasswordPage from "@/pages/ChangePasswordPage"
import ClientsPage from "@/pages/ClientsPage"
import ClientCreatePage from "@/pages/ClientCreatePage"
import ClientEditPage from "@/pages/ClientEditPage"
import ClientDetailPage from "@/pages/ClientDetailPage"
import DealsPage from "@/pages/DealsPage"
import DealsListPage from "@/pages/DealsListPage"
import DealCreatePage from "@/pages/DealCreatePage"
import DealEditPage from "@/pages/DealEditPage"
import DealDetailPage from "@/pages/DealDetailPage"
import DashboardPage from "@/pages/DashboardPage"
import SettingsPage from "@/pages/SettingsPage"
import UsersPage from "@/pages/UsersPage"

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-muted-foreground">Загрузка...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user?.must_change_password) {
    return <Navigate to="/change-password" replace />
  }

  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* публичные роуты */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/change-password" element={<ChangePasswordPage />} />

      {/* защищенные роуты */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/clients/new" element={<ClientCreatePage />} />
        <Route path="/clients/:id" element={<ClientDetailPage />} />
        <Route path="/clients/:id/edit" element={<ClientEditPage />} />
        <Route path="/deals" element={<DealsPage />} />
        <Route path="/deals/list" element={<DealsListPage />} />
        <Route path="/deals/new" element={<DealCreatePage />} />
        <Route path="/deals/:id" element={<DealDetailPage />} />
        <Route path="/deals/:id/edit" element={<DealEditPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/users" element={<UsersPage />} />
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
