// ─── Auth Types ───────────────────────────────────────────────────────────────
export interface User {
  id: string
  email: string
  role: 'customer' | 'admin'
  is_verified: boolean
  full_name?: string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenResponse
}

// ─── Order Types ──────────────────────────────────────────────────────────────
export type OrderStatus = 'pending' | 'shipped' | 'delivered' | 'delayed' | 'cancelled'

export interface ProductItem {
  name: string
  sku: string
  qty: number
  price: number
}

export interface Order {
  id: string
  order_number: string
  status: OrderStatus
  total_amount: number
  currency: string
  product_details: ProductItem[]
  shipping_address?: string
  tracking_number?: string
  estimated_delivery?: string
  delivered_at?: string
  is_refund_eligible: boolean
  created_at: string
}

export interface OrderListResponse {
  orders: Order[]
  total: number
  page: number
  page_size: number
}

// ─── Ticket Types ─────────────────────────────────────────────────────────────
export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'escalated' | 'closed'
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Ticket {
  id: string
  ticket_number: string
  subject: string
  description?: string
  status: TicketStatus
  priority: TicketPriority
  assigned_agent?: string
  created_at: string
  updated_at?: string
}

export interface TicketListResponse {
  tickets: Ticket[]
  total: number
}

// ─── Chat Types (Phase 2 ready) ───────────────────────────────────────────────
export type ChatRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  agent_name?: string
  confidence_score?: number
  sentiment?: string
  metadata?: Record<string, unknown>
  created_at: string
  // Optimistic UI
  isLoading?: boolean
  isError?: boolean
}

// ─── Analytics Types (Phase 4 ready) ─────────────────────────────────────────
export interface AnalyticsSummary {
  total_tickets: number
  open_tickets: number
  resolved_tickets: number
  escalated_tickets: number
  avg_response_time_minutes: number
  customer_satisfaction_score?: number
  top_agents: Array<{ agent: string; count: number }>
  guardrail_triggers_today: number
}

// ─── API Error ────────────────────────────────────────────────────────────────
export interface ApiError {
  detail: string
  status?: number
}
