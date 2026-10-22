import React, { useState, useEffect } from 'react';
import {
  History,
  Download,
  Trash2,
  RefreshCw,
  Eye,
  Filter,
  X,
  Clock,
  CheckCircle2
} from 'lucide-react';
import { PageHeader, LoadingSkeleton, EmptyState } from '../components/common/CommonComponents';
import { historyService } from '../services/historyService';

export default function PredictionHistoryPage() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(10);
  const [classFilter, setClassFilter] = useState('');
  const [modelFilter, setModelFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await historyService.getHistory({
        limit,
        offset: page * limit,
        predictedClass: classFilter || undefined,
        modelId: modelFilter || undefined,
      });
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to load prediction history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, classFilter, modelFilter]);

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete prediction record #${id}?`)) return;
    try {
      await historyService.deletePrediction(id);
      fetchHistory();
      if (selectedRecord?.id === id) setSelectedRecord(null);
    } catch (err) {
      alert('Error deleting record: ' + err.message);
    }
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

  const exportUrl = historyService.getExportCsvUrl({
    predictedClass: classFilter || undefined,
    modelId: modelFilter || undefined,
  });

  return (
    <div>
      <PageHeader
        title="Prediction History & Audit"
        subtitle="Historical log of all recorded brain MRI evaluations with database persistence and CSV export."
        badge={`${total} Total Records`}
        action={
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={fetchHistory}
              className="btn-secondary"
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
              title="Refresh"
            >
              <RefreshCw size={15} />
              <span>Refresh</span>
            </button>
            <a
              href={exportUrl}
              target="_blank"
              rel="noreferrer"
              className="btn-primary"
              style={{ padding: '8px 16px', fontSize: '0.85rem' }}
            >
              <Download size={15} />
              <span>Export CSV</span>
            </a>
          </div>
        }
      />

      {/* Filter Toolbar */}
      <div className="white-card" style={{ padding: '16px 20px', marginBottom: 24, display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.85rem', fontWeight: 600, color: 'var(--prism-slate)' }}>
          <Filter size={16} />
          <span>Filters:</span>
        </div>

        <select
          value={classFilter}
          onChange={(e) => { setClassFilter(e.target.value); setPage(0); }}
          style={{ padding: '7px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border)', background: 'var(--prism-surface)', fontSize: '0.86rem', color: 'var(--prism-navy)' }}
        >
          <option value="">All Tumor Histologies</option>
          <option value="glioma">Glioma</option>
          <option value="meningioma">Meningioma</option>
          <option value="notumor">No Tumor</option>
          <option value="pituitary">Pituitary</option>
        </select>

        <select
          value={modelFilter}
          onChange={(e) => { setModelFilter(e.target.value); setPage(0); }}
          style={{ padding: '7px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--prism-border)', background: 'var(--prism-surface)', fontSize: '0.86rem', color: 'var(--prism-navy)' }}
        >
          <option value="">All Trained Models</option>
          <option value="hybrid_v1">hybrid_v1 (Phase 1)</option>
          <option value="hybrid_v1_final">hybrid_v1_final (Phase 1 Final)</option>
          <option value="hybrid_v2_finetuned">hybrid_v2_finetuned (Phase 2 Checkpoint)</option>
        </select>

        {(classFilter || modelFilter) && (
          <button
            onClick={() => { setClassFilter(''); setModelFilter(''); setPage(0); }}
            style={{ background: 'none', border: 'none', color: 'var(--prism-indigo)', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Table Content */}
      <div className="white-table-wrap">
        <table className="white-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp</th>
              <th>Model Identifier</th>
              <th>Predicted Class</th>
              <th>Confidence</th>
              <th>Latency</th>
              <th>Scan Persisted</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="8" style={{ padding: 24 }}>
                  <LoadingSkeleton height={32} count={5} />
                </td>
              </tr>
            ) : items.length > 0 ? (
              items.map((item) => (
                <tr key={item.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>#{item.id}</td>
                  <td style={{ fontSize: '0.82rem', color: 'var(--prism-slate)' }}>
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--prism-indigo)' }}>
                      {item.model_id}
                    </span>
                  </td>
                  <td>
                    <span className={`badge-class ${getBadgeClass(item.predicted_class)}`}>
                      {item.predicted_class}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{(item.confidence * 100).toFixed(1)}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--prism-slate-light)' }}>
                    {item.inference_time_ms} ms
                  </td>
                  <td>{item.image_saved ? '✓ Saved' : '—'}</td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => setSelectedRecord(item)}
                        className="btn-secondary"
                        style={{ padding: '5px 10px', fontSize: '0.75rem' }}
                        title="View Full Probability Breakdown"
                      >
                        <Eye size={14} />
                        <span>Inspect</span>
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        style={{ background: 'none', border: 'none', color: 'var(--prism-rose)', cursor: 'pointer', padding: 6, borderRadius: 4 }}
                        title="Delete Record"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8">
                  <EmptyState
                    icon={History}
                    title="No Prediction Records Found"
                    description="No analyses matched your current filter criteria or no scans have been classified yet."
                  />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 20 }}>
        <span style={{ fontSize: '0.82rem', color: 'var(--prism-slate-light)' }}>
          Showing Page {page + 1} of {Math.max(1, Math.ceil(total / limit))} ({total} total analyses)
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn-secondary"
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            style={{ fontSize: '0.82rem', padding: '6px 16px' }}
          >
            Previous
          </button>
          <button
            className="btn-secondary"
            disabled={(page + 1) * limit >= total}
            onClick={() => setPage((p) => p + 1)}
            style={{ fontSize: '0.82rem', padding: '6px 16px' }}
          >
            Next
          </button>
        </div>
      </div>

      {/* Detail Inspection Modal */}
      {selectedRecord && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.45)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: 20,
          }}
          onClick={() => setSelectedRecord(null)}
        >
          <div
            className="white-card"
            style={{ maxWidth: 540, width: '100%', maxHeight: '90vh', overflowY: 'auto' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18 }}>
              <div style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--prism-navy)' }}>
                Analysis Record #{selectedRecord.id}
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                style={{ background: 'none', border: 'none', color: 'var(--prism-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20, background: 'var(--prism-surface-subtle)', padding: 14, borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <div>
                <span style={{ color: 'var(--prism-slate-light)' }}>Class:</span>{' '}
                <strong style={{ textTransform: 'capitalize' }}>{selectedRecord.predicted_class}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--prism-slate-light)' }}>Confidence:</span>{' '}
                <strong>{(selectedRecord.confidence * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span style={{ color: 'var(--prism-slate-light)' }}>Model:</span>{' '}
                <span style={{ fontFamily: 'var(--font-mono)' }}>{selectedRecord.model_id}</span>
              </div>
              <div>
                <span style={{ color: 'var(--prism-slate-light)' }}>Duration:</span>{' '}
                <span>{selectedRecord.inference_time_ms} ms</span>
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <div style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--prism-navy)', marginBottom: 10 }}>
                Class Probabilities:
              </div>
              {Object.entries(selectedRecord.class_probabilities || {}).map(([c, p]) => (
                <div key={c} style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 3 }}>
                    <span style={{ textTransform: 'capitalize' }}>{c}</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>{(p * 100).toFixed(2)}%</span>
                  </div>
                  <div style={{ height: 6, background: '#f1f5f9', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${p * 100}%`, background: 'var(--prism-indigo)' }} />
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => setSelectedRecord(null)}
              className="btn-secondary"
              style={{ width: '100%' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
