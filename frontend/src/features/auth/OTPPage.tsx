import { useState, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldCheck, ArrowRight } from 'lucide-react'
import { authApi } from '@/api'
import { AuthLayout } from './AuthLayout'

export function OTPPage() {
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const location = useLocation()
  const navigate = useNavigate()
  const { email, detail } = (location.state as { email?: string; detail?: string }) ?? {}

  const handleChange = (idx: number, val: string) => {
    if (!/^\d?$/.test(val)) return
    const next = [...otp]
    next[idx] = val
    setOtp(next)
    if (val && idx < 5) inputRefs.current[idx + 1]?.focus()
  }

  const handleKeyDown = (idx: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[idx] && idx > 0) inputRefs.current[idx - 1]?.focus()
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (pasted.length === 6) setOtp(pasted.split(''))
    e.preventDefault()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const code = otp.join('')
    if (code.length < 6) { setError('Please enter all 6 digits'); return }
    setError(''); setLoading(true)
    try {
      await authApi.verifyOtp({ email: email!, otp_code: code, purpose: 'email_verify' })
      setSuccess('Email verified! Redirecting to login...')
      setTimeout(() => navigate('/login'), 1500)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg ?? 'Invalid OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout title="Verify your email" subtitle={`Enter the 6-digit code sent to ${email ?? 'your email'}`}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {detail && (
          <div className="p-3 rounded-xl bg-violet-50 border border-violet-200 text-xs text-violet-700 font-mono">
            {detail}
          </div>
        )}
        {error && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600">{error}</motion.div>
        )}
        {success && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-xl bg-green-50 border border-green-200 text-sm text-green-600 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" />{success}
          </motion.div>
        )}

        {/* OTP Input boxes */}
        <div className="flex gap-3 justify-center" onPaste={handlePaste}>
          {otp.map((digit, idx) => (
            <motion.input
              key={idx}
              ref={el => { inputRefs.current[idx] = el }}
              type="text" inputMode="numeric" maxLength={1}
              value={digit}
              onChange={e => handleChange(idx, e.target.value)}
              onKeyDown={e => handleKeyDown(idx, e)}
              whileFocus={{ scale: 1.05 }}
              className="w-11 h-13 text-center text-xl font-bold rounded-xl border-2 border-slate-200 bg-white text-slate-800 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"
            />
          ))}
        </div>

        <motion.button type="submit" disabled={loading}
          whileHover={{ scale: loading ? 1 : 1.01 }} whileTap={{ scale: loading ? 1 : 0.98 }}
          className="w-full py-2.5 px-4 rounded-xl gradient-primary text-white text-sm font-semibold shadow-lg shadow-violet-500/30 transition-all disabled:opacity-60 flex items-center justify-center gap-2">
          {loading ? <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            : <>Verify email <ArrowRight className="w-4 h-4" /></>}
        </motion.button>
      </form>
    </AuthLayout>
  )
}
