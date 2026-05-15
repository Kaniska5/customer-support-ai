import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp, Zap } from 'lucide-react'

interface TimelineStep {
  step: string
  agent: string
  timestamp: string
  details: string
}

interface ExplainabilityPanelProps {
  timeline: TimelineStep[]
}

const AGENT_ICONS: Record<string, string> = {
  orchestrator: '🎯',
  order_agent: '📦',
  refund_agent: '💳',
  faq_agent: '📚',
  escalation_agent: '🚨',
  synthesizer: '✨',
}

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

export function ExplainabilityPanel({ timeline }: ExplainabilityPanelProps) {
  const [isOpen, setIsOpen] = useState(false)

  if (!timeline || timeline.length === 0) return null

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen(v => !v)}
        className="flex items-center gap-1.5 text-[11px] text-slate-500 hover:text-violet-600 transition-colors group"
      >
        <Zap className="w-3 h-3 group-hover:text-violet-500" />
        <span className="font-medium">Reasoning Timeline</span>
        <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded-full ml-1">
          {timeline.length} steps
        </span>
        {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="mt-2 rounded-xl border border-slate-200 bg-slate-50 p-3 space-y-0">
              {timeline.map((step, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05, duration: 0.2 }}
                  className="flex gap-3"
                >
                  {/* Connector line */}
                  <div className="flex flex-col items-center">
                    <div className="w-6 h-6 rounded-full bg-white border-2 border-violet-300 flex items-center justify-center text-[11px] shrink-0 shadow-sm">
                      {AGENT_ICONS[step.agent] ?? '🔹'}
                    </div>
                    {idx < timeline.length - 1 && (
                      <div className="w-px flex-1 bg-violet-200 my-1 min-h-[12px]" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="pb-3 flex-1 min-w-0">
                    <div className="flex items-baseline gap-2 flex-wrap">
                      <span className="text-[12px] font-semibold text-slate-700">{step.step}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {formatTimestamp(step.timestamp)}
                      </span>
                    </div>
                    {step.details && (
                      <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed break-words">
                        {step.details}
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
