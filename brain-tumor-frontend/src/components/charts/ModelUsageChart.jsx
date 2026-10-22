import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

const MODEL_COLORS = ['#4f46e5', '#0d9488', '#d97706'];

export default function ModelUsageChart({ modelCounts = {} }) {
  const chartData = Object.entries(modelCounts).map(([modelId, count]) => ({
    modelId,
    displayName:
      modelId === 'hybrid_v1'
        ? 'Hybrid v1 (Phase 1)'
        : modelId === 'hybrid_v1_final'
        ? 'Hybrid v1 Final'
        : modelId === 'hybrid_v2_finetuned'
        ? 'Hybrid v2 Fine-tuned'
        : modelId,
    analyses: count,
  }));

  const total = chartData.reduce((acc, curr) => acc + curr.analyses, 0);

  if (total === 0) {
    return (
      <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--prism-muted)', fontSize: '0.86rem' }}>
        No model utilization data recorded yet.
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="displayName"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: '#e2e8f0' }}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
          />
          <Tooltip
            formatter={(val) => [`${val} analyses`, 'Usage']}
            contentStyle={{
              backgroundColor: '#ffffff',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 12px rgba(15, 23, 42, 0.08)',
              fontSize: '0.82rem',
            }}
          />
          <Bar dataKey="analyses" radius={[6, 6, 0, 0]}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={MODEL_COLORS[index % MODEL_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
