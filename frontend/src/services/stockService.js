import api from './api';

export const stockService = {
  /**
   * Get paginated list of medicines with filters
   */
  async getMedicines(params = {}) {
    const { page = 1, pageSize = 50, search, familyId, typeId, isLowStock, isExpired } = params;
    
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (search) queryParams.append('search', search);
    if (familyId) queryParams.append('family_id', familyId.toString());
    if (typeId) queryParams.append('type_id', typeId.toString());
    if (isLowStock !== undefined) queryParams.append('is_low_stock', isLowStock.toString());
    if (isExpired !== undefined) queryParams.append('is_expired', isExpired.toString());

    const response = await api.get(`/stock/medicines?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Get a single medicine by ID
   */
  async getMedicine(id) {
    const response = await api.get(`/stock/medicines/${id}`);
    return response.data;
  },

  /**
   * Create a new medicine
   */
  async createMedicine(data) {
    const response = await api.post('/stock/medicines', data);
    return response.data;
  },

  /**
   * Update an existing medicine
   */
  async updateMedicine(id, data) {
    const response = await api.put(`/stock/medicines/${id}`, data);
    return response.data;
  },

  /**
   * Delete a medicine
   */
  async deleteMedicine(id) {
    await api.delete(`/stock/medicines/${id}`);
  },

  /**
   * Get stock alerts (low stock + expired)
   */
  async getStockAlerts() {
    const response = await api.get('/stock/alerts');
    return response.data;
  },
};

export default stockService;
