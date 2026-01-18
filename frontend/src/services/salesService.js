import api from './api';

const salesService = {
  // Existing methods...
  getSalesHistory: async (params) => {
    const response = await api.get('/sales/history', { params });
    return response.data;
  },

  downloadInvoice: async (saleId) => {
    const response = await api.get(`/sales/${saleId}/invoice`, {
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `invoice-${saleId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  createSale: async (saleData) => {
    const response = await api.post('/sales/create', saleData);
    return response.data;
  },

  getMedicineSalesStats: async (params) => {
    // Filter out empty values
    const cleanParams = {};
    if (params.startDate) cleanParams.startDate = params.startDate;
    if (params.endDate) cleanParams.endDate = params.endDate;
    
    const response = await api.get('/sales/medicine-stats', { params: cleanParams });
    return response.data;
  },

  cancelSale: async (saleId) => {
    const response = await api.post(`/sales/${saleId}/cancel`);
    return response.data;
  },
};

export default salesService;
