import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          localStorage.setItem('access_token', response.data.access_token);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return api.request(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  refresh: () => api.post('/auth/refresh'),
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  changePassword: (passwordData) => api.put('/auth/change-password', passwordData),
};

// Products API
export const productsAPI = {
  getAll: (params = {}) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  getCategories: () => api.get('/products/categories'),
};

// Suppliers API
export const suppliersAPI = {
  getAll: () => api.get('/suppliers'),
  getById: (id) => api.get(`/suppliers/${id}`),
  create: (data) => api.post('/suppliers', data),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  contact: (id, data) => api.post(`/suppliers/${id}/contact`, data),
  getMyContacts: () => api.get('/suppliers/contacts'),
};

// Competitors API
export const competitorsAPI = {
  getAll: () => api.get('/competitors'),
  getDetails: (id) => api.get(`/competitors/${id}`),
  getProducts: (id) => api.get(`/competitors/${id}/products`),
  getSales: (id, params = {}) => api.get(`/competitors/${id}/sales`, { params }),
  getComparison: () => api.get('/competitors/comparison'),
};

// Inventory API
export const inventoryAPI = {
  getAll: (params = {}) => api.get('/inventory/items', { params }),
  getByProductId: (productId) => api.get(`/inventory/items/${productId}`),
  create: (data) => api.post('/inventory/items', data),
  update: (productId, data) => api.put(`/inventory/items/${productId}`, data),
  delete: (productId) => api.delete(`/inventory/items/${productId}`),
  adjustStock: (productId, data) => api.post(`/inventory/items/${productId}/adjust`, data),
  recordSale: (productId, data) => api.post(`/inventory/items/${productId}/sale`, data),
  getLowStock: () => api.get('/inventory/low-stock'),
  getSummary: () => api.get('/inventory/summary'),
};

// Sales API
export const salesAPI = {
  getAll: (params = {}) => api.get('/sales', { params }),
  getDailySales: () => api.get('/sales/analytics/daily'),
  getTopProducts: (params = {}) => api.get('/sales/analytics/top-products', { params }),
  getMonthlySales: () => api.get('/sales/analytics/monthly'),
};

// Alerts API
export const alertsAPI = {
  getAll: (params = {}) => api.get('/alerts', { params }),
  resolve: (id) => api.put(`/alerts/${id}/resolve`),
  checkStockLevels: () => api.post('/alerts/check-stock-levels'),
  getSummary: () => api.get('/alerts/summary'),
  create: (data) => api.post('/alerts', data),
};

// Forecast API
export const forecastAPI = {
  predict: (productId, data) => api.post(`/forecast/predict/${productId}`, data),
  getForecasts: (productId, params = {}) => api.get(`/forecast/forecast/${productId}`, { params }),
  batchPredict: (data) => api.post('/forecast/batch-predict', data),
  getAccuracy: (productId) => api.get(`/forecast/accuracy/${productId}`),
  getModelInfo: () => api.get('/forecast/model-info'),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

// Customers API
export const customersAPI = {
  getAll: (params = {}) => api.get('/customers', { params }),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post('/customers', data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  addLoyaltyPoints: (id, data) => api.post(`/customers/${id}/loyalty`, data),
  setSpecialPrice: (id, data) => api.post(`/customers/${id}/special-price`, data),
  removeSpecialPrice: (id, productId) => api.delete(`/customers/${id}/special-price/${productId}`),
  getTopCustomers: (params = {}) => api.get('/customers/top', { params }),
  getCustomerPrice: (customerId, productId) => api.get(`/customers/${customerId}/price/${productId}`),
};

// Batches API
export const batchesAPI = {
  getAll: (params = {}) => api.get('/batches', { params }),
  getById: (id) => api.get(`/batches/${id}`),
  create: (data) => api.post('/batches', data),
  update: (id, data) => api.put(`/batches/${id}`, data),
  getExpiring: (params = {}) => api.get('/batches/expiring', { params }),
  getValuation: (params = {}) => api.get('/batches/valuation', { params }),
  allocate: (data) => api.post('/batches/allocate', data),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getSalesPerformance: (params = {}) => api.get('/analytics/sales-performance', { params }),
  getInventoryValuation: () => api.get('/analytics/inventory-valuation'),
  getForecastAccuracy: (params = {}) => api.get('/analytics/forecast-accuracy', { params }),
  exportFile: async (endpoint, params = {}) => {
    try {
      const response = await api.get(`/analytics/export/${endpoint}`, { params, responseType: 'blob' });
      return response;
    } catch (error) {
      if (error.response?.status === 401) {
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw new Error('Session expired. Please login again.');
      }
      throw error;
    }
  }
};

export default api;