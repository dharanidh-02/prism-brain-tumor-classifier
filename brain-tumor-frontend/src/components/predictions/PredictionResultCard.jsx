import React from 'react';
import {
  Clock,
  Layers,
  Database,
  Printer,
  ShieldAlert,
  CheckCircle2
} from 'lucide-react';

const CLASS_COLORS = {
  glioma: '#e11d48',
  meningioma: '#ea580c',
  notumor: '#059669',
  pituitary: '#7c3aed',
};

const CLASS_LABELS = {
  glioma: 'Glioma',
  meningioma: 'Meningioma',
  notumor: 'No Tumor',
  pituitary: 'Pituitary',
};

export default function PredictionResultCard({ result }) {
  if (!result) return null;

  const predictedClass = result.predicted_class?.toLowerCase();
  const classColor = CLASS_COLORS[predictedClass] || 'var(--prism-indigo)';
  const confidencePct = (result.confidence * 100).toFixed(1);

  const handlePrint = () => {
    window.print();
  };

  const getBadgeClass = (className) => {
    switch (className?.toLowerCase()) {
      case 'glioma': return 'badge-glioma';
      case 'meningioma': return 'badge-meningioma';
      case 'notumor': return 'badge-notumor';
      case 'pituitary': return 'badge-pituitary';
      default: return 'badge-notumor';
    }
  };

  return (
    <div className="white-card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Top Classification Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <span style={{ fontSize: '0.74rem', fontWeight: 600, color: 'var(--prism-slate-light)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>
            Diagnostic Classification
          </span>
          <span
            className={`badge-class ${getBadgeClass(result.predicted_class)}`}
            style={{ fontSize: '1.25rem', padding: '6px 18px', fontWeight: 800 }}
          >
            {result.predicted_class}
          </span>
        </div>

        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '0.74rem', fontWeight: 600, color: 'var(--prism-slate-light)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 2 }}>
            Output Confidence
          </span>
          <span style={{ fontSize: '2.1rem', fontFamily: 'var(--font-display)', fontWeight: 800, color: classColor }}>
            {confidencePct}%
          </span>
        </div>
      </div>

      {/* Meta Pills */}
      <div style={{ display: 'flex', gap: 12, padding: '10px 14px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border-light)', fontSize: '0.8rem', color: 'var(--prism-slate)', flexWrap: 'wrap', marginBottom: 22 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Clock size={15} style={{ color: 'var(--prism-indigo)' }} />
          <span>Latency: <strong>{result.inference_time_ms} ms</strong></span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Layers size={15} style={{ color: 'var(--prism-teal)' }} />
          <span>Model: <strong>{result.model_id}</strong></span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Database size={15} style={{ color: 'var(--prism-emerald)' }} />
          <span>Record: <strong>#{result.prediction_id}</strong></span>
        </div>
      </div>

      {/* 4 Class Probability Distribution */}
      <div style={{ marginBottom: 22 }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--prism-navy)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 12 }}>
          Full Class Probability Distribution
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {Object.entries(result.class_probabilities || {}).map(([cls, prob]) => {
            const isTarget = cls.toLowerCase() === predictedClass;
            const pct = (prob * 100).toFixed(1);
            const color = CLASS_COLORS[cls.toLowerCase()] || '#4f46e5';

            return (
              <div key={cls}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', marginBottom: 4 }}>
                  <span style={{ fontWeight: isTarget ? 700 : 500, color: isTarget ? 'var(--prism-navy)' : 'var(--prism-slate)' }}>
                    {CLASS_LABELS[cls.toLowerCase()] || cls} {isTarget && '★'}
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: isTarget ? color : 'var(--prism-slate)' }}>
                    {pct}%
                  </span>
                </div>
                <div style={{ height: 8, backgroundColor: '#f1f5f9', borderRadius: 4, overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${pct}%`,
                      backgroundColor: color,
                      borderRadius: 4,
                      transition: 'width 0.6s ease',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Print / Report button */}
      <div style={{ marginTop: 'auto', display: 'flex', gap: 10 }}>
        <button
          type="button"
          onClick={handlePrint}
          className="btn-secondary"
          style={{ width: '100%', fontSize: '0.82rem', padding: '8px 14px' }}
        >
          <Printer size={15} />
          <span>Print / Export Clinical Report</span>
        </button>
      </div>

      {/* Regulatory & Research Disclaimer */}
      <div
        style={{
          marginTop: 18,
          padding: '12px 14px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: 'var(--prism-amber-subtle)',
          border: '1px solid var(--prism-amber-border)',
          color: 'var(--prism-amber)',
          fontSize: '0.78rem',
          lineHeight: 1.45,
          display: 'flex',
          gap: 10,
          alignItems: 'flex-start',
        }}
      >
        <ShieldAlert size={18} style={{ flexShrink: 0, marginTop: 1 }} />
        <div>
          <strong>Medical Notice:</strong> PRISM provides experimental AI classification for research and educational purposes. Results are not a medical diagnosis and must not replace professional medical interpretation.
        </div>
      </div>
    </div>
  );
}
