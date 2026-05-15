import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Bot, Sparkles, Zap, Shield, BarChart3, MessageSquare, ArrowRight, CheckCircle } from 'lucide-react'

const features = [
  { icon: Bot, title: 'Agentic AI', desc: 'Specialized agents for orders, refunds, and FAQs — powered by LangGraph orchestration.' },
  { icon: Zap, title: 'Instant Responses', desc: 'From 6-hour wait times to sub-second AI answers. 24/7, no queue.' },
  { icon: Shield, title: 'Smart Guardrails', desc: 'Built-in safety: refund thresholds, PII protection, session isolation.' },
  { icon: BarChart3, title: 'Full Observability', desc: 'Every decision logged. Real-time analytics, escalation tracking, LangSmith monitoring.' },
]

const stats = [
  { value: '< 2s', label: 'Avg response time' },
  { value: '94%', label: 'Resolution rate' },
  { value: '10k+', label: 'Queries/day' },
  { value: '4.8★', label: 'CSAT score' },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white overflow-hidden">
      {/* Nav */}
      <nav className="fixed top-0 inset-x-0 z-50 h-16 border-b border-slate-100 bg-white/80 backdrop-blur-xl flex items-center justify-between px-8">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl gradient-primary flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-slate-800">SupportAI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-slate-600 hover:text-violet-600 transition-colors px-4 py-2">Sign in</Link>
          <Link to="/signup"
            className="text-sm font-semibold px-4 py-2 rounded-xl gradient-primary text-white shadow-md shadow-violet-500/25 hover:shadow-violet-500/40 transition-all">
            Get started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-8 text-center relative">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-violet-100/60 blur-3xl" />
        </div>
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="relative max-w-3xl mx-auto">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-50 border border-violet-200 text-xs font-semibold text-violet-700 mb-6">
            <Sparkles className="w-3.5 h-3.5" /> Powered by LangGraph + Gemini AI
          </motion.div>
          <h1 className="text-5xl font-extrabold text-slate-900 leading-tight mb-6">
            AI Customer Support<br />
            <span className="bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              That Actually Works
            </span>
          </h1>
          <p className="text-xl text-slate-500 mb-10 max-w-xl mx-auto leading-relaxed">
            Multi-agent AI that handles 10,000+ queries/day. Instant order tracking, smart refunds, and seamless human escalation.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link to="/signup">
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                className="flex items-center gap-2 px-6 py-3 rounded-xl gradient-primary text-white font-semibold shadow-xl shadow-violet-500/30 hover:shadow-violet-500/40 transition-all">
                Start for free <ArrowRight className="w-4 h-4" />
              </motion.div>
            </Link>
            <Link to="/login">
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                className="flex items-center gap-2 px-6 py-3 rounded-xl border border-slate-200 text-slate-700 font-semibold hover:border-violet-300 hover:text-violet-700 transition-all bg-white">
                Sign in to demo
              </motion.div>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="py-12 px-8 border-y border-slate-100 bg-slate-50">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map(({ value, label }, i) => (
            <motion.div key={label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <p className="text-3xl font-extrabold bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">{value}</p>
              <p className="text-sm text-slate-500 mt-1">{label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Enterprise-grade AI support</h2>
            <p className="text-slate-500">Production architecture with interview-winning design</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map(({ icon: Icon, title, desc }, i) => (
              <motion.div key={title}
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.08 }}
                whileHover={{ y: -4 }}
                className="p-6 rounded-2xl border border-slate-100 bg-white shadow-sm hover:shadow-lg hover:border-violet-100 transition-all">
                <div className="w-11 h-11 rounded-xl gradient-primary flex items-center justify-center mb-4 shadow-md shadow-violet-500/25">
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-800 mb-2">{title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-8">
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto text-center p-10 rounded-3xl gradient-primary shadow-2xl shadow-violet-500/30 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 right-0 w-40 h-40 rounded-full bg-white blur-2xl" />
            <div className="absolute bottom-0 left-0 w-40 h-40 rounded-full bg-white blur-2xl" />
          </div>
          <div className="relative">
            <h2 className="text-3xl font-extrabold text-white mb-3">Ready to transform support?</h2>
            <p className="text-violet-200 mb-8">Join and experience AI-powered customer service</p>
            <Link to="/signup">
              <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-white text-violet-700 font-bold shadow-lg hover:shadow-xl transition-all">
                Get started free <ArrowRight className="w-4 h-4" />
              </motion.div>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-8 border-t border-slate-100 text-center text-sm text-slate-400">
        <p>© 2025 SupportAI · Built with LangGraph, FastAPI, React</p>
      </footer>
    </div>
  )
}
