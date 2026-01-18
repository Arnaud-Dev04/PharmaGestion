import api from './api';

export const dashboardService = {
  /**
   * Get dashboard statistics
   * @returns {Promise} Dashboard stats including KPIs and revenue chart
   */
  async getDashboardStats(days = 7) {
    const response = await api.get(`/dashboard/stats?days=${days}`);
    return response.data;
  },

  /**
   * Get low stock medicines
   */
  async getLowStockMedicines() {
    const response = await api.get('/medicines?low_stock=true');
    return response.data;
  },

  /**
   * Get expiring medicines
   */
  async getExpiringMedicines() {
    const response = await api.get('/medicines/expiring-soon');
    return response.data;
  },

  /**
   * Get all suppliers
   */
  async getSuppliers() {
    const response = await api.get('/suppliers');
    return response.data;
  },

  /**
   * Get cancelled sales
   */
  async getCancelledSales() {
    const response = await api.get('/sales/history?status_filter=cancelled&page_size=20');
    return response.data.items || [];
  },
};

export default dashboardService;

