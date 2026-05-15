import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ShoppingBag, Ticket, MessageSquare, TrendingUp, ArrowRight, Package, Clock } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { ordersApi, ticketsApi } from '@/api'
import type { Order, Ticket as TicketType } from '@/types'
import { formatCurrency, formatDate, truncate } from '@/utils/cn'

const statusColors: Record<string, string> = {
  delivered: 'bg-green-100 text-green-700',
  shipped: 'bg-blue-100 text-blue-700',
  delayed: 'bg-amber-100 text-amber-700',
  cancelled: 'bg-red-100 text-red-700',
  pending: 'bg-slate-100 text-slate-600',
  open: 'bg-violet-100 text-violet-700',
  in_progress: 'bg-blue-100 text-blue-700',
  resolved: 'bg-green-100 text-green-700',
  escalated: 'bg-red-100 text-red-700',
  closed: 'bg-slate-100 text-slate-500',
}

function StatCard({ icon: Icon, label, value, sub, color }: { icon: React.ElementType; label: string; value: string | number; sub?: string; color: string }) {
  return (
    <motion.div whileHover={{ y: -3 }} className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <p className="text-2xl font-bold text-slate-800">{value}</p>
      <p className="text-sm font-medium text-slate-600 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </motion.div>
  )
}

function SkeletonRow() {
  return <div className="h-12 rounded-xl shimmer" />
}

export function DashboardPage() {
  const { user } = useAuthStore()
  const [orders, setOrders] = useState<Order[]>([])
  const [tickets, setTickets] = useState<TicketType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      ordersApi.list({ page: 1, page_size: 5 }),
      ticketsApi.list(),
    ]).then(([oRes, tRes]) => {
      setOrders(oRes.data.orders ?? [])
      setTickets(tRes.data.tickets ?? [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h2 className="text-2xl font-bold text-slate-800">
          {greeting}, {user?.full_name?.split(' ')[0] ?? 'there'} 👋
        </h2>
        <p className="text-slate-500 text-sm mt-1">Here's your support overview for today</p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: ShoppingBag, label: 'Total Orders', value: loading ? '—' : orders.length, sub: 'Last 30 days', color: 'bg-violet-100 text-violet-600' },
          { icon: Ticket, label: 'Open Tickets', value: loading ? '—' : tickets.filter(t => t.status === 'open').length, sub: 'Awaiting response', color: 'bg-amber-100 text-amber-600' },
          { icon: MessageSquare, label: 'AI Chats', value: '—', sub: 'Coming in Phase 2', color: 'bg-indigo-100 text-indigo-600' },
          { icon: TrendingUp, label: 'Resolved', value: loading ? '—' : tickets.filter(t => t.status === 'resolved').length, sub: 'All time', color: 'bg-green-100 text-green-600' },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
            <StatCard {...s} />
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between p-5 border-b border-slate-50">
            <div className="flex items-center gap-2">
              <Package className="w-4 h-4 text-violet-500" />
              <h3 className="font-semibold text-slate-800">Recent Orders</h3>
            </div>
            <Link to="/orders" className="text-xs text-violet-600 font-medium flex items-center gap-1 hover:text-violet-700">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="p-4 space-y-2">
            {loading ? Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />) :
              orders.length === 0 ? <p className="text-sm text-slate-400 text-center py-6">No orders yet</p> :
              orders.slice(0, 5).map(order => (
                <div key={order.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-800">{order.order_number}</p>
                    <p className="text-xs text-slate-400 truncate">{truncate(order.product_details?.[0]?.name ?? '—', 40)}</p>
                  </div>
                  <div className="text-right shrink-0 ml-3">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusColors[order.status] ?? 'bg-slate-100 text-slate-500'}`}>
                      {order.status}
                    </span>
                    <p className="text-xs text-slate-400 mt-1">{formatCurrency(order.total_amount)}</p>
                  </div>
                </div>
              ))}
          </div>
        </motion.div>

        {/* Recent Tickets */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between p-5 border-b border-slate-50">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-violet-500" />
              <h3 className="font-semibold text-slate-800">Recent Tickets</h3>
            </div>
            <Link to="/tickets" className="text-xs text-violet-600 font-medium flex items-center gap-1 hover:text-violet-700">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="p-4 space-y-2">
            {loading ? Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />) :
              tickets.length === 0 ? (
                <div className="text-center py-8 space-y-3">
                  <p className="text-sm text-slate-400">No tickets yet</p>
                  <Link to="/chat" className="inline-flex items-center gap-1 text-sm font-medium text-violet-600 hover:text-violet-700">
                    Start AI chat <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              ) :
              tickets.slice(0, 5).map(ticket => (
                <div key={ticket.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-800">{ticket.ticket_number}</p>
                    <p className="text-xs text-slate-400 truncate">{truncate(ticket.subject, 40)}</p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ml-3 ${statusColors[ticket.status] ?? 'bg-slate-100 text-slate-500'}`}>
                    {ticket.status.replace('_', ' ')}
                  </span>
                </div>
              ))}
          </div>
        </motion.div>
      </div>

      {/* AI Support CTA */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="rounded-2xl gradient-primary p-6 flex items-center justify-between shadow-lg shadow-violet-500/25 relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-32 opacity-10 bg-white blur-2xl rounded-full" />
        <div className="relative">
          <h3 className="font-bold text-white text-lg">Need help with an order?</h3>
          <p className="text-violet-200 text-sm mt-1">Our AI agents resolve most issues in under 2 seconds</p>
        </div>
        <Link to="/chat" className="relative shrink-0">
          <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-violet-700 font-semibold text-sm shadow-md hover:shadow-lg transition-all">
            <MessageSquare className="w-4 h-4" /> Start chat
          </motion.div>
        </Link>
      </motion.div>
    </div>
  )
}
