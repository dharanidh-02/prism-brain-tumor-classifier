import { apiRequest } from './apiClient';

export const predictionService = {
  predictMRI: (file, modelId, saveImage = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_id', modelId);
    formData.append('save_image', saveImage ? 'true' : 'false');

    return apiRequest('/api/v1/predictions', {
      method: 'POST',
      body: formData,
    });
  },

  compareMRI: (file, modelIds) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_ids', Array.isArray(modelIds) ? modelIds.join(',') : modelIds);

    return apiRequest('/api/v1/predictions/compare', {
      method: 'POST',
      body: formData,
    });
  },
};
