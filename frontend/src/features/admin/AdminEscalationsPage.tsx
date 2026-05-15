import { AlertTriangle } from 'lucide-react'

export function AdminEscalationsPage() {
  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Escalation Management</h2>
        <p className="text-slate-500 text-sm mt-1">Review tickets escalated by AI agents</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-16 text-center">
          <AlertTriangle className="w-16 h-16 text-slate-200 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-800 mb-2">Escalation Queue Empty</h3>
          <p className="text-slate-500 max-w-md mx-auto">
            Once Phase 2 (LangGraph) and Phase 4 (Human-in-the-loop) are implemented, AI agents will escalate complex or sensitive tickets here with confidence scores and reasoning summaries.
          </p>
        </div>
      </div>
    </div>
  )
}
