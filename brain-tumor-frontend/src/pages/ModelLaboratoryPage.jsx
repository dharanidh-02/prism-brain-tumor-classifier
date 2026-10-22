import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BrainCircuit,
  Layers,
  Cpu,
  ShieldCheck,
  ArrowRight,
  RefreshCw,
  Fingerprint,
  Binary
} from 'lucide-react';
import { PageHeader, LoadingSkeleton } from '../components/common/CommonComponents';
import { modelService } from '../services/modelService';

export default function ModelLaboratoryPage() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const data = await modelService.getModels();
      // Fetch full details for each model
      const detailed = await Promise.all(
        data.map(async (m) => {
          try {
            return await modelService.getModelDetail(m.model_id);
          } catch {
            return m;
          }
        })
      );
      setModels(detailed);
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  return (
    <div>
      <PageHeader
        title="Model Laboratory"
        subtitle="Inspection workspace for registered Keras 3 neural models, layer graphs, parameter allocations, and fingerprints."
        badge="Architecture Registry"
        action={
          <button onClick={fetchModels} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
            <RefreshCw size={14} />
            <span>Refresh Registry</span>
          </button>
        }
      />

      {loading ? (
        <LoadingSkeleton height={180} count={3} />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {models.map((m) => {
            const isLoaded = m.status === 'loaded';
            return (
              <div key={m.model_id} className="white-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 14, marginBottom: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div
                      style={{
                        width: 48,
                        height: 48,
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: isLoaded ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
                        color: isLoaded ? 'var(--prism-emerald)' : 'var(--prism-rose)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <BrainCircuit size={26} />
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--prism-navy)', marginBottom: 2 }}>
                        {m.display_name}
                      </h3>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--prism-indigo)', fontWeight: 600 }}>
                          {m.model_id}
                        </span>
                        <span style={{ color: 'var(--prism-border)' }}>•</span>
                        <span style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
                          {m.phase || 'Dual-Backbone Artifact'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        padding: '4px 12px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        backgroundColor: isLoaded ? 'var(--prism-emerald-subtle)' : 'var(--prism-rose-subtle)',
                        color: isLoaded ? 'var(--prism-emerald)' : 'var(--prism-rose)',
                        border: `1px solid ${isLoaded ? 'var(--prism-emerald-border)' : 'var(--prism-rose-border)'}`,
                      }}
                    >
                      <span className="pulse-dot" style={{ backgroundColor: isLoaded ? 'var(--prism-emerald)' : 'var(--prism-rose)' }} />
                      <span>{isLoaded ? 'Operational / Ready' : m.status}</span>
                    </span>

                    <Link
                      to={`/analyze?model=${m.model_id}`}
                      className="btn-primary"
                      style={{ fontSize: '0.82rem', padding: '8px 16px' }}
                    >
                      <span>Analyze with Model</span>
                      <ArrowRight size={14} />
                    </Link>
                  </div>
                </div>

                <p style={{ color: 'var(--prism-slate)', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: 20 }}>
                  {m.description}
                </p>

                {/* Technical Specifications Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, padding: 16, background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border-light)', fontSize: '0.82rem', marginBottom: 16 }}>
                  <div>
                    <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.74rem', textTransform: 'uppercase', marginBottom: 3 }}>
                      Total Parameters
                    </span>
                    <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '1rem', color: 'var(--prism-navy)' }}>
                      {m.parameter_count?.toLocaleString() || '7,851,431'}
                    </strong>
                  </div>

                  <div>
                    <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.74rem', textTransform: 'uppercase', marginBottom: 3 }}>
                      Input Dimensions
                    </span>
                    <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '0.92rem', color: 'var(--prism-navy)' }}>
                      [None, 224, 224, 3] (RGB)
                    </strong>
                  </div>

                  <div>
                    <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.74rem', textTransform: 'uppercase', marginBottom: 3 }}>
                      Output Classes
                    </span>
                    <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '0.92rem', color: 'var(--prism-navy)' }}>
                      [None, 4] (Softmax)
                    </strong>
                  </div>

                  <div>
                    <span style={{ color: 'var(--prism-slate-light)', display: 'block', fontSize: '0.74rem', textTransform: 'uppercase', marginBottom: 3 }}>
                      Load Latency
                    </span>
                    <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '0.92rem', color: 'var(--prism-navy)' }}>
                      {m.load_duration_ms ? `${m.load_duration_ms} ms` : 'Eager Loaded'}
                    </strong>
                  </div>
                </div>

                {/* Fingerprint & Integrity */}
                {m.model_sha256 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.76rem', color: 'var(--prism-slate-light)' }}>
                    <Fingerprint size={15} style={{ color: 'var(--prism-indigo)' }} />
                    <span>SHA-256 Checksum:</span>
                    <code style={{ fontFamily: 'var(--font-mono)', background: 'var(--prism-surface-subtle)', padding: '2px 6px', borderRadius: 4, color: 'var(--prism-navy-soft)' }}>
                      {m.model_sha256}
                    </code>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
