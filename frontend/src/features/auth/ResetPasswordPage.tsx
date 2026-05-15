import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, Eye, EyeOff, ArrowRight, CheckCircle } from 'lucide-react'
import { authApi } from '@/api'
import { AuthLayout } from './AuthLayout'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState(searchParams.get('token') ?? '')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password !== confirm) { setError('Passwords do not match'); return }
    setError(''); setLoading(true)
    try {
      await authApi.resetPassword({ token, new_password: password })
      setDone(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg ?? 'Reset failed. Token may be expired.')
    } finally {
      setLoading(false)
    }
  }

  const inputCls = 'w-full pl-10 pr-10 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all'

  if (done) {
    return (
      <AuthLayout title="Password reset!" subtitle="Your password has been updated">
        <div className="text-center space-y-4">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 200 }}
            className="w-16 h-16 mx-auto rounded-2xl bg-green-50 border border-green-200 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-green-500" />
          </motion.div>
          <p className="text-sm text-slate-600">Redirecting you to login...</p>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Reset your password" subtitle="Enter your reset token and new password">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600">{error}</motion.div>
        )}

        <div className="space-y-1.5">
          <label className="text-sm font-medium text-slate-700">Reset token</label>
          <input type="text" value={token} onChange={e => setToken(e.target.value)} required
            placeholder="Paste your reset token"
            className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all font-mono" />
        </div>

        {[
          { label: 'New password', val: password, set: setPassword },
          { label: 'Confirm password', val: confirm, set: setConfirm },
        ].map(({ label, val, set }) => (
          <div key={label} className="space-y-1.5">
            <label className="text-sm font-medium text-slate-700">{label}</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input type={showPw ? 'text' : 'password'} value={val} onChange={e => set(e.target.value)}
                required placeholder="••••••••" className={inputCls} />
              <button type="button" onClick={() => setShowPw(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        ))}

        <motion.button type="submit" disabled={loading}
          whileHover={{ scale: loading ? 1 : 1.01 }} whileTap={{ scale: loading ? 1 : 0.98 }}
          className="w-full py-2.5 px-4 rounded-xl gradient-primary text-white text-sm font-semibold shadow-lg shadow-violet-500/30 disabled:opacity-60 flex items-center justify-center gap-2">
          {loading ? <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            : <>Reset password <ArrowRight className="w-4 h-4" /></>}
        </motion.button>
        <p className="text-center text-sm"><Link to="/login" className="text-violet-600 hover:text-violet-700 font-medium">Back to login</Link></p>
      </form>
    </AuthLayout>
  )
}
