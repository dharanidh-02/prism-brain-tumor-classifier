import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

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

export default function ClassDistributionChart({ classCounts = {} }) {
  const chartData = Object.entries(classCounts)
    .filter(([_, count]) => count > 0)
    .map(([cls, count]) => ({
      name: CLASS_LABELS[cls?.toLowerCase()] || cls,
      value: count,
      key: cls?.toLowerCase(),
    }));

  const total = chartData.reduce((acc, curr) => acc + curr.value, 0);

  if (total === 0) {
    return (
      <div style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--prism-muted)', fontSize: '0.86rem' }}>
        No class distribution data available yet.
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={88}
            paddingAngle={4}
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell
                key={entry.key}
                fill={CLASS_COLORS[entry.key] || '#0ea5e9'}
                stroke="#ffffff"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [
              `${value} (${((value / total) * 100).toFixed(1)}%)`,
              'Analyses',
            ]}
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
            layout="horizontal"
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ fontSize: '0.78rem', paddingTop: '10px' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
