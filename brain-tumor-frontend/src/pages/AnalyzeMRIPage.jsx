import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ScanLine, RefreshCw, Layers, CheckCircle2 } from 'lucide-react';
import { PageHeader } from '../components/common/CommonComponents';
import UploadDropzone from '../components/predictions/UploadDropzone';
import PredictionResultCard from '../components/predictions/PredictionResultCard';
import { modelService } from '../services/modelService';
import { predictionService } from '../services/predictionService';

export default function AnalyzeMRIPage() {
  const [searchParams] = useSearchParams();
  const preselectedModel = searchParams.get('model');

  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('hybrid_v2_finetuned');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [saveImage, setSaveImage] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    modelService.getModels().then((data) => {
      setModels(data);
      if (preselectedModel && data.some((m) => m.model_id === preselectedModel)) {
        setSelectedModel(preselectedModel);
      } else if (data.length > 0 && !selectedModel) {
        setSelectedModel(data[0].model_id);
      }
    }).catch((err) => {
      console.warn('Failed to load models list:', err);
    });
  }, [preselectedModel]);

  const handleFileSelect = (file) => {
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Please upload a valid JPEG or PNG MRI image.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreviewUrl(e.target.result);
    reader.readAsDataURL(file);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select or drag an MRI scan file.');
      return;
    }
    setIsAnalyzing(true);
    setError(null);

    try {
      const data = await predictionService.predictMRI(selectedFile, selectedModel, saveImage);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Analysis failed. Verify backend server is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Analyze Brain MRI"
        subtitle="Upload T1/T2-weighted brain MRI scan to classify tumor histology using hybrid attention neural networks."
        badge="Inference Workspace"
      />

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1.3fr 1fr', gap: 28, alignItems: 'start' }}>
        {/* Left Column: Upload & Controls */}
        <div className="white-card">
          <form onSubmit={handleAnalyze}>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                1. Upload MRI Image
              </label>
              <UploadDropzone
                file={selectedFile}
                previewUrl={previewUrl}
                onFileSelect={handleFileSelect}
                onClear={handleClear}
                error={error}
              />
            </div>

            {/* Model Selection */}
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                2. Select Trained Model
              </label>
              <select
                className="select-input"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                style={{
                  width: '100%',
                  padding: '11px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--prism-border)',
                  backgroundColor: 'var(--prism-surface)',
                  color: 'var(--prism-navy)',
                  fontSize: '0.9rem',
                }}
              >
                {models.length > 0 ? (
                  models.map((m) => (
                    <option key={m.model_id} value={m.model_id}>
                      {m.display_name} ({m.model_id}) — {m.status === 'loaded' ? 'Active' : m.status}
                    </option>
                  ))
                ) : (
                  <>
                    <option value="hybrid_v2_finetuned">Hybrid Fine-tuned (Phase 2 Checkpoint)</option>
                    <option value="hybrid_v1_final">Hybrid EfficientNetB0 + MobileNetV3 (Final Attention)</option>
                    <option value="hybrid_v1">Hybrid EfficientNetB0 + MobileNetV3 (Attention)</option>
                  </>
                )}
              </select>
            </div>

            {/* Persistence Checkbox */}
            <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 10 }}>
              <input
                type="checkbox"
                id="saveImageCheckbox"
                checked={saveImage}
                onChange={(e) => setSaveImage(e.target.checked)}
                style={{ width: 16, height: 16, accentColor: 'var(--prism-indigo)', cursor: 'pointer' }}
              />
              <label htmlFor="saveImageCheckbox" style={{ fontSize: '0.86rem', color: 'var(--prism-slate)', cursor: 'pointer' }}>
                Persist uploaded scan file to local encrypted storage
              </label>
            </div>

            {/* Submit Action */}
            <button
              type="submit"
              className="btn-primary"
              disabled={isAnalyzing || !selectedFile}
              style={{ width: '100%', padding: '13px 24px', fontSize: '0.98rem' }}
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw size={18} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Executing Neural Inference...</span>
                </>
              ) : (
                <>
                  <ScanLine size={18} />
                  <span>Run PRISM Diagnostic Inference</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Prediction Result / Guidance */}
        <div>
          {result ? (
            <PredictionResultCard result={result} />
          ) : (
            <div className="white-card" style={{ padding: 32, textAlign: 'center', color: 'var(--prism-slate-light)' }}>
              <div style={{ width: 60, height: 60, borderRadius: '50%', backgroundColor: 'var(--prism-surface-subtle)', border: '1px solid var(--prism-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--prism-indigo)' }}>
                <ScanLine size={28} />
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 8 }}>
                Ready for Image Analysis
              </h3>
              <p style={{ fontSize: '0.86rem', lineHeight: 1.5, maxWidth: 360, margin: '0 auto 20px' }}>
                Select a brain MRI image and click "Run PRISM Diagnostic Inference". The pipeline will evaluate probabilities for Glioma, Meningioma, No Tumor, and Pituitary.
              </p>
              <div style={{ textAlign: 'left', background: 'var(--prism-surface-subtle)', borderRadius: 'var(--radius-sm)', padding: 16, fontSize: '0.8rem', color: 'var(--prism-slate)' }}>
                <div style={{ fontWeight: 600, color: 'var(--prism-navy)', marginBottom: 6 }}>
                  Pre-processing Workflow:
                </div>
                <ul style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <li>Safe format & EXIF orientation normalization</li>
                  <li>Bicubic resampling to 224 × 224 resolution</li>
                  <li>3-Channel RGB float32 conversion</li>
                  <li>Integrated backbone normalization & gating</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
