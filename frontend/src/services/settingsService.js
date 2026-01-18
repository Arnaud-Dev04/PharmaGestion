import api from './api';

export const settingsService = {
  /**
   * Get current settings
   */
  async getSettings() {
    const response = await api.get('/settings');
    return response.data;
  },

  /**
   * Update settings
   */
  async updateSettings(data) {
    const response = await api.put('/settings', data);
    return response.data;
  },
};

export default settingsService;
