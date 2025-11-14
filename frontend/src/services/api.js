import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getProducts = async () => {
  const response = await api.get('/products');
  return response.data;
};

export const getHistoricalData = async (productId, startDate = null, endDate = null) => {
  const params = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  const response = await api.get(`/historical/${productId}`, { params });
  return response.data;
};

export const runForecast = async (forecastRequest) => {
  const response = await api.post('/forecast', forecastRequest);
  return response.data;
};

export const getLatestForecast = async (productId, forecastMode = 'comprehensive', forecastHorizonDays = 30) => {
  const response = await api.get(`/forecast/${productId}`, {
    params: { forecast_mode: forecastMode, forecast_horizon_days: forecastHorizonDays },
  });
  return response.data;
};

export const getSupplyChainMetrics = async (productId) => {
  const response = await api.get(`/supply-chain/${productId}`);
  return response.data;
};

export const getScenarios = async (productId) => {
  const response = await api.get(`/scenarios/${productId}`);
  return response.data;
};

export const getAllProductsStatus = async () => {
  const response = await api.get('/products/status');
  return response.data;
};

export const getProductStatus = async (productCode) => {
  const response = await api.get(`/products/${productCode}/status`);
  return response.data;
};

