import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('PRISM UI Error Boundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '400px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px 24px',
          textAlign: 'center',
          background: 'var(--prism-card-bg)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--prism-border)',
          margin: '24px'
        }}>
          <div style={{
            width: 56,
            height: 56,
            borderRadius: '50%',
            background: 'var(--prism-rose-subtle)',
            color: 'var(--prism-rose)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16
          }}>
            <AlertTriangle size={28} />
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--prism-navy)', marginBottom: 8 }}>
            Clinical Workspace Encountered an Issue
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--prism-slate)', maxWidth: 500, marginBottom: 20 }}>
            {this.state.error?.message || 'An unexpected rendering error occurred. You can reload this view safely.'}
          </p>
          <button
            onClick={this.handleReset}
            className="prism-btn-primary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
          >
            <RefreshCw size={16} />
            Reload Workspace
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
