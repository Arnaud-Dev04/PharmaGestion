import api from './api';

export const adminService = {
  /**
   * Get system license information
   */
  async getLicense() {
    const response = await api.get('/admin/license');
    return response.data;
  },

  /**
   * Update system license
   * @param {string} expiryDate - YYYY-MM-DD format
   */
  async updateLicense(expiryDate) {
    const response = await api.post('/admin/license', {
      expiry_date: expiryDate
    });
    return response.data;
  },

  /**
   * Reset data
   * @param {Object} data - { sales: boolean, products: boolean, users: boolean }
   */
  async resetData(data) {
    const response = await api.post('/admin/reset', data);
    return response.data;
  }
};

export default adminService;
