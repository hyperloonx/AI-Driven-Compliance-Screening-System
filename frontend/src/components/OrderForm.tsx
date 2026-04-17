import React, { useState } from 'react';
import { ordersApi, OrderCreate, OrderItem } from '../services/api';

const emptyItem = (): OrderItem => ({
  product_id: `PRD-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
  product_name: '',
  quantity: 1,
  unit_price: 0,
  category: '',
  hs_code: '',
});

const CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD'];

interface Props {
  onOrderCreated?: () => void;
}

const OrderForm: React.FC<Props> = ({ onOrderCreated }) => {
  const [form, setForm] = useState<OrderCreate>({
    customer_name: '',
    customer_country: '',
    customer_email: '',
    items: [emptyItem()],
    total_amount: 0,
    currency: 'USD',
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const updateField = (field: keyof OrderCreate, value: unknown) => {
    setForm(f => ({ ...f, [field]: value }));
  };

  const updateItem = (idx: number, field: keyof OrderItem, value: unknown) => {
    const items = [...form.items];
    items[idx] = { ...items[idx], [field]: value };
    // Recalculate total
    const total = items.reduce((sum, it) => sum + (Number(it.quantity) * Number(it.unit_price)), 0);
    setForm(f => ({ ...f, items, total_amount: Math.round(total * 100) / 100 }));
  };

  const addItem = () => setForm(f => ({ ...f, items: [...f.items, emptyItem()] }));
  const removeItem = (idx: number) => setForm(f => ({ ...f, items: f.items.filter((_, i) => i !== idx) }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await ordersApi.create(form);
      setSuccess(`Order ${res.data.order_number} submitted for screening!`);
      setForm({
        customer_name: '', customer_country: '', customer_email: '',
        items: [emptyItem()], total_amount: 0, currency: 'USD',
      });
      onOrderCreated?.();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to submit order');
    } finally {
      setSubmitting(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0',
    borderRadius: 6, fontSize: 14, outline: 'none', marginTop: 4,
  };
  const labelStyle: React.CSSProperties = { fontSize: 13, fontWeight: 600, color: '#4a5568', display: 'block' };

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: 24 }}>
      <h2 style={{ color: '#1a365d', marginBottom: 8 }}>Submit Order for Screening</h2>
      <p style={{ color: '#718096', marginBottom: 24, fontSize: 14 }}>
        All orders are automatically screened against sanctions, AML/KYC, and regulatory requirements.
      </p>

      <form onSubmit={handleSubmit}>
        {/* Customer section */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginBottom: 16 }}>
          <h3 style={{ color: '#2d3748', marginBottom: 16, fontSize: 15 }}>Customer Information</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={labelStyle}>Full Name *</label>
              <input style={inputStyle} required value={form.customer_name}
                onChange={e => updateField('customer_name', e.target.value)} placeholder="e.g. John Smith" />
            </div>
            <div>
              <label style={labelStyle}>Country *</label>
              <input style={inputStyle} required value={form.customer_country}
                onChange={e => updateField('customer_country', e.target.value)} placeholder="e.g. United States" />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Email Address *</label>
              <input style={inputStyle} required type="email" value={form.customer_email}
                onChange={e => updateField('customer_email', e.target.value)} placeholder="e.g. john@example.com" />
            </div>
          </div>
        </div>

        {/* Items section */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ color: '#2d3748', fontSize: 15 }}>Order Items</h3>
            <button type="button" onClick={addItem} style={{
              background: '#ebf8ff', color: '#2c5282', border: 'none', borderRadius: 6,
              padding: '6px 14px', cursor: 'pointer', fontWeight: 600, fontSize: 13,
            }}>+ Add Item</button>
          </div>

          {form.items.map((item, idx) => (
            <div key={item.product_id} style={{
              background: '#f7fafc', borderRadius: 8, padding: 12, marginBottom: 12,
              border: '1px solid #e2e8f0',
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 12, marginBottom: 8 }}>
                <div>
                  <label style={labelStyle}>Product Name *</label>
                  <input style={inputStyle} required value={item.product_name}
                    onChange={e => updateItem(idx, 'product_name', e.target.value)} placeholder="Product name" />
                </div>
                <div>
                  <label style={labelStyle}>Quantity *</label>
                  <input style={inputStyle} required type="number" min={1} value={item.quantity}
                    onChange={e => updateItem(idx, 'quantity', parseInt(e.target.value) || 1)} />
                </div>
                <div>
                  <label style={labelStyle}>Unit Price *</label>
                  <input style={inputStyle} required type="number" min={0} step="0.01" value={item.unit_price}
                    onChange={e => updateItem(idx, 'unit_price', parseFloat(e.target.value) || 0)} />
                </div>
                <div>
                  <label style={labelStyle}>Category</label>
                  <input style={inputStyle} value={item.category || ''}
                    onChange={e => updateItem(idx, 'category', e.target.value)} placeholder="e.g. ELECTRONICS" />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <label style={labelStyle}>HS Code (optional)</label>
                  <input style={inputStyle} value={item.hs_code || ''}
                    onChange={e => updateItem(idx, 'hs_code', e.target.value)} placeholder="e.g. 8542" />
                </div>
                {form.items.length > 1 && (
                  <button type="button" onClick={() => removeItem(idx)} style={{
                    background: '#fed7d7', color: '#63171b', border: 'none', borderRadius: 6,
                    padding: '6px 12px', cursor: 'pointer', marginTop: 20, fontWeight: 600,
                  }}>Remove</button>
                )}
              </div>
            </div>
          ))}

          {/* Total */}
          <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', justifyContent: 'flex-end' }}>
            <div>
              <label style={labelStyle}>Currency</label>
              <select style={{ ...inputStyle, width: 'auto' }} value={form.currency}
                onChange={e => updateField('currency', e.target.value)}>
                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 13, color: '#718096', fontWeight: 600 }}>Total Amount</div>
              <div style={{ fontSize: 24, fontWeight: 800, color: '#1a365d' }}>
                {form.currency} {form.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        </div>

        {success && (
          <div style={{ background: '#c6f6d5', color: '#22543d', padding: 12, borderRadius: 8, marginBottom: 12, fontWeight: 600 }}>
            ✓ {success}
          </div>
        )}
        {error && (
          <div style={{ background: '#fed7d7', color: '#63171b', padding: 12, borderRadius: 8, marginBottom: 12, fontWeight: 600 }}>
            ✗ {error}
          </div>
        )}

        <button type="submit" disabled={submitting} style={{
          background: submitting ? '#a0aec0' : '#1a365d', color: '#fff', border: 'none',
          borderRadius: 8, padding: '12px 32px', fontSize: 16, fontWeight: 700,
          cursor: submitting ? 'not-allowed' : 'pointer', width: '100%',
        }}>
          {submitting ? 'Submitting…' : 'Submit Order for Compliance Screening'}
        </button>
      </form>
    </div>
  );
};

export default OrderForm;
