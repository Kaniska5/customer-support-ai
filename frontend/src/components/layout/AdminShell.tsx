import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import { BarChart3, Activity, AlertTriangle, ScrollText, Bot, LogOut, Sparkles } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/api'
import { cn } from '@/utils/cn'

const adminNav = [
  { to: '/admin', icon: BarChart3, label: 'Analytics', exact: true },
  { to: '/admin/monitoring', icon: Activity, label: 'Monitoring' },
  { to: '/admin/escalations', icon: AlertTriangle, label: 'Escalations' },
  { to: '/admin/logs', icon: ScrollText, label: 'Agent Logs' },
]

export function AdminShell() {
  const location = useLocation()
  const { user, refreshToken, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    if (refreshToken) { try { await authApi.logout(refreshToken) } catch { /* silent */ } }
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 via-indigo-50/30 to-violet-50/20 overflow-hidden">
      {/* Admin Sidebar */}
      <aside className="w-64 flex flex-col border-r border-indigo-100/80 bg-white/80 backdrop-blur-xl shrink-0">
        <div className="p-6 border-b border-indigo-100/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-slate-800 text-sm">SupportAI</p>
              <p className="text-xs text-indigo-500 font-medium flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> Admin Console
              </p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {adminNav.map(({ to, icon: Icon, label, exact }) => (
            <NavLink key={to} to={to} end={exact}>
              {({ isActive }) => (
                <motion.div
                  whileHover={{ x: 3 }}
                  whileTap={{ scale: 0.97 }}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/30'
                      : 'text-slate-600 hover:bg-indigo-50 hover:text-indigo-700'
                  )}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {label}
                </motion.div>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-indigo-100/60">
          <div className="flex items-center gap-3 p-2 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
              {user?.email?.[0]?.toUpperCase() ?? 'A'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">Admin</p>
              <p className="text-xs text-slate-400 truncate">{user?.email}</p>
            </div>
            <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={handleLogout} className="text-slate-400 hover:text-red-500 transition-colors">
              <LogOut className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </aside>

      {/* Admin Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-indigo-100/60 bg-white/70 backdrop-blur-xl flex items-center px-6 shrink-0">
          <h1 className="text-lg font-bold text-slate-800">Admin Console</h1>
          <span className="ml-3 text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-600">ADMIN</span>
        </header>
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="p-6 h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
