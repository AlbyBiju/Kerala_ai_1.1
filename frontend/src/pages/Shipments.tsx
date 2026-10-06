import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import type { Shipment } from '../types'
import CreateShipmentModal from '../components/CreateShipmentModal'

const STATUS_STYLES: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-700',
  processing: 'bg-amber-100 text-amber-800',
  reviewed: 'bg-emerald-100 text-emerald-800',
  closed: 'bg-blue-100 text-blue-800',
}

export default function Shipments() {
  const [modalOpen, setModalOpen] = useState(false)
  const { data: shipments, isLoading, isError } = useQuery({
    queryKey: ['shipments'],
    queryFn: async () => {
      const { data } = await api.get<Shipment[]>('/shipments')
      return data
    },
  })

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Shipment Sessions</h1>
          <p className="mt-1 text-sm text-slate-500">
            Verify export documents before you ship.
          </p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
        >
          + New Shipment
        </button>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white">
        {isLoading ? (
          <p className="p-8 text-center text-sm text-slate-500">Loading sessions…</p>
        ) : isError ? (
          <p className="p-8 text-center text-sm text-red-600">Failed to load shipment sessions.</p>
        ) : !shipments || shipments.length === 0 ? (
          <p className="p-8 text-center text-sm text-slate-500">
            No shipment sessions yet. Create your first one to get started.
          </p>
        ) : (
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-6 py-3">Name</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Created</th>
                <th className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {shipments.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50">
                  <td className="px-6 py-4">
                    <Link to={`/shipments/${s.id}`} className="font-medium text-slate-900 hover:underline">
                      {s.name}
                    </Link>
                    {s.description && (
                      <p className="text-xs text-slate-500">{s.description}</p>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[s.status] ?? 'bg-slate-100 text-slate-700'}`}
                    >
                      {s.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {new Date(s.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/shipments/${s.id}`}
                      className="text-sm font-medium text-slate-700 hover:text-slate-900"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <CreateShipmentModal open={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  )
}
