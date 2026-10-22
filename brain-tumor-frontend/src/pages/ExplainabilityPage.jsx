import React, { useState } from 'react';
import {
  ScanEye,
  Info,
  AlertTriangle,
  Layers,
  Cpu,
  Code2,
  ShieldAlert
} from 'lucide-react';
import { PageHeader, EmptyState } from '../components/common/CommonComponents';

export default function ExplainabilityPage() {
  const [selectedModel, setSelectedModel] = useState('hybrid_v2_finetuned');

  return (
    <div>
      <PageHeader
        title="Explainable AI & Attention Interpretability"
        subtitle="Visualizing feature saliency and self-attention weight allocations across hybrid neural pathways."
        badge="XAI Diagnostic Suite"
      />

      {/* Notice Banner */}
      <div className="white-card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
          <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--prism-amber-subtle)', border: '1px solid var(--prism-amber-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--prism-amber)', flexShrink: 0 }}>
            <AlertTriangle size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 4 }}>
              Grad-CAM Pipeline Verification Status
            </h3>
            <p style={{ fontSize: '0.86rem', color: 'var(--prism-slate)', lineHeight: 1.5 }}>
              Explainability visualization is not currently available for this model. Enable this feature after the explanation pipeline has been verified. In Keras 3 functional multi-backbone models with dual input branches, gradient tape extraction across concatenated layers requires custom gradient hooks.
            </p>
          </div>
        </div>
      </div>

      {/* Model Feature Gating Architecture Diagram */}
      <div className="white-card" style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <Layers size={20} style={{ color: 'var(--prism-indigo)' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
            Hybrid Cross-Branch Self-Attention Mechanism
          </h3>
        </div>

        <p style={{ fontSize: '0.88rem', color: 'var(--prism-slate)', lineHeight: 1.5, marginBottom: 20 }}>
          Instead of relying on post-hoc empirical heatmaps, PRISM achieves intrinsic interpretability through an explicit <strong>Feature Attention Gating Layer</strong> positioned directly after dual-backbone feature fusion:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 24 }}>
          {/* Branch 1 */}
          <div style={{ padding: 16, background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border-light)' }}>
            <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--prism-indigo)', fontWeight: 700 }}>
              Spatial Branch
            </span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', margin: '4px 0' }}>
              EfficientNetB0 Backbone
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--prism-slate-light)' }}>
              Extracts fine-grained edge textures and contrast gradients via inverted residual blocks (1280 output dimensions).
            </div>
          </div>

          {/* Branch 2 */}
          <div style={{ padding: 16, background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border-light)' }}>
            <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--prism-teal)', fontWeight: 700 }}>
              Semantic Branch
            </span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', margin: '4px 0' }}>
              MobileNetV3Large Backbone
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--prism-slate-light)' }}>
              Computes global anatomical morphology with hard-swish activations and squeeze-and-excitation (960 output dimensions).
            </div>
          </div>

          {/* Attention Fusion */}
          <div style={{ padding: 16, background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-indigo-border)' }}>
            <span style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--prism-amber)', fontWeight: 700 }}>
              Gating Core
            </span>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', margin: '4px 0' }}>
              Dual-Projection Attention Gate
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--prism-slate-light)' }}>
              Dense sigmoid gating vector dynamically reweights spatial vs contextual channels before the 4-class output head.
            </div>
          </div>
        </div>

        <div style={{ background: '#f8fafc', padding: 16, borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#1e293b', overflowX: 'auto' }}>
          <code>
            {`# Model Attention Flow:
Input (224x224x3)
  ├──> EfficientNetB0 -> GlobalAvgPool -> Dense(128) ──┐
  └──> MobileNetV3    -> GlobalAvgPool -> Dense(128) ──┴──> Concatenate(256)
                                                               │
                                               Dense(256, Sigmoid Attention Gate)
                                                               │
                                               Multiply(Fusion, Attention Gate)
                                                               │
                                               Dense(128, ReLU) -> Dropout(0.4)
                                                               │
                                               Dense(4, Softmax) -> [glioma, meningioma, notumor, pituitary]`}
          </code>
        </div>
      </div>
    </div>
  );
}
