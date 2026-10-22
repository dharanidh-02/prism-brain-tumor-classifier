import { apiRequest, API_BASE_URL } from './apiClient';

export const historyService = {
  getHistory: ({ limit = 20, offset = 0, predictedClass, modelId, startDate, endDate } = {}) => {
    const params = new URLSearchParams();
    params.append('limit', limit);
    params.append('offset', offset);
    if (predictedClass) params.append('predicted_class', predictedClass);
    if (modelId) params.append('model_id', modelId);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    return apiRequest(`/api/v1/history?${params.toString()}`);
  },

  getPrediction: (id) => apiRequest(`/api/v1/history/${id}`),

  deletePrediction: (id) =>
    apiRequest(`/api/v1/history/${id}`, {
      method: 'DELETE',
    }),

  getExportCsvUrl: ({ predictedClass, modelId, startDate, endDate } = {}) => {
    const params = new URLSearchParams();
    if (predictedClass) params.append('predicted_class', predictedClass);
    if (modelId) params.append('model_id', modelId);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return `${API_BASE_URL}/api/v1/history/export/csv${query ? `?${query}` : ''}`;
  },
};
