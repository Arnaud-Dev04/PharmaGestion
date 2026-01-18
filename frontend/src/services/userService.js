import api from './api';

export const userService = {
  /**
   * Get all users (admin only)
   */
  async getAll() {
    const response = await api.get('/auth/users');
    return response.data;
  },

  /**
   * Create a new user
   * @param {Object} userData { username, password, role }
   */
  async create(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  /**
   * Update a user
   * @param {number} userId
   * @param {Object} userData { username, password, role, is_active }
   */
  async update(userId, userData) {
    const response = await api.put(`/users/${userId}`, userData);
    return response.data;
  },

  /**
   * Change user password
   * @param {number} userId
   * @param {string} newPassword
   */
  async updatePassword(userId, newPassword) {
    const response = await api.put(`/auth/users/${userId}/password`, {
      password: newPassword,
    });
    return response.data;
  },

  /**
   * Delete user
   * @param {number} userId
   */
  async delete(userId) {
    const response = await api.delete(`/auth/users/${userId}`);
    return response.data;
  },

  /**
   * Toggle user active status (activate/deactivate)
   * @param {number} userId
   */
  async toggleStatus(userId) {
    const response = await api.put(`/auth/users/${userId}/toggle-status`);
    return response.data;
  },

  /**
   * Get user sales statistics
   * @param {number} userId
   * @param {string} startDate - YYYY-MM-DD format
   * @param {string} endDate - YYYY-MM-DD format
   */
  async getSalesStats(userId, startDate = null, endDate = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get(`/auth/users/${userId}/sales-stats`, { params });
    return response.data;
  },

  /**
   * Get all users performance comparison
   * @param {string} startDate - YYYY-MM-DD format
   * @param {string} endDate - YYYY-MM-DD format
   */
  async getAllPerformance(startDate = null, endDate = null) {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get('/auth/users/sales-performance', { params });
    return response.data;
  },
};

export default userService;

