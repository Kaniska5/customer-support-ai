import { ScrollText } from 'lucide-react'

export function AdminLogsPage() {
  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Agent Action Logs</h2>
        <p className="text-slate-500 text-sm mt-1">Audit trail for all AI agent decisions and tool calls</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-16 text-center">
          <ScrollText className="w-16 h-16 text-slate-200 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 mb-2">Logs Available in Phase 4</h3>
          <p className="text-slate-500 max-w-md mx-auto">
            This dashboard will display the <code>agent_logs</code> and <code>guardrail_events</code> tables, showing exactly why an AI made a specific decision, what tools it called, and which guardrails were triggered.
          </p>
        </div>
      </div>
    </div>
  )
}
