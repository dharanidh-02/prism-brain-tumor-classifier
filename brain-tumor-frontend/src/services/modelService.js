import { apiRequest } from './apiClient';

export const modelService = {
  getModels: () => apiRequest('/api/v1/models'),
  getModelDetail: (modelId) => apiRequest(`/api/v1/models/${encodeURIComponent(modelId)}`),
  getModelStatus: (modelId) => apiRequest(`/api/v1/models/${encodeURIComponent(modelId)}/status`),
};
