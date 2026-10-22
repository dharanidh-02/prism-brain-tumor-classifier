import { apiRequest } from './apiClient';

export const analyticsService = {
  getOverview: () => apiRequest('/api/v1/analytics/overview'),
  getModelPerformance: () => apiRequest('/api/v1/analytics/model-performance'),
};
