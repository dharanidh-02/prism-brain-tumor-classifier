import React from 'react';

export default function MetricCard({
  label,
  value,
  sublabel,
  icon: Icon,
  accentColor = 'var(--prism-indigo)',
  loading = false,
}) {
  return (
    <div className="metric-card-white">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="metric-card-lbl">{label}</span>
        {Icon && (
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: '8px',
              backgroundColor: 'var(--prism-surface)',
              border: '1px solid var(--prism-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: accentColor,
            }}
          >
            <Icon size={16} />
          </div>
        )}
      </div>

      {loading ? (
        <div style={{ height: 38, background: 'var(--prism-border-light)', borderRadius: 6, margin: '6px 0', animation: 'pulse 1.5s infinite' }} />
      ) : (
        <div className="metric-card-val" style={{ color: value === null || value === undefined ? 'var(--prism-muted)' : 'var(--prism-navy)' }}>
          {value ?? '—'}
        </div>
      )}

      {sublabel && (
        <div style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
          {sublabel}
        </div>
      )}
    </div>
  );
}
