/**
 * API Service Layer for DENSO Dashboard
 * Handles all communication with backend FastAPI server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`[API] Error fetching ${endpoint}:`, error);
    throw error;
  }
}

// ========================================
// DASHBOARD APIs (Phase 1 - Critical)
// ========================================

/**
 * Get latest forecast data for dashboard Tier 2
 */
export async function getLatestForecasts(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.productCodes?.length) {
    params.append('product_codes', filters.productCodes.join(','));
  }
  if (filters.category) {
    params.append('category', filters.category);
  }
  if (filters.limit) {
    params.append('limit', filters.limit);
  }

  const query = params.toString() ? `?${params}` : '';
  return fetchAPI(`/forecasts/latest${query}`);
}

/**
 * Get action recommendations for dashboard Tier 4
 */
export async function getActionRecommendations(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.priority) {
    params.append('priority', filters.priority);
  }
  if (filters.category) {
    params.append('category', filters.category);
  }
  if (filters.limit) {
    params.append('limit', filters.limit);
  }

  const query = params.toString() ? `?${params}` : '';
  return fetchAPI(`/actions/recommendations${query}`);
}

/**
 * Get risk intelligence and news for dashboard Tier 3
 */
export async function getRiskNews(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.days) {
    params.append('days', filters.days);
  }
  if (filters.riskThreshold) {
    params.append('risk_threshold', filters.riskThreshold);
  }
  if (filters.category) {
    params.append('category', filters.category);
  }

  const query = params.toString() ? `?${params}` : '';
  return fetchAPI(`/risks/news${query}`);
}

// ========================================
// ALERTS APIs
// ========================================

export async function getAlerts(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.since) params.append('since', filters.since);
  if (filters.severity) params.append('severity', filters.severity);
  if (filters.unreadOnly) params.append('unread_only', 'true');

  const query = params.toString() ? `?${params}` : '';
  return fetchAPI(`/alerts${query}`);
}

export async function getAlertStats() {
  return fetchAPI('/alerts/stats');
}

export async function markAlertRead(alertId, userId) {
  return fetchAPI(`/alerts/${alertId}/mark-read`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

export async function markAllAlertsRead(userId) {
  return fetchAPI('/alerts/mark-all-read', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

// ========================================
// JOBS APIs
// ========================================

export async function triggerForecastJob() {
  return fetchAPI('/jobs/forecast/trigger', { method: 'POST' });
}

export async function getJobStatus(jobId) {
  return fetchAPI(`/jobs/forecast/${jobId}`);
}

export async function cancelJob(jobId) {
  return fetchAPI(`/jobs/forecast/${jobId}/cancel`, { method: 'POST' });
}

export async function getJobStats() {
  return fetchAPI('/jobs/stats');
}

// ========================================
// LEGACY APIs (Keep for backward compatibility)
// ========================================

export const getProducts = async () => {
  return fetchAPI('/products');
};

export const getHistoricalData = async (productId, startDate = null, endDate = null) => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  const query = params.toString() ? `?${params}` : '';
  return fetchAPI(`/historical/${productId}${query}`);
};

export const runForecast = async (forecastRequest) => {
  return fetchAPI('/forecast', {
    method: 'POST',
    body: JSON.stringify(forecastRequest),
  });
};

export const getSupplyChainMetrics = async (productId) => {
  return fetchAPI(`/supply-chain/${productId}`);
};

export const getScenarios = async (productId) => {
  return fetchAPI(`/scenarios/${productId}`);
};

export const getAllProductsStatus = async () => {
  return fetchAPI('/products/status');
};

export const getProductStatus = async (productCode) => {
  return fetchAPI(`/products/${productCode}/status`);
};

// ========================================
// HEALTH CHECK
// ========================================

export async function healthCheck() {
  const response = await fetch('http://localhost:8000/health');
  return response.json();
}

// ========================================
// DEMO / MOCK APIs
// ========================================

export async function triggerDemoYokohamaAlert() {
  // Gọi tới backend mock endpoint
  return fetchAPI('/alerts/demo/yokohama-hagibis', {
    method: 'POST',
  });
}

export async function sendAssignmentEmail(payload) {
  return fetchAPI('/notifications/assignment-email', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}