import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_BASE = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

const api = axios.create({ baseURL: BASE_URL, timeout: 30000 });

// ── Types ──────────────────────────────────────────────────────────────────

export interface OrderItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  category?: string;
  hs_code?: string;
}

export interface OrderCreate {
  customer_name: string;
  customer_country: string;
  customer_email: string;
  items: OrderItem[];
  total_amount: number;
  currency: string;
}

export interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  customer_country: string;
  customer_email: string;
  items: OrderItem[];
  total_amount: number;
  currency: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ComplianceResult {
  id: string;
  order_id: string;
  screening_type: string;
  status: string;
  risk_score: number;
  findings: Record<string, unknown>;
  created_at: string;
}

export interface AuditReport {
  id: string;
  order_id: string;
  report_data: Record<string, unknown>;
  pdf_path?: string;
  created_at: string;
}

export interface ComplianceSummary {
  order_id: string;
  order_number: string;
  overall_status: string;
  overall_risk_score: number;
  screening_results: ComplianceResult[];
  audit_report?: AuditReport;
  screened_at: string;
}

export interface OrderListResponse {
  total: number;
  orders: Order[];
}

export interface ReportListResponse {
  total: number;
  reports: AuditReport[];
}

export interface ScreeningUpdate {
  order_id: string;
  status: string;
  message: string;
  agent?: string;
  progress?: number;
  overall_risk_score?: number;
  timestamp: string;
}

// ── API calls ──────────────────────────────────────────────────────────────

export const ordersApi = {
  create: (data: OrderCreate) => api.post<Order>('/api/v1/orders', data),
  list: (skip = 0, limit = 50, status?: string) =>
    api.get<OrderListResponse>('/api/v1/orders', { params: { skip, limit, status } }),
  get: (id: string) => api.get<Order>(`/api/v1/orders/${id}`),
  getCompliance: (id: string) => api.get<ComplianceSummary>(`/api/v1/orders/${id}/compliance`),
};

export const reportsApi = {
  list: (skip = 0, limit = 50) =>
    api.get<ReportListResponse>('/api/v1/reports', { params: { skip, limit } }),
  get: (id: string) => api.get<AuditReport>(`/api/v1/reports/${id}`),
  downloadUrl: (id: string) => `${BASE_URL}/api/v1/reports/${id}/download`,
};

export const createWebSocket = (orderId: string, onMessage: (update: ScreeningUpdate) => void): WebSocket => {
  const ws = new WebSocket(`${WS_BASE}/api/v1/orders/ws/${orderId}`);
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)); } catch {}
  };
  return ws;
};

export default api;
