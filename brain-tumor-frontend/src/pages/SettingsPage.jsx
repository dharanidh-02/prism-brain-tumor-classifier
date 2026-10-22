import React, { useState, useEffect } from 'react';
import {
  Settings2,
  Server,
  Database,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Info,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { PageHeader } from '../components/common/CommonComponents';
import PrismLogo from '../components/common/PrismLogo';
import { API_BASE_URL } from '../services/apiClient';
import { healthService } from '../services/healthService';

export default function SettingsPage() {
  const [health, setHealth] = useState(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [latencyMs, setLatencyMs] = useState(null);
  const [testStatus, setTestStatus] = useState(null);

  const runConnectionTest = async () => {
    setTestingConnection(true);
    setTestStatus(null);
    const start = performance.now();
    try {
      const data = await healthService.getHealth();
      const duration = Math.round(performance.now() - start);
      setLatencyMs(duration);
      setHealth(data);
      setTestStatus('success');
    } catch (err) {
      setTestStatus('error');
    } finally {
      setTestingConnection(false);
    }
  };

  useEffect(() => {
    runConnectionTest();
  }, []);

  return (
    <div>
      <PageHeader
        title="Settings & System Diagnostics"
        subtitle="Manage backend API connections, inspect SQLite database state, and review architecture specifications."
        badge="Platform Diagnostics"
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, marginBottom: 28 }}>
        {/* Backend Diagnostics */}
        <div className="white-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <Server size={20} style={{ color: 'var(--prism-indigo)' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              Backend Connection & Endpoints
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: '0.86rem', marginBottom: 20 }}>
            <div>
              <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.76rem', textTransform: 'uppercase', marginBottom: 3 }}>
                Configured Base URL
              </span>
              <code style={{ fontFamily: 'var(--font-mono)', background: 'var(--prism-surface-subtle)', padding: '4px 10px', borderRadius: 4, display: 'inline-block', color: 'var(--prism-navy)' }}>
                {API_BASE_URL}
              </code>
            </div>

            <div>
              <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.76rem', textTransform: 'uppercase', marginBottom: 3 }}>
                System Readiness Status
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '3px 10px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    backgroundColor: health?.status === 'healthy' ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
                    color: health?.status === 'healthy' ? 'var(--prism-emerald)' : 'var(--prism-rose)',
                    border: `1px solid ${health?.status === 'healthy' ? 'var(--prism-emerald-border)' : 'var(--prism-rose-border)'}`,
                  }}
                >
                  <span className="pulse-dot" style={{ backgroundColor: health?.status === 'healthy' ? 'var(--prism-emerald)' : 'var(--prism-rose)' }} />
                  <span>{health?.status === 'healthy' ? 'Connected & Operational' : 'Offline / Degraded'}</span>
                </span>
                {latencyMs !== null && (
                  <span style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
                    (Ping: {latencyMs} ms)
                  </span>
                )}
              </div>
            </div>

            <div>
              <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.76rem', textTransform: 'uppercase', marginBottom: 3 }}>
                Database Storage
              </span>
              <span style={{ fontWeight: 600, color: 'var(--prism-navy)' }}>
                SQLite (data/PRISM.db) — {health?.database === 'connected' ? 'Active' : 'Unreachable'}
              </span>
            </div>
          </div>

          <button
            onClick={runConnectionTest}
            className="btn-secondary"
            disabled={testingConnection}
            style={{ width: '100%', fontSize: '0.85rem' }}
          >
            <RefreshCw size={15} className={testingConnection ? 'spin' : ''} style={{ animation: testingConnection ? 'spin 1s linear infinite' : 'none' }} />
            <span>{testingConnection ? 'Testing Connection...' : 'Run Connectivity Diagnostic'}</span>
          </button>
        </div>

        {/* Neural Engine Diagnostic */}
        <div className="white-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <Cpu size={20} style={{ color: 'var(--prism-teal)' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              Registered Keras 3 Engines
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {health?.models ? (
              Object.entries(health.models).map(([mid, stat]) => (
                <div
                  key={mid}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--prism-surface-subtle)',
                    border: '1px solid var(--prism-border-light)',
                    fontSize: '0.84rem',
                  }}
                >
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--prism-navy)' }}>
                    {mid}
                  </span>
                  <span
                    style={{
                      fontSize: '0.74rem',
                      fontWeight: 600,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: stat === 'loaded' ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
                      color: stat === 'loaded' ? 'var(--prism-emerald)' : 'var(--prism-rose)',
                    }}
                  >
                    {stat.toUpperCase()}
                  </span>
                </div>
              ))
            ) : (
              <div style={{ color: 'var(--prism-muted)', fontSize: '0.85rem' }}>
                No active model response received.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* About PRISM Specification Card */}
      <div className="white-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
          <PrismLogo size={28} />
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              About PRISM
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
              Version 1.0.0 • Clinical Research Platform
            </span>
          </div>
        </div>

        <div style={{ padding: '14px 18px', background: 'var(--prism-indigo-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-indigo-border)', marginBottom: 16 }}>
          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--prism-indigo)', marginBottom: 4 }}>
            Expanded Project Title:
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--prism-navy)', lineHeight: 1.5 }}>
            Precision Radiology Imaging for Solid Masses: A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors.
          </p>
        </div>

        <div style={{ fontSize: '0.86rem', color: 'var(--prism-slate)', lineHeight: 1.6, display: 'flex', flexDirection: 'column', gap: 10 }}>
          <p>
            PRISM integrates dual transfer-learning backbones (EfficientNetB0 and MobileNetV3Large) combined through a cross-feature attention gating mechanism to extract both high-resolution localized edge textures and broad anatomical spatial contexts.
          </p>
          <p>
            The software was designed to provide reproducible, zero-hallucination deep learning classifications across 4 distinct cranial tissue categories: <strong>Glioma</strong>, <strong>Meningioma</strong>, <strong>No Tumor</strong>, and <strong>Pituitary</strong>.
          </p>
        </div>
      </div>
    </div>
  );
}
