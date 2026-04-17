import React, { useEffect, useState, useCallback } from 'react';
import { ordersApi, reportsApi, Order, ComplianceSummary } from '../services/api';

const STATUS_COLORS: Record<string, string> = {
  PASS: '#22543d',
  FLAG: '#7b341e',
  FAIL: '#63171b',
  PENDING: '#2c5282',
  SCREENING: '#4a235a',
  ERROR: '#63171b',
};

const STATUS_BG: Record<string, string> = {
  PASS: '#c6f6d5',
  FLAG: '#feebc8',
  FAIL: '#fed7d7',
  PENDING: '#bee3f8',
  SCREENING: '#e9d8fd',
  ERROR: '#fed7d7',
};

const Badge: React.FC<{ status: string }> = ({ status }) => (
  <span style={{
    background: STATUS_BG[status] || '#e2e8f0',
    color: STATUS_COLORS[status] || '#2d3748',
    padding: '2px 10px',
    borderRadius: 12,
    fontWeight: 700,
    fontSize: 12,
  }}>{status}</span>
);

interface Stats {
  total: number;
  pending: number;
  screening: number;
  flagged: number;
  cleared: number;
  failed: number;
}

const Dashboard: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, pending: 0, screening: 0, flagged: 0, cleared: 0, failed: 0 });
  const [selectedOrder, setSelectedOrder] = useState<string | null>(null);
  const [compliance, setCompliance] = useState<ComplianceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [complianceLoading, setComplianceLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    try {
      const res = await ordersApi.list(0, 100);
      const all = res.data.orders;
      setOrders(all);
      setStats({
        total: res.data.total,
        pending: all.filter(o => o.status === 'PENDING').length,
        screening: all.filter(o => o.status === 'SCREENING').length,
        flagged: all.filter(o => o.status === 'FLAG').length,
        cleared: all.filter(o => o.status === 'PASS').length,
        failed: all.filter(o => o.status === 'FAIL').length,
      });
    } catch {
      setError('Failed to load orders');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, [fetchOrders]);

  const handleSelectOrder = async (id: string) => {
    setSelectedOrder(id);
    setCompliance(null);
    setComplianceLoading(true);
    try {
      const res = await ordersApi.getCompliance(id);
      setCompliance(res.data);
    } catch {
      setCompliance(null);
    } finally {
      setComplianceLoading(false);
    }
  };

  const statCards = [
    { label: 'Total Orders', value: stats.total, color: '#2c5282', bg: '#ebf8ff' },
    { label: 'Pending', value: stats.pending, color: '#2c5282', bg: '#bee3f8' },
    { label: 'Screening', value: stats.screening, color: '#4a235a', bg: '#e9d8fd' },
    { label: 'Flagged', value: stats.flagged, color: '#7b341e', bg: '#feebc8' },
    { label: 'Cleared', value: stats.cleared, color: '#22543d', bg: '#c6f6d5' },
    { label: 'Failed', value: stats.failed, color: '#63171b', bg: '#fed7d7' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ color: '#1a365d', marginBottom: 8 }}>Compliance Screening Dashboard</h1>
      <p style={{ color: '#718096', marginBottom: 24 }}>Real-time order screening against sanctions, AML/KYC, and regulatory requirements</p>

      {/* Stats */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 32 }}>
        {statCards.map(card => (
          <div key={card.label} style={{
            background: card.bg, border: `1px solid ${card.color}22`, borderRadius: 12,
            padding: '16px 24px', minWidth: 130, textAlign: 'center',
          }}>
            <div style={{ fontSize: 32, fontWeight: 800, color: card.color }}>{card.value}</div>
            <div style={{ color: card.color, fontWeight: 600, fontSize: 13 }}>{card.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Orders List */}
        <div>
          <h2 style={{ color: '#2d3748', marginBottom: 12 }}>Recent Orders</h2>
          {loading && <p>Loading orders…</p>}
          {error && <p style={{ color: 'red' }}>{error}</p>}
          {orders.map(order => (
            <div
              key={order.id}
              onClick={() => handleSelectOrder(order.id)}
              style={{
                background: selectedOrder === order.id ? '#ebf8ff' : '#fff',
                border: `1px solid ${selectedOrder === order.id ? '#3182ce' : '#e2e8f0'}`,
                borderRadius: 8, padding: '12px 16px', marginBottom: 8, cursor: 'pointer',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, color: '#2d3748' }}>{order.order_number}</div>
                  <div style={{ fontSize: 13, color: '#718096' }}>{order.customer_name} · {order.customer_country}</div>
                  <div style={{ fontSize: 12, color: '#a0aec0' }}>
                    {order.currency} {Number(order.total_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <Badge status={order.status} />
              </div>
            </div>
          ))}
          {!loading && orders.length === 0 && (
            <p style={{ color: '#a0aec0', textAlign: 'center', padding: 32 }}>No orders yet. Submit one using the form.</p>
          )}
        </div>

        {/* Compliance Detail */}
        <div>
          {selectedOrder && (
            <>
              <h2 style={{ color: '#2d3748', marginBottom: 12 }}>Compliance Details</h2>
              {complianceLoading && <p>Loading compliance results…</p>}
              {!complianceLoading && !compliance && (
                <p style={{ color: '#a0aec0' }}>Screening in progress or no results yet.</p>
              )}
              {compliance && (
                <div>
                  <div style={{
                    background: STATUS_BG[compliance.overall_status] || '#f7fafc',
                    border: `1px solid ${STATUS_COLORS[compliance.overall_status] || '#e2e8f0'}33`,
                    borderRadius: 8, padding: 16, marginBottom: 16,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 18, color: STATUS_COLORS[compliance.overall_status] }}>
                          {compliance.overall_status}
                        </div>
                        <div style={{ color: '#718096', fontSize: 13 }}>Order: {compliance.order_number}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 24, fontWeight: 800, color: STATUS_COLORS[compliance.overall_status] }}>
                          {(compliance.overall_risk_score * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: 12, color: '#718096' }}>Risk Score</div>
                      </div>
                    </div>
                  </div>

                  {compliance.screening_results.map(sr => (
                    <div key={sr.id} style={{
                      background: '#fff', border: '1px solid #e2e8f0',
                      borderRadius: 8, padding: 12, marginBottom: 8,
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, color: '#2d3748' }}>{sr.screening_type}</span>
                        <Badge status={sr.status} />
                      </div>
                      <div style={{ fontSize: 12, color: '#718096' }}>
                        Risk score: {(sr.risk_score * 100).toFixed(1)}%
                      </div>
                      {(sr.findings as any)?.flags?.length > 0 && (
                        <div style={{ marginTop: 6 }}>
                          {((sr.findings as any).flags as string[]).map((f: string, i: number) => (
                            <div key={i} style={{ fontSize: 11, color: '#7b341e', background: '#fffaf0', borderRadius: 4, padding: '2px 6px', marginTop: 2 }}>
                              ⚠ {f}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {compliance.audit_report && compliance.audit_report.pdf_path && (
                    <a
                      href={`http://localhost:8000/api/v1/reports/${compliance.audit_report.id}/download`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-block', marginTop: 8, padding: '8px 16px',
                        background: '#1a365d', color: '#fff', borderRadius: 6,
                        textDecoration: 'none', fontSize: 14, fontWeight: 600,
                      }}
                    >
                      ↓ Download PDF Report
                    </a>
                  )}
                </div>
              )}
            </>
          )}
          {!selectedOrder && (
            <div style={{ textAlign: 'center', color: '#a0aec0', padding: 64 }}>
              Select an order to view compliance details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
