import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export default function ModelPerformanceChart({ performanceData }) {
  if (!performanceData || !performanceData.models) {
    return (
      <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--prism-muted)', fontSize: '0.86rem' }}>
        No verified evaluation benchmark data available.
      </div>
    );
  }

  const chartData = performanceData.models.map((m) => ({
    name: m.model_id === 'hybrid_v1' ? 'Phase 1 (v1)' : m.model_id === 'hybrid_v1_final' ? 'Phase 1 (Final)' : 'Phase 2 (Checkpoint)',
    Accuracy: m.metrics?.test_accuracy ? Number((m.metrics.test_accuracy * 100).toFixed(2)) : 0,
    F1Score: m.metrics?.macro_f1_score ? Number((m.metrics.macro_f1_score * 100).toFixed(2)) : 0,
    ROCAUC: m.metrics?.macro_roc_auc ? Number((m.metrics.macro_roc_auc * 100).toFixed(2)) : 0,
  }));

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="name"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#e2e8f0' }}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={12}
            domain={[85, 100]}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            formatter={(val, name) => [`${val}%`, name]}
            contentStyle={{
              backgroundColor: '#ffffff',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 12px rgba(15, 23, 42, 0.08)',
              fontSize: '0.82rem',
            }}
          />
          <Legend
            iconType="circle"
            wrapperStyle={{ fontSize: '0.78rem', paddingTop: '10px' }}
          />
          <Bar dataKey="Accuracy" name="Test Accuracy" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          <Bar dataKey="F1Score" name="Macro F1" fill="#0d9488" radius={[4, 4, 0, 0]} />
          <Bar dataKey="ROCAUC" name="Macro ROC-AUC" fill="#7c3aed" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
