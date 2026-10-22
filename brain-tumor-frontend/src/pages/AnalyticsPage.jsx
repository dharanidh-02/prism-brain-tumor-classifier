import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Award,
  Clock,
  Layers,
  PieChart,
  Info,
  ShieldAlert
} from 'lucide-react';
import { PageHeader, LoadingSkeleton } from '../components/common/CommonComponents';
import MetricCard from '../components/common/MetricCard';
import ClassDistributionChart from '../components/charts/ClassDistributionChart';
import ModelUsageChart from '../components/charts/ModelUsageChart';
import ModelPerformanceChart from '../components/charts/ModelPerformanceChart';
import { analyticsService } from '../services/analyticsService';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      analyticsService.getOverview(),
      analyticsService.getModelPerformance(),
    ]).then(([oData, pData]) => {
      if (oData.status === 'fulfilled') setOverview(oData.value);
      if (pData.status === 'fulfilled') setPerformance(pData.value);
      setLoading(false);
    });
  }, []);

  return (
    <div>
      <PageHeader
        title="Analytics & Model Reports"
        subtitle="Comprehensive operational workload metrics and verified deep learning benchmark evaluations."
        badge="Performance Intelligence"
      />

      {/* SECTION A: OPERATIONAL ANALYTICS */}
      <div style={{ marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <div style={{ width: 8, height: 24, borderRadius: 4, background: 'var(--prism-indigo)' }} />
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
            Section A: Operational Analytics
          </h2>
          <span style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
            (Live metrics derived from stored inference records)
          </span>
        </div>

        <div className="metrics-row">
          <MetricCard
            label="Total Predictions"
            value={overview?.total_predictions}
            sublabel="Recorded MRI scans"
            icon={TrendingUp}
            accentColor="var(--prism-indigo)"
            loading={loading}
          />
          <MetricCard
            label="Average CPU Latency"
            value={overview?.average_inference_time_ms ? `${overview.average_inference_time_ms} ms` : '—'}
            sublabel="End-to-end inference pass"
            icon={Clock}
            accentColor="var(--prism-amber)"
            loading={loading}
          />
          <MetricCard
            label="Active Engine Instances"
            value={overview?.operational_models_count}
            sublabel="Operational Keras models"
            icon={Layers}
            accentColor="var(--prism-emerald)"
            loading={loading}
          />
          <MetricCard
            label="24-Hour Throughput"
            value={overview?.recent_predictions_24h}
            sublabel="Recent requests served"
            icon={BarChart3}
            accentColor="var(--prism-teal)"
            loading={loading}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 24 }}>
          <div className="white-card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 16 }}>
              Historical Diagnostic Distribution
            </h3>
            <ClassDistributionChart classCounts={overview?.predictions_by_class} />
          </div>

          <div className="white-card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 16 }}>
              Inference Volume by Model Architecture
            </h3>
            <ModelUsageChart modelCounts={overview?.predictions_by_model} />
          </div>
        </div>
      </div>

      {/* SECTION B: MODEL EVALUATION & PROVENANCE */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <div style={{ width: 8, height: 24, borderRadius: 4, background: 'var(--prism-teal)' }} />
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.25rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
            Section B: Verified Model Evaluation Benchmarks
          </h2>
          <span style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)' }}>
            (Independent test split benchmarks with strict provenance)
          </span>
        </div>

        <div className="white-card" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 18, padding: '12px 16px', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border-light)' }}>
            <Info size={18} style={{ color: 'var(--prism-indigo)', flexShrink: 0 }} />
            <span style={{ fontSize: '0.84rem', color: 'var(--prism-slate)' }}>
              {performance?.disclaimer || 'Model performance metrics reflect fixed evaluation benchmarks on test splits and are never calculated from user uploads.'}
            </span>
          </div>

          <div style={{ marginBottom: 28 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 14 }}>
              Comparative Test Metrics Across Model Iterations
            </h3>
            <ModelPerformanceChart performanceData={performance} />
          </div>

          {/* Detailed Metric Cards per Model */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
            {performance?.models?.map((m) => (
              <div
                key={m.model_id}
                style={{
                  padding: 20,
                  border: '1px solid var(--prism-border)',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--prism-surface-subtle)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div>
                    <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
                      {m.display_name}
                    </h4>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.76rem', color: 'var(--prism-indigo)' }}>
                      {m.model_id}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: 4, background: '#ffffff', border: '1px solid var(--prism-border)', fontWeight: 600 }}>
                    {m.reported_file_size_mb} MB
                  </span>
                </div>

                <div style={{ fontSize: '0.78rem', color: 'var(--prism-slate-light)', marginBottom: 14 }}>
                  {m.metrics.provenance} • {m.metrics.evaluation_split}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
                  <div style={{ padding: '8px 12px', background: '#ffffff', borderRadius: 6, border: '1px solid var(--prism-border-light)' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--prism-slate-light)' }}>Test Accuracy</span>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--prism-emerald)' }}>
                      {(m.metrics.test_accuracy * 100).toFixed(2)}%
                    </div>
                  </div>

                  <div style={{ padding: '8px 12px', background: '#ffffff', borderRadius: 6, border: '1px solid var(--prism-border-light)' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--prism-slate-light)' }}>Test Loss</span>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
                      {m.metrics.test_loss}
                    </div>
                  </div>

                  {m.metrics.macro_f1_score && (
                    <div style={{ padding: '8px 12px', background: '#ffffff', borderRadius: 6, border: '1px solid var(--prism-border-light)' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--prism-slate-light)' }}>Macro F1-Score</span>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--prism-indigo)' }}>
                        {(m.metrics.macro_f1_score * 100).toFixed(2)}%
                      </div>
                    </div>
                  )}

                  {m.metrics.macro_roc_auc && (
                    <div style={{ padding: '8px 12px', background: '#ffffff', borderRadius: 6, border: '1px solid var(--prism-border-light)' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--prism-slate-light)' }}>Macro ROC-AUC</span>
                      <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--prism-teal)' }}>
                        {m.metrics.macro_roc_auc}
                      </div>
                    </div>
                  )}
                </div>

                {m.metrics.notes && (
                  <div style={{ fontSize: '0.76rem', color: 'var(--prism-slate-light)', fontStyle: 'italic' }}>
                    Note: {m.metrics.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
