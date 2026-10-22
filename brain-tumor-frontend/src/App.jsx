import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import OverviewPage from './pages/OverviewPage';
import AnalyzeMRIPage from './pages/AnalyzeMRIPage';
import PredictionHistoryPage from './pages/PredictionHistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ModelLaboratoryPage from './pages/ModelLaboratoryPage';
import ModelComparisonPage from './pages/ModelComparisonPage';
import ExplainabilityPage from './pages/ExplainabilityPage';
import DatasetExplorerPage from './pages/DatasetExplorerPage';
import SettingsPage from './pages/SettingsPage';
import ErrorBoundary from './components/common/ErrorBoundary';
import './styles/prism-theme.css';

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AppShell>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/analyze" element={<AnalyzeMRIPage />} />
            <Route path="/history" element={<PredictionHistoryPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/models" element={<ModelLaboratoryPage />} />
            <Route path="/model-comparison" element={<ModelComparisonPage />} />
            <Route path="/explainability" element={<ExplainabilityPage />} />
            <Route path="/dataset" element={<DatasetExplorerPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppShell>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
