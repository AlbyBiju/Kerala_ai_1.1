import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import type { ChecklistItem } from '../types'

export default function ChecklistPanel({ shipmentId }: { shipmentId: string }) {
  const { data: checklist } = useQuery({
    queryKey: ['checklist', shipmentId],
    queryFn: async () => {
      const { data } = await api.get<ChecklistItem[]>(`/shipments/${shipmentId}/checklist`)
      return data
    },
  })

  if (!checklist || checklist.length === 0) {
    return (
      <p className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
        Checklist will appear after analysis runs.
      </p>
    )
  }

  const passed = checklist.filter((c) => c.is_passed).length
  const score = Math.round((passed / checklist.length) * 100)

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-900">Export Readiness</h2>
        <span className="text-sm font-semibold text-slate-900">{score}%</span>
      </div>
      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all ${score === 100 ? 'bg-emerald-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-500'}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <ul className="mt-4 space-y-3">
        {checklist.map((item) => (
          <li key={item.id} className="flex items-start gap-3">
            <span
              className={`mt-0.5 inline-flex h-5 w-5 flex-none items-center justify-center rounded-full text-xs font-bold ${
                item.is_passed ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'
              }`}
            >
              {item.is_passed ? '✓' : '✕'}
            </span>
            <div>
              <p className="text-sm font-medium text-slate-900">{item.label}</p>
              {item.notes && <p className="text-xs text-slate-500">{item.notes}</p>}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
