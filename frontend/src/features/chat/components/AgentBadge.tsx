import { motion } from 'framer-motion'

const AGENT_CONFIG: Record<string, { label: string; color: string; bg: string; border: string }> = {
  order_agent: {
    label: '📦 Order Agent',
    color: 'text-blue-700',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
  refund_agent: {
    label: '💳 Refund Agent',
    color: 'text-emerald-700',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
  },
  faq_agent: {
    label: '📚 FAQ Agent',
    color: 'text-violet-700',
    bg: 'bg-violet-50',
    border: 'border-violet-200',
  },
  escalation_agent: {
    label: '🚨 Escalation Agent',
    color: 'text-amber-700',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
  },
  orchestrator: {
    label: '🤖 Orchestrator',
    color: 'text-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
  },
}

interface AgentBadgeProps {
  agentName: string
  delay?: number
}

export function AgentBadge({ agentName, delay = 0 }: AgentBadgeProps) {
  const config = AGENT_CONFIG[agentName] ?? {
    label: `🔧 ${agentName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
    color: 'text-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
  }

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.8, y: 4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay, duration: 0.2, ease: 'easeOut' }}
      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${config.bg} ${config.color} ${config.border}`}
    >
      {config.label}
    </motion.span>
  )
}
