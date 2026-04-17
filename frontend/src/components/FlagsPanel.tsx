import React from 'react';
import { ComplianceSummary } from '../services/api';

interface Props {
  summaries: ComplianceSummary[];
}

const SEVERITY_ORDER = ['FAIL', 'FLAG', 'PASS'];

const FlagsPanel: React.FC<Props> = ({ summaries }) => {
  interface FlagEntry {
    order_number: string;
    order_id: string;
    flag: string;
    screening_type: string;
    status: string;
    risk_score: number;
  }

  const allFlags: FlagEntry[] = [];
  for (const s of summaries) {
    for (const sr of s.screening_results) {
      const flags: string[] = (sr.findings as any)?.flags || [];
      for (const f of flags) {
        allFlags.push({
          order_number: s.order_number,
          order_id: s.order_id,
          flag: f,
          screening_type: sr.screening_type,
          status: sr.status,
          risk_score: sr.risk_score,
        });
      }
    }
  }

  allFlags.sort((a, b) => {
    const ai = SEVERITY_ORDER.indexOf(a.status);
    const bi = SEVERITY_ORDER.indexOf(b.status);
    return ai - bi || b.risk_score - a.risk_score;
  });

  if (allFlags.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#a0aec0', padding: 48 }}>
        <div style={{ fontSize: 48, marginBottom: 8 }}>✓</div>
        <div style={{ fontWeight: 600 }}>No compliance flags found</div>
      </div>
    );
  }

  const colorMap: Record<string, string> = { FAIL: '#63171b', FLAG: '#7b341e', PASS: '#22543d' };
  const bgMap: Record<string, string> = { FAIL: '#fed7d7', FLAG: '#feebc8', PASS: '#c6f6d5' };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ color: '#1a365d', marginBottom: 8 }}>Compliance Violations & Flags</h2>
      <p style={{ color: '#718096', marginBottom: 16, fontSize: 14 }}>{allFlags.length} flag(s) detected</p>

      {allFlags.map((entry, i) => (
        <div key={i} style={{
          background: bgMap[entry.status] || '#f7fafc',
          border: `1px solid ${colorMap[entry.status] || '#e2e8f0'}44`,
          borderRadius: 8, padding: 14, marginBottom: 8,
          borderLeft: `4px solid ${colorMap[entry.status] || '#e2e8f0'}`,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: colorMap[entry.status], marginBottom: 2 }}>
                ⚠ {entry.flag}
              </div>
              <div style={{ fontSize: 12, color: '#718096' }}>
                Order: <strong>{entry.order_number}</strong> · Agent: {entry.screening_type} · Risk: {(entry.risk_score * 100).toFixed(1)}%
              </div>
            </div>
            <span style={{
              background: bgMap[entry.status],
              color: colorMap[entry.status],
              padding: '2px 10px', borderRadius: 12, fontWeight: 700, fontSize: 12,
              flexShrink: 0, marginLeft: 12,
            }}>{entry.status}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FlagsPanel;
