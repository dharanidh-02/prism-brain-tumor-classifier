import React from 'react';

export function PageHeader({ title, subtitle, badge, action }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28, flexWrap: 'wrap', gap: 16 }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.65rem', fontWeight: 800, color: 'var(--prism-navy)', letterSpacing: '-0.02em' }}>
            {title}
          </h1>
          {badge && (
            <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '3px 10px', borderRadius: 'var(--radius-full)', background: 'var(--prism-indigo-subtle)', color: 'var(--prism-indigo)', border: '1px solid var(--prism-indigo-border)' }}>
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p style={{ color: 'var(--prism-slate-light)', fontSize: '0.9rem', marginTop: 4 }}>
            {subtitle}
          </p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function LoadingSkeleton({ height = 200, count = 1 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          style={{
            height,
            backgroundColor: 'var(--prism-surface-muted)',
            borderRadius: 'var(--radius-md)',
            animation: 'pulse 1.5s infinite',
          }}
        />
      ))}
    </div>
  );
}

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div style={{ padding: '48px 24px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      {Icon && (
        <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--prism-surface-subtle)', border: '1px solid var(--prism-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--prism-muted)', marginBottom: 16 }}>
          <Icon size={26} />
        </div>
      )}
      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 6 }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.86rem', color: 'var(--prism-slate-light)', maxWidth: 420, lineHeight: 1.5, marginBottom: action ? 20 : 0 }}>
        {description}
      </p>
      {action}
    </div>
  );
}

export function ErrorState({ title = 'Error Loading Data', message, onRetry }) {
  return (
    <div style={{ padding: '24px', borderRadius: 'var(--radius-md)', background: 'var(--prism-rose-subtle)', border: '1px solid var(--prism-rose-border)', color: 'var(--prism-rose)', margin: '16px 0' }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: '0.85rem', color: 'var(--prism-navy-soft)', marginBottom: onRetry ? 12 : 0 }}>
        {message}
      </div>
      {onRetry && (
        <button className="btn-secondary" onClick={onRetry} style={{ fontSize: '0.8rem', padding: '6px 14px' }}>
          Try Again
        </button>
      )}
    </div>
  );
}
