import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import OrderForm from './components/OrderForm';
import AuditLog from './components/AuditLog';

type Tab = 'dashboard' | 'submit' | 'audit';

const NAV_ITEMS: { id: Tab; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'submit', label: 'Submit Order', icon: '📦' },
  { id: 'audit', label: 'Audit Log', icon: '📋' },
];

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  return (
    <div style={{ minHeight: '100vh', background: '#f7fafc' }}>
      {/* Header */}
      <header style={{
        background: '#1a365d', color: '#fff', padding: '0 24px',
        display: 'flex', alignItems: 'center', height: 56, boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      }}>
        <div style={{ fontWeight: 800, fontSize: 18, marginRight: 48, letterSpacing: '-0.5px' }}>
          🛡 Compliance Screening
        </div>
        <nav style={{ display: 'flex', gap: 4 }}>
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                background: activeTab === item.id ? 'rgba(255,255,255,0.15)' : 'transparent',
                color: '#fff', border: 'none', padding: '8px 16px', borderRadius: 6,
                cursor: 'pointer', fontWeight: activeTab === item.id ? 700 : 400,
                fontSize: 14, display: 'flex', alignItems: 'center', gap: 6,
                transition: 'background 0.2s',
              }}
            >
              {item.icon} {item.label}
            </button>
          ))}
        </nav>
        <div style={{ marginLeft: 'auto', fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>
          AI-Driven Compliance System v1.0
        </div>
      </header>

      {/* Content */}
      <main>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'submit' && <OrderForm onOrderCreated={() => setActiveTab('dashboard')} />}
        {activeTab === 'audit' && <AuditLog />}
      </main>
    </div>
  );
};

export default App;
