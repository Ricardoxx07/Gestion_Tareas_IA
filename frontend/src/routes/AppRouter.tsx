import { Navigate, Route, Routes } from 'react-router-dom'
import { ConnectionPage } from '../pages/ConnectionPage'
import { DashboardPage } from '../pages/DashboardPage'
import { DayPlanPage } from '../pages/DayPlanPage'
import { LoginPage } from '../pages/LoginPage'
import { PlannerPage } from '../pages/PlannerPage'
import { RegisterPage } from '../pages/RegisterPage'
import { TaskDetailPage } from '../pages/TaskDetailPage'
import { TasksPage } from '../pages/TasksPage'
import { WorkloadPage } from '../pages/WorkloadPage'
import { AppLayout } from '../layouts/AppLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { PublicRoute } from './PublicRoute'

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />
      </Route>
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/tareas" element={<TasksPage />} />
          <Route path="/tareas/:tareaId" element={<TaskDetailPage />} />
          <Route path="/planificar" element={<PlannerPage />} />
          <Route path="/plan-dia" element={<DayPlanPage />} />
          <Route path="/carga" element={<WorkloadPage />} />
        </Route>
      </Route>
      <Route path="/conexion" element={<ConnectionPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
