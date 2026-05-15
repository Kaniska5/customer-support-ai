import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart3, Users, Ticket, AlertTriangle, ShieldAlert } from 'lucide-react'
import { analyticsApi } from '@/api'
import type { AnalyticsSummary } from '@/types'

function AdminCard({ title, value, icon: Icon, color, delay }: { title: string, value: string | number, icon: any, color: string, delay: number }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
      className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-slate-800">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </motion.div>
  )
}

export function AdminDashboardPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi.summary()
      .then(res => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">System Analytics</h2>
        <p className="text-slate-500 text-sm mt-1">Real-time overview of the AI support platform</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AdminCard title="Total Tickets" value={loading ? '...' : data?.total_tickets ?? 0} icon={Ticket} color="bg-indigo-100 text-indigo-600" delay={0} />
        <AdminCard title="Avg Response (min)" value={loading ? '...' : data?.avg_response_time_minutes.toFixed(1) ?? 0} icon={BarChart3} color="bg-violet-100 text-violet-600" delay={0.1} />
        <AdminCard title="Escalations" value={loading ? '...' : data?.escalated_tickets ?? 0} icon={AlertTriangle} color="bg-amber-100 text-amber-600" delay={0.2} />
        <AdminCard title="Guardrail Blocks" value={loading ? '...' : data?.guardrail_triggers_today ?? 0} icon={ShieldAlert} color="bg-red-100 text-red-600" delay={0.3} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-500" /> Top Performing Agents (Phase 2)
          </h3>
          <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-100 rounded-xl bg-slate-50">
            <p className="text-sm text-slate-400">Agent performance charts will appear here</p>
          </div>
        </div>
        
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-violet-500" /> Resolution Timeline (Phase 4)
          </h3>
          <div className="h-48 flex items-center justify-center border-2 border-dashed border-slate-100 rounded-xl bg-slate-50">
            <p className="text-sm text-slate-400">Resolution graphs will appear here</p>
          </div>
        </div>
      </div>
    </div>
  )
}
