import React from 'react';
import { ComplianceSummary } from '../services/api';
import { reportsApi } from '../services/api';

interface Props {
  summary: ComplianceSummary;
}

const STATUS_COLORS: Record<string, string> = {
  PASS: '#22543d', FLAG: '#7b341e', FAIL: '#63171b',
};
const STATUS_BG: Record<string, string> = {
  PASS: '#c6f6d5', FLAG: '#feebc8', FAIL: '#fed7d7',
};

const RiskBar: React.FC<{ score: number }> = ({ score }) => {
  const pct = Math.round(score * 100);
  const color = score >= 0.8 ? '#e53e3e' : score >= 0.4 ? '#dd6b20' : '#38a169';
  return (
    <div style={{ background: '#e2e8f0', borderRadius: 4, height: 8, width: '100%' }}>
      <div style={{ background: color, width: `${pct}%`, height: '100%', borderRadius: 4, transition: 'width 0.4s' }} />
    </div>
  );
};

const ComplianceReport: React.FC<Props> = ({ summary }) => {
  const { overall_status, overall_risk_score, screening_results, audit_report, order_number } = summary;

  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 24 }}>
      {/* Header */}
      <div style={{
        background: STATUS_BG[overall_status] || '#f7fafc',
        border: `1px solid ${STATUS_COLORS[overall_status] || '#e2e8f0'}44`,
        borderRadius: 10, padding: 16, marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 800, color: STATUS_COLORS[overall_status] }}>{overall_status}</div>
          <div style={{ color: '#718096', fontSize: 14 }}>Order {order_number}</div>
          <div style={{ color: '#a0aec0', fontSize: 12, marginTop: 4 }}>
            Screened: {new Date(summary.screened_at).toLocaleString()}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 36, fontWeight: 900, color: STATUS_COLORS[overall_status] }}>
            {(overall_risk_score * 100).toFixed(0)}%
          </div>
          <div style={{ fontSize: 12, color: '#718096' }}>Overall Risk</div>
          <div style={{ width: 120, marginTop: 4 }}>
            <RiskBar score={overall_risk_score} />
          </div>
        </div>
      </div>

      {/* Screening results */}
      <h3 style={{ color: '#2d3748', marginBottom: 12, fontSize: 15 }}>Screening Results</h3>
      {screening_results.map(sr => {
        const flags: string[] = (sr.findings as any)?.flags || [];
        return (
          <div key={sr.id} style={{
            border: '1px solid #e2e8f0', borderRadius: 8, padding: 14, marginBottom: 10,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <div>
                <span style={{ fontWeight: 700, color: '#2d3748' }}>{sr.screening_type}</span>
                <span style={{ fontSize: 12, color: '#a0aec0', marginLeft: 8 }}>
                  {new Date(sr.created_at).toLocaleTimeString()}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 80 }}><RiskBar score={sr.risk_score} /></div>
                <span style={{ fontSize: 12, color: '#718096' }}>{(sr.risk_score * 100).toFixed(1)}%</span>
                <span style={{
                  background: STATUS_BG[sr.status] || '#e2e8f0',
                  color: STATUS_COLORS[sr.status] || '#2d3748',
                  padding: '2px 10px', borderRadius: 12, fontWeight: 700, fontSize: 12,
                }}>{sr.status}</span>
              </div>
            </div>
            {flags.length > 0 && (
              <div>
                {flags.map((f, i) => (
                  <div key={i} style={{
                    background: '#fffaf0', border: '1px solid #feebc8', borderRadius: 6,
                    padding: '4px 10px', marginTop: 4, fontSize: 12, color: '#7b341e',
                  }}>
                    ⚠ {f}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* PDF Download */}
      {audit_report && (
        <div style={{ marginTop: 16 }}>
          {audit_report.pdf_path && (
            <a
              href={reportsApi.downloadUrl(audit_report.id)}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: '#1a365d', color: '#fff', padding: '10px 20px',
                borderRadius: 8, textDecoration: 'none', fontWeight: 700, fontSize: 14,
              }}
            >
              ↓ Download Audit PDF Report
            </a>
          )}
        </div>
      )}
    </div>
  );
};

export default ComplianceReport;
