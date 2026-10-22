import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Menu, ShieldCheck, Settings, Activity } from 'lucide-react';
import { healthService } from '../../services/healthService';

export default function TopBar({ onToggleSidebar }) {
  const location = useLocation();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    healthService.getHealth().then(setHealth).catch(() => setHealth({ status: 'unhealthy' }));
  }, []);

  // Format pathname into friendly breadcrumb
  const path = location.pathname;
  let pageName = 'Overview';
  if (path === '/analyze') pageName = 'Analyze MRI Scan';
  else if (path === '/history') pageName = 'Prediction History & Audit';
  else if (path === '/analytics') pageName = 'Analytics & Model Reports';
  else if (path === '/models') pageName = 'Model Laboratory';
  else if (path === '/model-comparison') pageName = 'Multi-Model Comparison';
  else if (path === '/explainability') pageName = 'Explainable AI Visualization';
  else if (path === '/dataset') pageName = 'Dataset Explorer';
  else if (path === '/settings') pageName = 'System Settings & Diagnostics';

  const isHealthy = health?.status === 'healthy';

  return (
    <header className="prism-topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button
          onClick={onToggleSidebar}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--prism-slate)',
            cursor: 'pointer',
            padding: 6,
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
          }}
          title="Toggle Navigation Menu"
        >
          <Menu size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.88rem' }}>
          <span style={{ color: 'var(--prism-muted)' }}>Workspace</span>
          <span style={{ color: 'var(--prism-border)' }}>/</span>
          <span style={{ fontWeight: 600, color: 'var(--prism-navy)' }}>{pageName}</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Health Indicator Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '5px 14px',
            borderRadius: 'var(--radius-full)',
            background: isHealthy ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
            border: `1px solid ${isHealthy ? 'var(--prism-emerald-border)' : 'var(--prism-rose-border)'}`,
            fontSize: '0.78rem',
            fontWeight: 600,
            color: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)',
          }}
        >
          <span className="pulse-dot" style={{ backgroundColor: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)' }} />
          <span>{isHealthy ? 'Models Operational (3/3)' : 'Engine Offline'}</span>
        </div>

        {/* Quick Settings Action */}
        <Link
          to="/settings"
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            backgroundColor: 'var(--prism-surface-muted)',
            border: '1px solid var(--prism-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--prism-slate)',
            textDecoration: 'none',
            transition: 'all 0.15s ease',
          }}
          title="Settings"
        >
          <Settings size={18} />
        </Link>
      </div>
    </header>
  );
}
