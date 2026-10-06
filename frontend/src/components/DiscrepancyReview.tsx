import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../lib/api'
import type { Discrepancy, DiscrepancyStatus, Severity } from '../types'

const SEVERITY_STYLES: Record<Severity, { badge: string; border: string; label: string }> = {
  critical: { badge: 'bg-red-100 text-red-700', border: 'border-red-200', label: 'Critical' },
  warning: { badge: 'bg-amber-100 text-amber-800', border: 'border-amber-200', label: 'Warning' },
  info: { badge: 'bg-blue-100 text-blue-700', border: 'border-blue-200', label: 'Info' },
}

const SEVERITY_ORDER: Severity[] = ['critical', 'warning', 'info']

export default function DiscrepancyReview({ shipmentId }: { shipmentId: string }) {
  const queryClient = useQueryClient()

  const { data: discrepancies, isLoading } = useQuery({
    queryKey: ['discrepancies', shipmentId],
    queryFn: async () => {
      const { data } = await api.get<Discrepancy[]>(`/shipments/${shipmentId}/discrepancies`)
      return data
    },
  })

  const statusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: DiscrepancyStatus }) => {
      const { data } = await api.patch<Discrepancy>(
        `/shipments/${shipmentId}/discrepancies/${id}`,
        { status },
      )
      return data
    },
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['discrepancies', shipmentId] })
      const previous = queryClient.getQueryData<Discrepancy[]>(['discrepancies', shipmentId])
      queryClient.setQueryData<Discrepancy[]>(['discrepancies', shipmentId], (old) =>
        old?.map((d) => (d.id === id ? { ...d, status } : d)),
      )
      return { previous }
    },
    onError: () => {
      toast.error('Failed to update status')
      queryClient.invalidateQueries({ queryKey: ['discrepancies', shipmentId] })
    },
    onSuccess: () => {
      toast.success('Status updated')
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['discrepancies', shipmentId] })
      queryClient.invalidateQueries({ queryKey: ['checklist', shipmentId] })
    },
  })

  if (isLoading) return <p className="text-sm text-slate-500">Loading discrepancies…</p>
  if (!discrepancies || discrepancies.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
        <p className="font-medium text-slate-700">No discrepancies flagged.</p>
        <p className="mt-1 text-xs text-slate-500 leading-relaxed">
          All shared fields across uploaded documents match, or only a single document has been ingested. To perform cross-document discrepancy checking, upload at least two distinct documents (e.g., Commercial Invoice + Packing List) or click <strong>⚡ 1-Click Sample Docs</strong> above.
        </p>
      </div>
    )
  }

  const grouped = SEVERITY_ORDER.map((severity) => ({
    severity,
    items: discrepancies.filter((d) => d.severity === severity),
  })).filter((g) => g.items.length > 0)

  return (
    <div className="space-y-6">
      {grouped.map(({ severity, items }) => (
        <section key={severity}>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${SEVERITY_STYLES[severity].badge}`}
            >
              {SEVERITY_STYLES[severity].label}
            </span>
            <span className="text-xs text-slate-500">{items.length} finding(s)</span>
          </div>
          <div className="mt-3 space-y-3">
            {items.map((d) => (
              <div
                key={d.id}
                className={`rounded-xl border bg-white p-4 ${SEVERITY_STYLES[severity].border}`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-mono text-sm font-semibold text-slate-900">{d.field_name}</p>
                  <select
                    value={d.status}
                    onChange={(e) =>
                      statusMutation.mutate({
                        id: d.id,
                        status: e.target.value as DiscrepancyStatus,
                      })
                    }
                    className="rounded-lg border border-slate-300 px-2 py-1 text-xs focus:border-slate-500 focus:outline-none"
                  >
                    <option value="open">open</option>
                    <option value="acknowledged">acknowledged</option>
                    <option value="resolved">resolved</option>
                  </select>
                </div>
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs font-medium text-slate-500">Document A</p>
                    <p className="mt-1 text-sm text-slate-900">{d.document_a_value}</p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3">
                    <p className="text-xs font-medium text-slate-500">Document B</p>
                    <p className="mt-1 text-sm text-slate-900">{d.document_b_value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
