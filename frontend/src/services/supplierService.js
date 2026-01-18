import api from './api';

export const supplierService = {
  /**
   * Get paginated list of suppliers
   */
  async getSuppliers(params = {}) {
    const { page = 1, pageSize = 50 } = params;
    
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const response = await api.get(`/suppliers?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Get a single supplier by ID
   */
  async getSupplier(id) {
    const response = await api.get(`/suppliers/${id}`);
    return response.data;
  },

  /**
   * Create a new supplier
   */
  async createSupplier(data) {
    const response = await api.post('/suppliers', data);
    return response.data;
  },

  /**
   * Update an existing supplier
   */
  async updateSupplier(id, data) {
    const response = await api.put(`/suppliers/${id}`, data);
    return response.data;
  },

  /**
   * Delete a supplier
   */
  async deleteSupplier(id) {
    await api.delete(`/suppliers/${id}`);
  },
};

export default supplierService;
