import React, { useState, useEffect } from 'react';
import NavigationPanel from '../components/dashboard/NavigationPanel';
import SystemStatusPanel from '../components/dashboard/SystemStatusPanel';
import AnalysisDataPanel from '../components/dashboard/AnalysisDataPanel';
import { healthService } from '../services/healthService';
import { analyticsService } from '../services/analyticsService';
import { historyService } from '../services/historyService';

export default function OverviewPage() {
  const [health, setHealth] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [hData, aData, pData, histData] = await Promise.allSettled([
        healthService.getHealth(),
        analyticsService.getOverview(),
        analyticsService.getModelPerformance(),
        historyService.getHistory({ limit: 5 }),
      ]);

      if (hData.status === 'fulfilled') setHealth(hData.value);
      if (aData.status === 'fulfilled') setAnalytics(aData.value);
      if (pData.status === 'fulfilled') setPerformance(pData.value);
      if (histData.status === 'fulfilled') setRecentAnalyses(histData.value?.items || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div>
      {/* Top Wireframe Row: 4 Navigation Tiles (Left) + System Status (Right) */}
      <div className="wireframe-grid">
        <NavigationPanel />
        <SystemStatusPanel health={health} loading={loading} />
      </div>

      {/* Bottom Wireframe Row: Wide Analysis Data Panel */}
      <AnalysisDataPanel
        analytics={analytics}
        performance={performance}
        recentAnalyses={recentAnalyses}
        health={health}
        loading={loading}
        onRefresh={fetchDashboardData}
      />
    </div>
  );
}
