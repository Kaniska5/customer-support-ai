import { Bell, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { useLocation } from 'react-router-dom'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/orders': 'My Orders',
  '/tickets': 'Support Tickets',
  '/chat': 'AI Support Chat',
  '/profile': 'Profile',
}

export function Topbar() {
  const location = useLocation()
  const { user } = useAuthStore()
  const title = PAGE_TITLES[location.pathname] ?? 'SupportAI'

  return (
    <header className="h-16 border-b border-violet-100/60 bg-white/70 backdrop-blur-xl flex items-center justify-between px-6 shrink-0">
      <div>
        <h1 className="text-lg font-bold text-slate-800">{title}</h1>
        <p className="text-xs text-slate-400">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </div>
      <div className="flex items-center gap-3">
        {/* Search (placeholder for future) */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="w-9 h-9 rounded-xl border border-violet-100 bg-violet-50/50 flex items-center justify-center text-slate-500 hover:text-violet-600 transition-colors"
        >
          <Search className="w-4 h-4" />
        </motion.button>

        {/* Notifications (placeholder for Phase 4) */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="w-9 h-9 rounded-xl border border-violet-100 bg-violet-50/50 flex items-center justify-center text-slate-500 hover:text-violet-600 transition-colors relative"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-violet-500" />
        </motion.button>

        {/* User chip */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-violet-50 border border-violet-100">
          <div className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center text-white text-xs font-bold">
            {user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? 'U'}
          </div>
          <span className="text-sm font-medium text-slate-700">{user?.full_name?.split(' ')[0] ?? 'User'}</span>
        </div>
      </div>
    </header>
  )
}
