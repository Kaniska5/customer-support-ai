import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, ArrowRight, ArrowLeft } from 'lucide-react'
import { authApi } from '@/api'
import { AuthLayout } from './AuthLayout'

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState<{ message: string; detail?: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const { data } = await authApi.forgotPassword(email)
      setSent(data)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <AuthLayout title="Check your inbox" subtitle="We sent you a password reset link">
        <div className="space-y-4 text-center">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-green-50 border border-green-200 flex items-center justify-center">
            <Mail className="w-8 h-8 text-green-500" />
          </div>
          <p className="text-sm text-slate-600">{sent.message}</p>
          {sent.detail && (
            <div className="p-3 rounded-xl bg-violet-50 border border-violet-200 text-xs text-violet-700 font-mono text-left">
              {sent.detail}
            </div>
          )}
          <Link to="/reset-password"
            className="w-full py-2.5 px-4 rounded-xl gradient-primary text-white text-sm font-semibold shadow-lg shadow-violet-500/30 flex items-center justify-center gap-2">
            Enter reset token <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/login" className="flex items-center justify-center gap-1 text-sm text-slate-500 hover:text-violet-600">
            <ArrowLeft className="w-4 h-4" /> Back to login
          </Link>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Forgot password?" subtitle="Enter your email and we'll send a reset link">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600">{error}</motion.div>
        )}
        <div className="space-y-1.5">
          <label className="text-sm font-medium text-slate-700">Email address</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
              placeholder="you@example.com"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all" />
          </div>
        </div>
        <motion.button type="submit" disabled={loading}
          whileHover={{ scale: loading ? 1 : 1.01 }} whileTap={{ scale: loading ? 1 : 0.98 }}
          className="w-full py-2.5 px-4 rounded-xl gradient-primary text-white text-sm font-semibold shadow-lg shadow-violet-500/30 disabled:opacity-60 flex items-center justify-center gap-2">
          {loading ? <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            : <>Send reset link <ArrowRight className="w-4 h-4" /></>}
        </motion.button>
        <Link to="/login" className="flex items-center justify-center gap-1 text-sm text-slate-500 hover:text-violet-600">
          <ArrowLeft className="w-4 h-4" /> Back to login
        </Link>
      </form>
    </AuthLayout>
  )
}
