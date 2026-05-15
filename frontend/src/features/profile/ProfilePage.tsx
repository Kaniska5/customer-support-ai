import { useAuthStore } from '@/store/authStore'
import { User, Mail, Shield, Calendar, Key } from 'lucide-react'
import { formatDate } from '@/utils/cn'

export function ProfilePage() {
  const { user } = useAuthStore()

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Profile Settings</h2>
        <p className="text-slate-500 text-sm mt-1">Manage your account and preferences</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Header */}
        <div className="h-32 bg-gradient-to-r from-violet-100 to-indigo-50" />
        <div className="px-8 pb-8">
          <div className="-mt-12 flex items-end justify-between mb-6">
            <div className="flex items-end gap-5">
              <div className="w-24 h-24 rounded-2xl gradient-primary flex items-center justify-center text-white text-3xl font-bold border-4 border-white shadow-md">
                {user?.full_name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? 'U'}
              </div>
              <div className="mb-2">
                <h3 className="text-2xl font-bold text-slate-800">{user?.full_name ?? 'Customer'}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-slate-500">{user?.email}</span>
                  {user?.is_verified && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-[10px] font-bold uppercase">
                      <Shield className="w-3 h-3" /> Verified
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-6 mt-8">
            <div className="space-y-4">
              <h4 className="font-semibold text-slate-800 flex items-center gap-2">
                <User className="w-4 h-4 text-violet-500" /> Personal Info
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-400">Full Name</label>
                  <p className="text-sm text-slate-800 font-medium">{user?.full_name ?? '—'}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">Account Role</label>
                  <p className="text-sm text-slate-800 font-medium capitalize">{user?.role}</p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">Member Since</label>
                  <p className="text-sm text-slate-800 font-medium flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    {formatDate(user?.created_at)}
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-slate-800 flex items-center gap-2">
                <Shield className="w-4 h-4 text-violet-500" /> Security
              </h4>
              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-400">Email Address</label>
                  <p className="text-sm text-slate-800 font-medium flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    {user?.email}
                  </p>
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">Password</label>
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-800 font-medium flex items-center gap-1.5">
                      <Key className="w-3.5 h-3.5 text-slate-400" />
                      ••••••••
                    </p>
                    <button className="text-xs font-semibold text-violet-600 hover:text-violet-700">Change</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
