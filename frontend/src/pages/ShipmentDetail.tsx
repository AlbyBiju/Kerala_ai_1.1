import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { DOC_TYPE_LABELS } from '../types'
import type { Shipment, DocumentItem, ExtractionStatus } from '../types'
import DocumentUpload from '../components/DocumentUpload'
import DiscrepancyReview from '../components/DiscrepancyReview'
import ChecklistPanel from '../components/ChecklistPanel'

const STATUS_CHIP: Record<ExtractionStatus, string> = {
  pending: 'bg-slate-100 text-slate-600',
  processing: 'bg-amber-100 text-amber-800',
  done: 'bg-emerald-100 text-emerald-800',
  failed: 'bg-red-100 text-red-700',
}

export default function ShipmentDetail({ shipmentId: propId }: { shipmentId?: string }) {
  const queryClient = useQueryClient()
  const { id: paramId } = useParams<{ id: string }>()
  const shipmentId = propId || paramId || ''

  const { data: shipment, isLoading: shipmentLoading, isError: shipmentError } = useQuery({
    queryKey: ['shipment', shipmentId],
    queryFn: async () => {
      const { data } = await api.get<Shipment>(`/shipments/${shipmentId}`)
      return data
    },
  })

  const { data: documents } = useQuery({
    queryKey: ['documents', shipmentId],
    queryFn: async () => {
      const { data } = await api.get<DocumentItem[]>(`/shipments/${shipmentId}/documents`)
      return data
    },
    refetchInterval: (query) => {
      const docs = query.state.data
      const busy = docs?.some((d) => d.extraction_status === 'pending' || d.extraction_status === 'processing')
      return busy ? 3000 : false
    },
  })

  const analyseMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/shipments/${shipmentId}/analyse`)
      return data
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['documents', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['discrepancies', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['checklist', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId] })
      toast.success('Analysis completed! Discrepancies and checklist updated.')
    },
    onError: () => {
      toast.error('Failed to run analysis. Ensure documents are uploaded.')
    },
  })

  const downloadReport = async () => {
    try {
      const response = await api.get(`/shipments/${shipmentId}/report/pdf`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report-${shipmentId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast.success('Report downloaded')
    } catch {
      toast.error('Failed to download report')
    }
  }

  if (shipmentLoading) {
    return <p className="text-sm text-slate-500">Loading shipment…</p>
  }
  if (shipmentError || !shipment) {
    return <p className="text-sm text-red-600">Shipment session not found.</p>
  }

  const allExtracted = documents?.length
    ? documents.every((d) => d.extraction_status === 'done' || d.extraction_status === 'failed')
    : false

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{shipment.name}</h1>
          {shipment.description && (
            <p className="mt-1 text-sm text-slate-500">{shipment.description}</p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => analyseMutation.mutate()}
            disabled={analyseMutation.isPending || !documents?.length}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {analyseMutation.isPending ? 'Analyzing…' : 'Run Analysis'}
          </button>
          <button
            onClick={downloadReport}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
          >
            Download Report
          </button>
        </div>
      </div>

      {documents && documents.length > 0 && documents.length < 2 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          <strong>Tip:</strong> Cross-document verification compares pairs of documents (e.g. Commercial Invoice vs. Packing List). Upload a second document or click <strong>1-Click Sample Docs</strong> to detect discrepancies.
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-5 py-3">
            <h2 className="text-sm font-semibold text-slate-900">
              Documents {documents ? `(${documents.length})` : ''}
            </h2>
          </div>
          {!documents || documents.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">
              No documents uploaded yet. Upload the invoice, packing list, and other export documents.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {documents.map((d) => (
                <li key={d.id} className="flex items-center justify-between px-5 py-3">
                  <div>
                    <p className="text-sm font-medium text-slate-900">{d.original_filename}</p>
                    <p className="text-xs text-slate-500">
                      {DOC_TYPE_LABELS[d.doc_type] ?? d.doc_type}
                    </p>
                  </div>
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_CHIP[d.extraction_status]}`}
                  >
                    {d.extraction_status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <DocumentUpload shipmentId={shipmentId} />
      </div>

      {!allExtracted && documents && documents.length > 0 && (
        <p className="text-xs text-slate-400">
          Polling extraction status every 3 seconds while documents are processing…
        </p>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Discrepancy Review
          </h2>
          <DiscrepancyReview shipmentId={shipmentId} />
        </div>
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Checklist
          </h2>
          <ChecklistPanel shipmentId={shipmentId} />
        </div>
      </div>
    </div>
  )
}
