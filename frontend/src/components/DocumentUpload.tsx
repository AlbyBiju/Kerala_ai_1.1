import { useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { DOC_TYPE_LABELS } from '../types'
import type { DocType } from '../types'

interface DocumentUploadProps {
  shipmentId: string
}

export default function DocumentUpload({ shipmentId }: DocumentUploadProps) {
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [docType, setDocType] = useState<DocType>('commercial_invoice')
  const [uploading, setUploading] = useState(false)
  const [loadingSamples, setLoadingSamples] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('doc_type', docType)
      await api.post(`/shipments/${shipmentId}/documents`, formData)
      toast.success(`${file.name} uploaded & extracted successfully`)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
      
      // Invalidate queries so documents list, discrepancies, and checklist refresh immediately
      await queryClient.invalidateQueries({ queryKey: ['documents', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['discrepancies', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['checklist', shipmentId] })
    } catch {
      toast.error('Upload failed. Check file type and size (max 20 MB).')
    } finally {
      setUploading(false)
    }
  }

  const handleLoadSamples = async () => {
    setLoadingSamples(true)
    try {
      await api.post(`/shipments/${shipmentId}/load-samples`)
      toast.success('Sample export documents loaded and analyzed!')
      await queryClient.invalidateQueries({ queryKey: ['documents', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['shipment', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['discrepancies', shipmentId] })
      await queryClient.invalidateQueries({ queryKey: ['checklist', shipmentId] })
    } catch {
      toast.error('Failed to load sample documents')
    } finally {
      setLoadingSamples(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Upload Document</h3>
        <button
          type="button"
          onClick={handleLoadSamples}
          disabled={loadingSamples}
          className="rounded border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
        >
          {loadingSamples ? 'Loading…' : '⚡ 1-Click Sample Docs'}
        </button>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragActive(false)
          const dropped = e.dataTransfer.files?.[0]
          if (dropped) setFile(dropped)
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-3 cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition ${
          dragActive ? 'border-slate-500 bg-slate-50' : 'border-slate-300 hover:border-slate-400'
        }`}
      >
        {file ? (
          <p className="text-sm font-medium text-slate-900">{file.name}</p>
        ) : (
          <p className="text-sm text-slate-500">
            Drag &amp; drop a file here, or <span className="font-medium text-slate-700">browse</span>
          </p>
        )}
        <p className="mt-1 text-xs text-slate-400">PDF, PNG, JPEG, TIFF, DOCX, XLSX — max 20 MB</p>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif,.docx,.xlsx"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <div className="mt-4 flex items-center gap-3">
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value as DocType)}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
        >
          {(Object.keys(DOC_TYPE_LABELS) as DocType[]).map((t) => (
            <option key={t} value={t}>
              {DOC_TYPE_LABELS[t]}
            </option>
          ))}
        </select>
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="ml-auto rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
      </div>
    </div>
  )
}
