import React from 'react';
import {
  Database,
  FileText,
  Layers,
  ExternalLink,
  CheckCircle2,
  ShieldAlert,
  Image
} from 'lucide-react';
import { PageHeader } from '../components/common/CommonComponents';

export default function DatasetExplorerPage() {
  const classes = [
    {
      name: 'Glioma',
      description: 'Primary brain tumors originating in glial cells (astrocytomas, oligodendrogliomas, glioblastomas). Characterized by irregular margins and surrounding hyperintense edema.',
      key: 'glioma',
      color: '#e11d48',
    },
    {
      name: 'Meningioma',
      description: 'Typically benign, extra-axial tumors arising from meningothelial arachnoid cells. Exhibits uniform contrast enhancement and characteristic dural tail sign.',
      key: 'meningioma',
      color: '#ea580c',
    },
    {
      name: 'No Tumor',
      description: 'Normal brain scans showing intact cerebral hemispheres, ventricles, sulci, and brainstem without space-occupying lesions or structural midline shifts.',
      key: 'notumor',
      color: '#059669',
    },
    {
      name: 'Pituitary',
      description: 'Sellar lesions arising from anterior pituitary lobe adenomas. Typically cause expansion of the sella turcica and potential chiasmatic compression.',
      key: 'pituitary',
      color: '#7c3aed',
    },
  ];

  return (
    <div>
      <PageHeader
        title="Dataset Explorer"
        subtitle="Benchmark dataset specifications, histology breakdown, training splits, and radiological imaging protocols."
        badge="Data Provenance"
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24, marginBottom: 28 }}>
        {/* Dataset Metadata Card */}
        <div className="white-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <Database size={20} style={{ color: 'var(--prism-indigo)' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              Benchmark Dataset Profile
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: '0.86rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 8, borderBottom: '1px solid var(--prism-border-light)' }}>
              <span style={{ color: 'var(--prism-slate-light)' }}>Dataset Title:</span>
              <strong style={{ color: 'var(--prism-navy)' }}>Brain Tumor MRI Dataset (4-Class)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 8, borderBottom: '1px solid var(--prism-border-light)' }}>
              <span style={{ color: 'var(--prism-slate-light)' }}>Imaging Modalities:</span>
              <strong style={{ color: 'var(--prism-navy)' }}>T1-weighted, T2-weighted, Contrast Enhanced</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 8, borderBottom: '1px solid var(--prism-border-light)' }}>
              <span style={{ color: 'var(--prism-slate-light)' }}>Orientation Planes:</span>
              <strong style={{ color: 'var(--prism-navy)' }}>Axial, Coronal, Sagittal slices</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 8, borderBottom: '1px solid var(--prism-border-light)' }}>
              <span style={{ color: 'var(--prism-slate-light)' }}>Target Classes:</span>
              <strong style={{ color: 'var(--prism-navy)' }}>4 Distinct Categories</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--prism-slate-light)' }}>Input Preprocessing:</span>
              <strong style={{ color: 'var(--prism-navy)' }}>224 × 224 RGB Normalization</strong>
            </div>
          </div>
        </div>

        {/* Train/Test Split Protocol */}
        <div className="white-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <Layers size={20} style={{ color: 'var(--prism-teal)' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              Evaluation Split Methodology
            </h3>
          </div>

          <p style={{ fontSize: '0.86rem', color: 'var(--prism-slate)', lineHeight: 1.5, marginBottom: 16 }}>
            The training pipeline used stratified 80/20 train-test partitioning with 10% validation holdout for model selection:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: '0.82rem' }}>
            <div style={{ padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 6, display: 'flex', justifyContent: 'space-between' }}>
              <span>Phase 1 Training Protocol:</span>
              <strong>Dual Backbone Feature Extraction (Frozen Weights)</strong>
            </div>
            <div style={{ padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 6, display: 'flex', justifyContent: 'space-between' }}>
              <span>Phase 2 Fine-tuning Protocol:</span>
              <strong>Unfrozen Backbones with Low Learning Rate (1e-5)</strong>
            </div>
            <div style={{ padding: '8px 12px', background: 'var(--prism-surface-subtle)', borderRadius: 6, display: 'flex', justifyContent: 'space-between' }}>
              <span>Verified Test Split Accuracy:</span>
              <strong style={{ color: 'var(--prism-emerald)' }}>93.12% (Phase 1) / 92.81% (Phase 2)</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Class Descriptions */}
      <div className="white-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--prism-navy)', marginBottom: 18 }}>
          Target Histopathological Classes
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 18 }}>
          {classes.map((cls) => (
            <div
              key={cls.key}
              style={{
                padding: 18,
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--prism-border)',
                background: 'var(--prism-surface-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: cls.color }} />
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
                  {cls.name}
                </h4>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--prism-slate)', lineHeight: 1.5 }}>
                {cls.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
