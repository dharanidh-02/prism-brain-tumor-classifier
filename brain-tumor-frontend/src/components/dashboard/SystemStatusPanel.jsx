import React from 'react';
import { Link } from 'react-router-dom';
import {
  Server,
  Database,
  Cpu,
  Settings,
  ExternalLink,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import PrismLogo from '../common/PrismLogo';

export default function SystemStatusPanel({ health, loading }) {
  const isHealthy = health?.status === 'healthy';
  const dbConnected = health?.database === 'connected';
  const loadedCount = health?.loaded_models_count ?? 0;
  const totalCount = health?.total_models_count ?? 3;

  return (
    <div className="status-panel">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <PrismLogo size={24} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--prism-navy)' }}>
                PRISM Core
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--prism-slate-light)' }}>
                Diagnostic Engine
              </div>
            </div>
          </div>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.74rem',
              fontWeight: 600,
              backgroundColor: isHealthy ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
              color: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)',
              border: `1px solid ${isHealthy ? 'var(--prism-emerald-border)' : 'var(--prism-rose-border)'}`,
            }}
          >
            <span
              className="pulse-dot"
              style={{ backgroundColor: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)' }}
            />
            {isHealthy ? 'Operational' : 'Attention'}
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '0.82rem' }}>
          {/* API Health */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--prism-slate)' }}>
              <Server size={15} color="var(--prism-indigo)" />
              <span>FastAPI Backend</span>
            </span>
            <strong style={{ color: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)' }}>
              {isHealthy ? 'Connected' : 'Offline'}
            </strong>
          </div>

          {/* Database Status */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--prism-slate)' }}>
              <Database size={15} color="var(--prism-teal)" />
              <span>SQLite Database</span>
            </span>
            <strong style={{ color: dbConnected ? 'var(--prism-emerald)' : 'var(--prism-rose)' }}>
              {dbConnected ? 'Active' : 'Unavailable'}
            </strong>
          </div>

          {/* Available Models */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--prism-slate)' }}>
              <Cpu size={15} color="var(--prism-amber)" />
              <span>Neural Models</span>
            </span>
            <strong style={{ color: loadedCount > 0 ? 'var(--prism-navy)' : 'var(--prism-rose)' }}>
              {loadedCount} / {totalCount} Active
            </strong>
          </div>
        </div>
      </div>

      <div style={{ borderTop: '1px solid var(--prism-border-light)', paddingTop: 14, marginTop: 16 }}>
        <Link
          to="/settings"
          className="btn-secondary"
          style={{ width: '100%', fontSize: '0.82rem', padding: '8px 14px' }}
        >
          <Settings size={15} />
          <span>System Settings & Diagnostics</span>
        </Link>
      </div>
    </div>
  );
}
