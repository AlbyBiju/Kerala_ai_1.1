export type DocType =
  | 'commercial_invoice'
  | 'packing_list'
  | 'shipping_bill'
  | 'purchase_order'
  | 'quality_certificate'

export const DOC_TYPE_LABELS: Record<DocType, string> = {
  commercial_invoice: 'Commercial Invoice',
  packing_list: 'Packing List',
  shipping_bill: 'Shipping Bill',
  purchase_order: 'Purchase Order',
  quality_certificate: 'Quality Certificate',
}

export type ExtractionStatus = 'pending' | 'processing' | 'done' | 'failed'

export type ShipmentStatus = 'draft' | 'processing' | 'reviewed' | 'closed'

export type Severity = 'critical' | 'warning' | 'info'
export type DiscrepancyStatus = 'open' | 'acknowledged' | 'resolved'

export interface Shipment {
  id: string
  name: string
  description: string | null
  status: ShipmentStatus
  created_at: string
  updated_at: string
}

export interface DocumentItem {
  id: string
  shipment_id: string
  doc_type: DocType
  original_filename: string
  mime_type: string
  extraction_status: ExtractionStatus
  created_at: string
}

export interface Discrepancy {
  id: string
  shipment_id: string
  field_name: string
  document_a_id: string
  document_a_value: string
  document_b_id: string
  document_b_value: string
  severity: Severity
  status: DiscrepancyStatus
  created_at: string
}

export interface ChecklistItem {
  id: string
  shipment_id: string
  label: string
  is_passed: boolean
  notes: string | null
}

export interface DashboardResponse {
  total_sessions: number
  open_discrepancies: Record<Severity, number>
  overall_pass_rate: number
  recent_sessions: Array<{
    id: string
    name: string
    status: ShipmentStatus
    created_at: string
  }>
}

export interface ShipmentDetail extends Shipment {
  documents?: DocumentItem[]
}
