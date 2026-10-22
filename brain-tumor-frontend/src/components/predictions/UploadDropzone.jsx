import React, { useRef, useState } from 'react';
import { Upload, Image, X, AlertCircle } from 'lucide-react';

export default function UploadDropzone({
  file,
  previewUrl,
  onFileSelect,
  onClear,
  error,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div>
      {previewUrl ? (
        <div style={{ position: 'relative', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--prism-border)', background: '#000000', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <img
            src={previewUrl}
            alt="MRI Preview"
            style={{ maxHeight: 300, width: '100%', objectFit: 'contain' }}
          />
          <button
            type="button"
            onClick={onClear}
            style={{
              position: 'absolute',
              top: 12,
              right: 12,
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '50%',
              width: 32,
              height: 32,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            }}
            title="Remove Image"
          >
            <X size={18} />
          </button>
          <div style={{ width: '100%', padding: '10px 16px', background: 'var(--prism-surface)', borderTop: '1px solid var(--prism-border)', display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--prism-slate)' }}>
            <span style={{ fontWeight: 600 }}>{file?.name}</span>
            <span>{(file?.size / 1024).toFixed(1)} KB</span>
          </div>
        </div>
      ) : (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragging ? 'var(--prism-indigo)' : '#cbd5e1'}`,
            borderRadius: 'var(--radius-lg)',
            padding: '42px 24px',
            textAlign: 'center',
            backgroundColor: isDragging ? 'var(--prism-indigo-subtle)' : 'var(--prism-surface-subtle)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png"
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                onFileSelect(e.target.files[0]);
              }
            }}
          />

          <div
            style={{
              width: 54,
              height: 54,
              borderRadius: '50%',
              backgroundColor: 'var(--prism-surface)',
              border: '1px solid var(--prism-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--prism-indigo)',
              marginBottom: 14,
              boxShadow: '0 2px 6px rgba(15, 23, 42, 0.04)',
            }}
          >
            <Upload size={24} />
          </div>

          <div style={{ fontWeight: 700, fontSize: '0.98rem', color: 'var(--prism-navy)', marginBottom: 4 }}>
            Click to upload or drag & drop brain MRI scan
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--prism-slate-light)', maxWidth: 360 }}>
            Supports JPEG (.jpg, .jpeg) and PNG (.png) up to 10 MB. Preprocessed automatically to 224 × 224.
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 'var(--radius-sm)', background: 'var(--prism-rose-subtle)', border: '1px solid var(--prism-rose-border)', color: 'var(--prism-rose)', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
