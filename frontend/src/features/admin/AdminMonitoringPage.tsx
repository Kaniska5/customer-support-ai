import { Activity, Server, Database } from 'lucide-react'

export function AdminMonitoringPage() {
  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">System Monitoring</h2>
        <p className="text-slate-500 text-sm mt-1">Live LangSmith and infrastructure metrics (Phase 4)</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
        <Activity className="w-16 h-16 text-indigo-300 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-slate-800 mb-2">LangSmith Integration Pending</h3>
        <p className="text-slate-500 max-w-md mx-auto">
          In Phase 4, this page will embed the LangSmith dashboard to trace LLM chains, monitor token usage, and track agent latency.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-green-100 text-green-600 flex items-center justify-center">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-800">FastAPI Backend</h4>
            <p className="text-sm text-green-600 font-medium">Status: Healthy</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-green-100 text-green-600 flex items-center justify-center">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-800">PostgreSQL DB</h4>
            <p className="text-sm text-green-600 font-medium">Status: Connected</p>
          </div>
        </div>
      </div>
    </div>
  )
}
