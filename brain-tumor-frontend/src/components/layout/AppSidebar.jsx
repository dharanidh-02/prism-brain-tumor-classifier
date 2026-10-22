import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  History,
  BarChart3,
  BrainCircuit,
  GitCompareArrows,
  ScanEye,
  Database,
  Settings2,
  ChevronLeft,
  ChevronRight,
  Activity
} from 'lucide-react';
import PrismLogo from '../common/PrismLogo';
import { healthService } from '../../services/healthService';

const NAV_ITEMS = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Analyze MRI', path: '/analyze', icon: ScanLine },
  { label: 'Prediction History', path: '/history', icon: History },
  { label: 'Analytics & Reports', path: '/analytics', icon: BarChart3 },
  { label: 'Model Laboratory', path: '/models', icon: BrainCircuit },
  { label: 'Model Comparison', path: '/model-comparison', icon: GitCompareArrows },
  { label: 'Explainable AI', path: '/explainability', icon: ScanEye },
  { label: 'Dataset Explorer', path: '/dataset', icon: Database },
  { label: 'Settings', path: '/settings', icon: Settings2 },
];

export default function AppSidebar({ collapsed, onToggle }) {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let mounted = true;
    const checkHealth = async () => {
      try {
        const data = await healthService.getHealth();
        if (mounted) setHealth(data);
      } catch (err) {
        if (mounted) setHealth({ status: 'unhealthy' });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // 30s polling
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const isHealthy = health?.status === 'healthy';

  return (
    <aside className={`prism-sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Brand Header */}
      <div className="sidebar-brand">
        <PrismLogo size={collapsed ? 28 : 34} />
        {!collapsed && (
          <div style={{ overflow: 'hidden' }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--prism-navy)', letterSpacing: '-0.02em' }}>
              PRISM
            </div>
            <div style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--prism-slate-light)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Clinical Intelligence
            </div>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav" aria-label="Main Navigation">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-link-item ${isActive ? 'active' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <Icon size={19} className="nav-icon" style={{ flexShrink: 0 }} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Sidebar Footer with Live API Status */}
      <div className="sidebar-footer">
        {!collapsed ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--prism-slate-light)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Engine Status
              </span>
              <button
                onClick={onToggle}
                style={{ background: 'none', border: 'none', color: 'var(--prism-muted)', cursor: 'pointer', padding: 2 }}
                title="Collapse Sidebar"
              >
                <ChevronLeft size={16} />
              </button>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '7px 12px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isHealthy ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
                border: `1px solid ${isHealthy ? 'var(--prism-emerald-border)' : 'var(--prism-rose-border)'}`,
                fontSize: '0.78rem',
                fontWeight: 600,
                color: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)',
              }}
            >
              <span
                className="pulse-dot"
                style={{ backgroundColor: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)' }}
              />
              <span>{isHealthy ? `Connected (${health.loaded_models_count}/${health.total_models_count} Ready)` : 'Engine Disconnected'}</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--prism-muted)', marginTop: 8, textAlign: 'center' }}>
              PRISM v1.0.0 • Local Host
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
            <span
              className="pulse-dot"
              style={{ backgroundColor: isHealthy ? 'var(--prism-emerald)' : 'var(--prism-rose)' }}
              title={isHealthy ? 'Backend Operational' : 'Backend Disconnected'}
            />
            <button
              onClick={onToggle}
              style={{ background: 'none', border: 'none', color: 'var(--prism-muted)', cursor: 'pointer' }}
              title="Expand Sidebar"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
