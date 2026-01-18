import api from './api';

const licenseService = {
  checkStatus: async () => {
    const response = await api.get('/license/status');
    return response.data;
  },
};

export default licenseService;
