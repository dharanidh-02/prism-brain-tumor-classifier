import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3,
  RefreshCw,
  ArrowUpRight,
  Clock,
  Brain,
  Layers,
  PieChart,
  TrendingUp,
  Award
} from 'lucide-react';
import MetricCard from '../common/MetricCard';
import PredictionActivityChart from '../charts/PredictionActivityChart';
import ClassDistributionChart from '../charts/ClassDistributionChart';
import ModelUsageChart from '../charts/ModelUsageChart';
import ModelPerformanceChart from '../charts/ModelPerformanceChart';

export default function AnalysisDataPanel({
  analytics,
  performance,
  recentAnalyses = [],
  health,
  loading = false,
  onRefresh,
}) {
  const [activeChartTab, setActiveChartTab] = useState('distribution');

  // Compute most frequent prediction class from real analytics
  const classCounts = analytics?.predictions_by_class || {};
  let mostFrequentClass = '—';
  let maxCount = 0;
  Object.entries(classCounts).forEach(([cls, count]) => {
    if (count > maxCount) {
      maxCount = count;
      mostFrequentClass = cls;
    }
  });

  // Calculate prediction activity line data from recent records
  const dateMap = {};
  recentAnalyses.forEach((item) => {
    const d = new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    dateMap[d] = (dateMap[d] || 0) + 1;
  });
  const activityData = Object.entries(dateMap).map(([date, count]) => ({ date, count }));

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
    <section className="analysis-panel" aria-labelledby="analysis-data-heading">
      {/* Header */}
      <div className="analysis-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <BarChart3 size={22} style={{ color: 'var(--prism-indigo)' }} />
            <h2 id="analysis-data-heading" style={{ fontFamily: 'var(--font-display)', fontSize: '1.35rem', fontWeight: 800, color: 'var(--prism-navy)' }}>
              Analysis Data
            </h2>
          </div>
          <p style={{ color: 'var(--prism-slate-light)', fontSize: '0.86rem', marginTop: 4 }}>
            Insights from recorded predictions and model evaluation.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            onClick={onRefresh}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '7px 14px' }}
            disabled={loading}
            title="Refresh Data"
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            <span>Refresh</span>
          </button>

          <Link
            to="/analytics"
            className="btn-primary"
            style={{ fontSize: '0.82rem', padding: '7px 16px' }}
          >
            <span>Full Reports</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* 4 Overview Metrics Cards */}
      <div className="metrics-row">
        <MetricCard
          label="Total Analyses"
          value={analytics?.total_predictions}
          sublabel="Saved SQLite records"
          icon={Brain}
          accentColor="var(--prism-indigo)"
          loading={loading}
        />
        <MetricCard
          label="Most Frequent Prediction"
          value={mostFrequentClass}
          sublabel={maxCount > 0 ? `${maxCount} analyses recorded` : 'No records yet'}
          icon={TrendingUp}
          accentColor="var(--prism-rose)"
          loading={loading}
        />
        <MetricCard
          label="Available Models"
          value={health ? `${health.loaded_models_count} / ${health.total_models_count}` : '—'}
          sublabel="Operational neural engines"
          icon={Layers}
          accentColor="var(--prism-emerald)"
          loading={loading}
        />
        <MetricCard
          label="Average Inference Time"
          value={analytics?.average_inference_time_ms ? `${analytics.average_inference_time_ms} ms` : '—'}
          sublabel="CPU inference latency"
          icon={Clock}
          accentColor="var(--prism-amber)"
          loading={loading}
        />
      </div>

      {/* Interactive Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20, marginBottom: 28 }}>
        {/* Chart 1: Class Distribution */}
        <div style={{ background: 'var(--prism-surface-subtle)', border: '1px solid var(--prism-border)', borderRadius: 'var(--radius-md)', padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <PieChart size={17} style={{ color: 'var(--prism-indigo)' }} />
            <h3 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
              Tumor Class Distribution
            </h3>
          </div>
          <ClassDistributionChart classCounts={analytics?.predictions_by_class} />
        </div>

        {/* Chart 2: Model Usage */}
        <div style={{ background: 'var(--prism-surface-subtle)', border: '1px solid var(--prism-border)', borderRadius: 'var(--radius-md)', padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Layers size={17} style={{ color: 'var(--prism-teal)' }} />
            <h3 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
              Inference by Model
            </h3>
          </div>
          <ModelUsageChart modelCounts={analytics?.predictions_by_model} />
        </div>

        {/* Chart 3: Verified Benchmarks */}
        <div style={{ background: 'var(--prism-surface-subtle)', border: '1px solid var(--prism-border)', borderRadius: 'var(--radius-md)', padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
            <Award size={17} style={{ color: 'var(--prism-amber)' }} />
            <h3 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
              Verified Model Evaluation
            </h3>
          </div>
          <ModelPerformanceChart performanceData={performance} />
        </div>
      </div>

      {/* Compact Recent Analyses Table */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--prism-navy)' }}>
            Recent Analyses
          </h3>
          <Link
            to="/history"
            style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--prism-indigo)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}
          >
            <span>View All History</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>

        <div className="white-table-wrap">
          <table className="white-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Predicted Class</th>
                <th>Model</th>
                <th>Confidence</th>
                <th>Latency</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentAnalyses.length > 0 ? (
                recentAnalyses.slice(0, 5).map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>#{item.id}</td>
                    <td>
                      <span className={`badge-class ${getBadgeClass(item.predicted_class)}`}>
                        {item.predicted_class}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--prism-slate)' }}>
                        {item.model_id}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{(item.confidence * 100).toFixed(1)}%</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--prism-slate-light)' }}>
                      {item.inference_time_ms} ms
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--prism-slate-light)' }}>
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td>
                      <Link
                        to="/history"
                        className="btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: 'var(--prism-muted)' }}>
                    No analyses recorded yet. Upload an MRI scan via the "Analyze MRI" tile above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
