import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../lib/api'
import type { Shipment } from '../types'

interface CreateShipmentModalProps {
  open: boolean
  onClose: () => void
}

export default function CreateShipmentModal({ open, onClose }: CreateShipmentModalProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const createMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post<Shipment>('/shipments', {
        name: name.trim(),
        description: description.trim() || null,
      })
      return data
    },
    onSuccess: (created) => {
      toast.success('Shipment session created')
      queryClient.invalidateQueries({ queryKey: ['shipments'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      onClose()
      setName('')
      setDescription('')
      navigate(`/shipments/${created.id}`)
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail
      let errorMsg = 'Failed to create shipment session'
      if (typeof detail === 'string') {
        errorMsg = detail
      } else if (Array.isArray(detail) && detail.length > 0) {
        errorMsg = detail[0].msg || errorMsg
      } else if (err.message) {
        errorMsg = err.message
      }
      toast.error(errorMsg)
    },
  })

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-900">New Shipment Session</h2>
        <form
          className="mt-4 space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            if (name.trim()) createMutation.mutate()
          }}
        >
          <div>
            <label htmlFor="shipment-name" className="block text-sm font-medium text-slate-700">
              Name
            </label>
            <input
              id="shipment-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Shipment #INV-2026-001"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="shipment-desc" className="block text-sm font-medium text-slate-700">
              Description <span className="text-slate-400">(optional)</span>
            </label>
            <textarea
              id="shipment-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Seafood export to Singapore"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim() || createMutation.isPending}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating…' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
