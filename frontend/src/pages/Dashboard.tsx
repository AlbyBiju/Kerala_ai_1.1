import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import api from '../lib/api'
import type { DashboardResponse, Shipment } from '../types'

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700',
  processing: 'bg-amber-100 text-amber-800',
  reviewed: 'bg-emerald-100 text-emerald-800',
  closed: 'bg-blue-100 text-blue-800',
}

export default function Dashboard() {
  const { data: dashboard, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const { data } = await api.get<DashboardResponse>('/dashboard')
      return data
    },
  })

  const { data: shipments } = useQuery({
    queryKey: ['shipments'],
    queryFn: async () => {
      const { data } = await api.get<Shipment[]>('/shipments')
      return data
    },
  })

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading dashboard…</p>
  }
  if (isError || !dashboard) {
    return <p className="text-sm text-red-600">Failed to load dashboard metrics.</p>
  }

  const { critical, warning, info } = dashboard.open_discrepancies
  const passRatePct = Math.round(dashboard.overall_pass_rate * 100)
  const donutData = [
    { name: 'Passed checks', value: passRatePct },
    { name: 'Failed checks', value: Math.max(0, 100 - passRatePct) },
  ]

  const statCards = [
    { label: 'Total Sessions', value: dashboard.total_sessions, cls: 'text-slate-900' },
    { label: 'Open Critical', value: critical, cls: 'text-red-600' },
    { label: 'Open Warnings', value: warning, cls: 'text-amber-600' },
    { label: 'Open Info', value: info, cls: 'text-blue-600' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
      <p className="mt-1 text-sm text-slate-500">Aggregate verification health at a glance.</p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{card.label}</p>
            <p className={`mt-2 text-3xl font-bold ${card.cls}`}>{card.value}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5 lg:col-span-1">
          <h2 className="text-sm font-semibold text-slate-900">Checklist Pass Rate</h2>
          <p className="mt-1 text-3xl font-bold text-slate-900">{passRatePct}%</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  dataKey="value"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  strokeWidth={0}
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#e2e8f0" />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white lg:col-span-2">
          <div className="border-b border-slate-200 px-5 py-3">
            <h2 className="text-sm font-semibold text-slate-900">Recent Sessions</h2>
          </div>
          {!dashboard.recent_sessions || dashboard.recent_sessions.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">
              No sessions yet.{' '}
              <Link to="/shipments" className="font-medium text-slate-700 underline">
                Create your first shipment
              </Link>
              .
            </p>
          ) : (
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-3">Name</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {dashboard.recent_sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="px-5 py-3">
                      <Link
                        to={`/shipments/${s.id}`}
                        className="font-medium text-slate-900 hover:underline"
                      >
                        {s.name}
                      </Link>
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[s.status] ?? 'bg-slate-100 text-slate-700'}`}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-500">
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {shipments === undefined && null}
    </div>
  )
}
