import { motion } from 'framer-motion'

interface ConfidenceBarProps {
  score: number // 0.0 – 1.0
}

function getConfidenceStyle(score: number) {
  if (score >= 0.8) return { label: 'High', bar: 'bg-emerald-500', text: 'text-emerald-700', track: 'bg-emerald-100' }
  if (score >= 0.5) return { label: 'Medium', bar: 'bg-amber-500', text: 'text-amber-700', track: 'bg-amber-100' }
  return { label: 'Low', bar: 'bg-red-400', text: 'text-red-600', track: 'bg-red-100' }
}

export function ConfidenceBar({ score }: ConfidenceBarProps) {
  const pct = Math.round(score * 100)
  const style = getConfidenceStyle(score)

  return (
    <div className="flex items-center gap-2 mt-1">
      <span className={`text-[10px] font-semibold uppercase tracking-wide ${style.text} w-12 shrink-0`}>
        {style.label}
      </span>
      <div className={`flex-1 h-1.5 rounded-full ${style.track} overflow-hidden`}>
        <motion.div
          className={`h-full rounded-full ${style.bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
        />
      </div>
      <span className={`text-[10px] font-mono font-bold ${style.text} w-8 text-right`}>
        {pct}%
      </span>
    </div>
  )
}
