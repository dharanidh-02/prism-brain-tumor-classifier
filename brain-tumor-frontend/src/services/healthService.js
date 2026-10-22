import { apiRequest } from './apiClient';

export const healthService = {
  getHealth: () => apiRequest('/health'),
  getApiV1Health: () => apiRequest('/api/v1/health'),
};
