import React, { useEffect, useState } from 'react';
import { reportsApi, AuditReport } from '../services/api';

const AuditLog: React.FC = () => {
  const [reports, setReports] = useState<AuditReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<AuditReport | null>(null);

  useEffect(() => {
    reportsApi.list().then(res => {
      setReports(res.data.reports);
    }).finally(() => setLoading(false));
  }, []);

  const STATUS_COLORS: Record<string, string> = { PASS: '#22543d', FLAG: '#7b341e', FAIL: '#63171b' };
  const STATUS_BG: Record<string, string> = { PASS: '#c6f6d5', FLAG: '#feebc8', FAIL: '#fed7d7' };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: '#1a365d', marginBottom: 8 }}>Audit Log</h2>
      <p style={{ color: '#718096', marginBottom: 16, fontSize: 14 }}>
        Complete audit trail of all compliance screenings
      </p>

      {loading && <p>Loading audit reports…</p>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 24 }}>
        <div>
          {reports.map(report => {
            const rd = report.report_data as any;
            const status = rd?.compliance_summary?.overall_status || 'UNKNOWN';
            const orderNum = rd?.order?.order_number || report.order_id.slice(0, 8);
            return (
              <div
                key={report.id}
                onClick={() => setSelected(report)}
                style={{
                  background: selected?.id === report.id ? '#ebf8ff' : '#fff',
                  border: `1px solid ${selected?.id === report.id ? '#3182ce' : '#e2e8f0'}`,
                  borderRadius: 8, padding: '12px 16px', marginBottom: 8, cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700, color: '#2d3748' }}>{orderNum}</div>
                    <div style={{ fontSize: 12, color: '#a0aec0' }}>
                      {new Date(report.created_at).toLocaleString()}
                    </div>
                  </div>
                  <span style={{
                    background: STATUS_BG[status] || '#e2e8f0',
                    color: STATUS_COLORS[status] || '#2d3748',
                    padding: '2px 10px', borderRadius: 12, fontWeight: 700, fontSize: 12,
                  }}>{status}</span>
                </div>
              </div>
            );
          })}
          {!loading && reports.length === 0 && (
            <p style={{ color: '#a0aec0', textAlign: 'center', padding: 32 }}>No audit reports yet.</p>
          )}
        </div>

        {selected && (
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20 }}>
            <h3 style={{ color: '#2d3748', marginBottom: 12 }}>Report Details</h3>
            <pre style={{
              background: '#f7fafc', borderRadius: 8, padding: 12,
              fontSize: 11, overflow: 'auto', maxHeight: 400,
              color: '#2d3748', whiteSpace: 'pre-wrap', wordBreak: 'break-word',
            }}>
              {JSON.stringify(selected.report_data, null, 2)}
            </pre>
            {selected.pdf_path && (
              <a
                href={reportsApi.downloadUrl(selected.id)}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-block', marginTop: 12,
                  background: '#1a365d', color: '#fff', padding: '8px 16px',
                  borderRadius: 6, textDecoration: 'none', fontWeight: 600, fontSize: 14,
                }}
              >
                ↓ Download PDF
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLog;
