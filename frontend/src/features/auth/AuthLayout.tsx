import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Bot, Sparkles } from 'lucide-react'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: ReactNode
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen gradient-surface flex items-center justify-center p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-violet-200/30 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-indigo-200/30 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md relative"
      >
        {/* Brand mark */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.4 }}
            className="inline-flex items-center gap-2 mb-4"
          >
            <div className="w-10 h-10 rounded-2xl gradient-primary flex items-center justify-center shadow-xl shadow-violet-500/30">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl text-slate-800">SupportAI</span>
            <span className="text-xs font-semibold px-1.5 py-0.5 rounded-full bg-violet-100 text-violet-600 flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> AI
            </span>
          </motion.div>
          <h2 className="text-2xl font-bold text-slate-800">{title}</h2>
          <p className="text-slate-500 text-sm mt-1">{subtitle}</p>
        </div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.4 }}
          className="glass rounded-2xl p-8 shadow-xl shadow-violet-500/10 border border-white/60"
        >
          {children}
        </motion.div>
      </motion.div>
    </div>
  )
}
