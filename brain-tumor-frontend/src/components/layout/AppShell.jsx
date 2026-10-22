import React, { useState } from 'react';
import AppSidebar from './AppSidebar';
import TopBar from './TopBar';

export default function AppShell({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="prism-shell">
      <AppSidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className="prism-workspace">
        <TopBar onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />
        <main className="workspace-content">{children}</main>
      </div>
    </div>
  );
}
