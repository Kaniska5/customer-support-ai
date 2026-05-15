import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Package, Search, ChevronRight } from 'lucide-react'
import { ordersApi } from '@/api'
import type { Order } from '@/types'
import { formatCurrency, formatDate } from '@/utils/cn'

const statusColors: Record<string, string> = {
  delivered: 'bg-green-100 text-green-700 border-green-200',
  shipped: 'bg-blue-100 text-blue-700 border-blue-200',
  delayed: 'bg-amber-100 text-amber-700 border-amber-200',
  cancelled: 'bg-red-100 text-red-700 border-red-200',
  pending: 'bg-slate-100 text-slate-600 border-slate-200',
}

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ordersApi.list({ page: 1, page_size: 20 })
      .then(res => setOrders(res.data.orders ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">My Orders</h2>
          <p className="text-slate-500 text-sm mt-1">Track and manage your recent purchases</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search orders..."
            className="pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 w-64"
          />
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-20 rounded-xl shimmer" />
            ))}
          </div>
        ) : orders.length === 0 ? (
          <div className="text-center py-16">
            <Package className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 font-medium">No orders found</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {orders.map(order => (
              <motion.div
                key={order.id}
                whileHover={{ backgroundColor: 'rgba(248, 250, 252, 1)' }}
                className="p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-50 border border-violet-100 flex items-center justify-center shrink-0">
                    <Package className="w-6 h-6 text-violet-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{order.order_number}</h3>
                    <p className="text-sm text-slate-500 mt-0.5">
                      {order.product_details.length} item{order.product_details.length > 1 ? 's' : ''} • {formatDate(order.created_at)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-6 sm:gap-8 ml-16 sm:ml-0">
                  <div className="text-left sm:text-right">
                    <p className="font-semibold text-slate-800">{formatCurrency(order.total_amount)}</p>
                    <span className={`inline-block mt-1 px-2.5 py-0.5 text-xs font-medium rounded-full border ${statusColors[order.status] ?? statusColors.pending}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-300 hidden sm:block" />
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
