import { CalendarCheck2, CheckSquare2, Gauge, LayoutDashboard, LogOut, Menu, Sparkles, X } from 'lucide-react'
import { useRef, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useDialogFocus } from '../hooks/useDialogFocus'

const navigation = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/tareas', label: 'Tareas', icon: CheckSquare2 },
  { to: '/planificar', label: 'Planificar con IA', icon: Sparkles },
  { to: '/plan-dia', label: 'Plan del día', icon: CalendarCheck2 },
  { to: '/carga', label: 'Carga de trabajo', icon: Gauge },
]

function NavigationLinks({ onNavigate }: { onNavigate?: () => void }) {
  return navigation.map(({ to, label, icon: Icon }) => (
    <NavLink
      key={to}
      to={to}
      onClick={onNavigate}
      className={({ isActive }) => `flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}`}
    >
      <Icon aria-hidden="true" size={18} />
      {label}
    </NavLink>
  ))
}

interface MobileNavigationProps {
  email?: string
  onClose: () => void
  onLogout: () => void
}

function MobileNavigation({ email, onClose, onLogout }: MobileNavigationProps) {
  const drawerRef = useRef<HTMLElement>(null)
  useDialogFocus(drawerRef, onClose)

  return (
    <div className="fixed inset-0 z-50 lg:hidden" role="presentation">
      <button
        type="button"
        className="absolute inset-0 h-full w-full cursor-default bg-slate-950/45"
        onClick={onClose}
        aria-label="Cerrar navegación"
      />
      <aside
        ref={drawerRef}
        className="relative flex h-full w-[min(20rem,88vw)] flex-col border-r border-slate-200 bg-white p-4 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-label="Navegación principal"
      >
        <div className="flex items-center justify-between gap-3 px-2 py-2">
          <NavLink to="/dashboard" onClick={onClose} className="flex items-center gap-3 text-slate-900">
            <span className="flex size-9 items-center justify-center rounded-xl bg-indigo-600 text-white">
              <Sparkles aria-hidden="true" size={18} />
            </span>
            <span className="font-semibold">Gestor de tareas</span>
          </NavLink>
          <button
            type="button"
            onClick={onClose}
            data-autofocus
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
            aria-label="Cerrar menú"
          >
            <X aria-hidden="true" size={20} />
          </button>
        </div>
        <nav className="mt-7 space-y-1" aria-label="Navegación principal">
          <NavigationLinks onNavigate={onClose} />
        </nav>
        <div className="mt-auto border-t border-slate-200 pt-4">
          <p className="truncate px-3 text-sm font-medium text-slate-700">{email}</p>
          <button type="button" onClick={onLogout} className="mt-3 flex min-h-11 w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900">
            <LogOut aria-hidden="true" size={18} />
            Cerrar sesión
          </button>
        </div>
      </aside>
    </div>
  )
}

export function AppLayout() {
  const { logout, user } = useAuth()
  const [isMobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 lg:flex">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white p-4 lg:sticky lg:top-0 lg:flex lg:h-screen">
        <NavLink to="/dashboard" className="flex items-center gap-3 px-2 py-3 text-slate-900">
          <span className="flex size-9 items-center justify-center rounded-xl bg-indigo-600 text-white"><Sparkles aria-hidden="true" size={18} /></span>
          <span className="font-semibold">Gestor de tareas</span>
        </NavLink>
        <nav className="mt-8 space-y-1" aria-label="Navegación principal"><NavigationLinks /></nav>
        <div className="mt-auto border-t border-slate-200 pt-4">
          <p className="truncate px-3 text-sm font-medium text-slate-700">{user?.email}</p>
          <button type="button" onClick={logout} className="mt-3 flex min-h-11 w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"><LogOut aria-hidden="true" size={18} />Cerrar sesión</button>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <NavLink to="/dashboard" className="flex items-center gap-2 font-semibold text-slate-900"><span className="flex size-8 items-center justify-center rounded-lg bg-indigo-600 text-white"><Sparkles aria-hidden="true" size={16} /></span>Gestor de tareas</NavLink>
            <button
              type="button"
              onClick={() => setMobileNavOpen(true)}
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
              aria-expanded={isMobileNavOpen}
              aria-haspopup="dialog"
              aria-label="Abrir navegación"
            >
              <Menu aria-hidden="true" size={20} />
            </button>
          </div>
        </header>
        <Outlet />
      </div>

      {isMobileNavOpen && (
        <MobileNavigation
          email={user?.email}
          onClose={() => setMobileNavOpen(false)}
          onLogout={logout}
        />
      )}
    </div>
  )
}
