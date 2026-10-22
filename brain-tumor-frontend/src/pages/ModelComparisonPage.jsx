import React, { useState, useEffect } from 'react';
import {
  GitCompareArrows,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldAlert
} from 'lucide-react';
import { PageHeader } from '../components/common/CommonComponents';
import UploadDropzone from '../components/predictions/UploadDropzone';
import { modelService } from '../services/modelService';
import { predictionService } from '../services/predictionService';

const CLASS_COLORS = {
  glioma: '#e11d48',
  meningioma: '#ea580c',
  notumor: '#059669',
  pituitary: '#7c3aed',
};

export default function ModelComparisonPage() {
  const [models, setModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState(['hybrid_v1', 'hybrid_v1_final', 'hybrid_v2_finetuned']);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [error, setError] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);

  useEffect(() => {
    modelService.getModels().then((data) => {
      setModels(data);
    }).catch(console.warn);
  }, []);

  const handleFileSelect = (f) => {
    if (!['image/jpeg', 'image/png'].includes(f.type)) {
      setError('Please upload a valid JPEG or PNG MRI image.');
      return;
    }
    setError(null);
    setFile(f);
    setComparisonResult(null);
    const r = new FileReader();
    r.onload = (e) => setPreviewUrl(e.target.result);
    r.readAsDataURL(f);
  };

  const handleToggleModel = (mid) => {
    if (selectedModels.includes(mid)) {
      if (selectedModels.length === 1) return; // Keep at least one
      setSelectedModels(selectedModels.filter((m) => m !== mid));
    } else {
      setSelectedModels([...selectedModels, mid]);
    }
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please upload an MRI image to evaluate.');
      return;
    }
    if (selectedModels.length < 2) {
      setError('Select at least two models to perform a comparative analysis.');
      return;
    }
    setIsComparing(true);
    setError(null);

    try {
      const data = await predictionService.compareMRI(file, selectedModels);
      setComparisonResult(data);
    } catch (err) {
      setError(err.message || 'Comparison failed. Verify backend service.');
    } finally {
      setIsComparing(false);
    }
  };

  // Determine agreement across successful model outputs
  const successfulPredictions = comparisonResult?.results?.filter((r) => r.status === 'completed') || [];
  const distinctClasses = [...new Set(successfulPredictions.map((r) => r.predicted_class))];
  const hasConsensus = distinctClasses.length === 1 && successfulPredictions.length > 1;

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
    <div>
      <PageHeader
        title="Multi-Model Comparative Analysis"
        subtitle="Simultaneously evaluate an MRI scan across multiple trained architectures to cross-examine class distributions."
        badge="Cross-Validation"
      />

      {/* Control Setup Card */}
      <div className="white-card" style={{ marginBottom: 28 }}>
        <form onSubmit={handleCompare}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 28, alignItems: 'start' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                1. Select Brain MRI Scan
              </label>
              <UploadDropzone
                file={file}
                previewUrl={previewUrl}
                onFileSelect={handleFileSelect}
                onClear={() => { setFile(null); setPreviewUrl(null); setComparisonResult(null); }}
                error={error}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                2. Select Models for Comparison (Min 2)
              </label>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 24 }}>
                {['hybrid_v1', 'hybrid_v1_final', 'hybrid_v2_finetuned'].map((mid) => {
                  const isChecked = selectedModels.includes(mid);
                  return (
                    <label
                      key={mid}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12,
                        padding: '12px 16px',
                        borderRadius: 'var(--radius-sm)',
                        border: `1px solid ${isChecked ? 'var(--prism-indigo-border)' : 'var(--prism-border)'}`,
                        backgroundColor: isChecked ? 'var(--prism-indigo-subtle)' : 'var(--prism-surface)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleToggleModel(mid)}
                        style={{ width: 16, height: 16, accentColor: 'var(--prism-indigo)' }}
                      />
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.88rem', color: isChecked ? 'var(--prism-indigo)' : 'var(--prism-navy)' }}>
                          {mid === 'hybrid_v1' && 'Hybrid EfficientNetB0 + MobileNetV3 (Attention)'}
                          {mid === 'hybrid_v1_final' && 'Hybrid EfficientNetB0 + MobileNetV3 (Final Attention)'}
                          {mid === 'hybrid_v2_finetuned' && 'Hybrid Fine-tuned (Phase 2 Checkpoint)'}
                        </div>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.74rem', color: 'var(--prism-slate-light)' }}>
                          {mid}
                        </span>
                      </div>
                    </label>
                  );
                })}
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={isComparing || !file || selectedModels.length < 2}
                style={{ width: '100%', padding: '12px 20px' }}
              >
                {isComparing ? (
                  <>
                    <RefreshCw size={17} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                    <span>Executing Parallel Inference...</span>
                  </>
                ) : (
                  <>
                    <GitCompareArrows size={17} />
                    <span>Compare Selected Models ({selectedModels.length})</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Comparison Results */}
      {comparisonResult && (
        <div>
          {/* Agreement Status Banner */}
          <div
            style={{
              padding: '16px 20px',
              borderRadius: 'var(--radius-md)',
              marginBottom: 24,
              display: 'flex',
              alignItems: 'center',
              gap: 14,
              backgroundColor: hasConsensus ? 'var(--prism-emerald-subtle)' : 'var(--prism-amber-subtle)',
              border: `1px solid ${hasConsensus ? 'var(--prism-emerald-border)' : 'var(--prism-amber-border)'}`,
            }}
          >
            {hasConsensus ? (
              <CheckCircle2 size={24} style={{ color: 'var(--prism-emerald)', flexShrink: 0 }} />
            ) : (
              <AlertTriangle size={24} style={{ color: 'var(--prism-amber)', flexShrink: 0 }} />
            )}
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.98rem', color: hasConsensus ? 'var(--prism-emerald)' : 'var(--prism-amber)' }}>
                {hasConsensus
                  ? `Consensus Classification: All ${successfulPredictions.length} models agree on ${distinctClasses[0].toUpperCase()}`
                  : `Model Divergence Detected: Models disagree across classes (${distinctClasses.join(', ')})`}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--prism-slate)', marginTop: 2 }}>
                Agreement between neural architectures is an experimental metric and does not constitute independent clinical confirmation.
              </div>
            </div>
          </div>

          {/* Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
            {comparisonResult.results.map((res) => (
              <div key={res.model_id} className="white-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--prism-indigo)', fontWeight: 600 }}>
                    {res.model_id}
                  </span>
                  <span className={`badge-class ${getBadgeClass(res.predicted_class)}`}>
                    {res.predicted_class || 'Failed'}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--prism-navy)', marginBottom: 14 }}>
                  {res.display_name}
                </h3>

                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', marginBottom: 16 }}>
                  <div>
                    <span style={{ fontSize: '0.74rem', color: 'var(--prism-slate-light)', display: 'block' }}>Confidence</span>
                    <strong style={{ fontSize: '1.3rem', color: 'var(--prism-navy)' }}>
                      {(res.confidence * 100).toFixed(1)}%
                    </strong>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.74rem', color: 'var(--prism-slate-light)', display: 'block' }}>Inference Duration</span>
                    <strong style={{ fontSize: '1.1rem', fontFamily: 'var(--font-mono)', color: 'var(--prism-slate)' }}>
                      {res.inference_time_ms} ms
                    </strong>
                  </div>
                </div>

                {/* Probability Distribution */}
                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--prism-slate)', textTransform: 'uppercase', marginBottom: 8 }}>
                    Class Probabilities
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {Object.entries(res.class_probabilities || {}).map(([cls, prob]) => {
                      const pct = (prob * 100).toFixed(1);
                      const isTop = cls === res.predicted_class;
                      const color = CLASS_COLORS[cls] || '#4f46e5';
                      return (
                        <div key={cls}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 2 }}>
                            <span style={{ textTransform: 'capitalize', fontWeight: isTop ? 700 : 500, color: isTop ? 'var(--prism-navy)' : 'var(--prism-slate)' }}>
                              {cls}
                            </span>
                            <span style={{ fontFamily: 'var(--font-mono)', color: isTop ? color : 'var(--prism-slate-light)' }}>
                              {pct}%
                            </span>
                          </div>
                          <div style={{ height: 6, background: '#f1f5f9', borderRadius: 3, overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${pct}%`, background: color }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
