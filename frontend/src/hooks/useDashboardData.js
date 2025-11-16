/**
 * Custom React hooks for dashboard data fetching
 * Handles API calls with loading and error states
 */

import { useState, useEffect } from 'react';
import * as api from '../services/api';

/**
 * Hook to fetch forecast data with automatic refetch on filter changes
 * @param {Object} filters - Filter options for forecast API
 * @returns {Object} { data, loading, error, refetch }
 */
export function useForecastData(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getLatestForecasts(filters);
      setData(result);
    } catch (err) {
      console.error('[useForecastData] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [JSON.stringify(filters)]); // Re-fetch when filters change

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * Hook to fetch action recommendations
 * @param {Object} filters - Filter options for actions API
 * @returns {Object} { data, loading, error, refetch }
 */
export function useActionRecommendations(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getActionRecommendations(filters);
      setData(result);
    } catch (err) {
      console.error('[useActionRecommendations] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [JSON.stringify(filters)]);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * Hook to fetch risk news and intelligence
 * @param {Object} filters - Filter options for risk API
 * @returns {Object} { data, loading, error, refetch }
 */
export function useRiskNews(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getRiskNews(filters);
      setData(result);
    } catch (err) {
      console.error('[useRiskNews] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [JSON.stringify(filters)]);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * Hook to fetch alerts
 * @param {Object} filters - Filter options for alerts API
 * @returns {Object} { data, loading, error, refetch }
 */
export function useAlerts(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getAlerts(filters);
      setData(result);
    } catch (err) {
      console.error('[useAlerts] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [JSON.stringify(filters)]);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * Hook to fetch alert statistics
 * @returns {Object} { data, loading, error, refetch }
 */
export function useAlertStats() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getAlertStats();
      setData(result);
    } catch (err) {
      console.error('[useAlertStats] Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { 
    data, 
    loading, 
    error, 
    refetch: fetchData 
  };
}

/**
 * Hook for polling job status
 * @param {string} jobId - Job ID to monitor
 * @param {number} interval - Polling interval in ms (default 2000)
 * @returns {Object} { data, loading, error, stopPolling }
 */
export function useJobStatus(jobId, interval = 2000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!jobId || !polling) return;

    const fetchStatus = async () => {
      try {
        const result = await api.getJobStatus(jobId);
        setData(result);
        setError(null);
        
        // Stop polling if job is complete or failed
        if (result.status === 'completed' || result.status === 'failed') {
          setPolling(false);
        }
      } catch (err) {
        console.error('[useJobStatus] Error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus(); // Initial fetch
    const intervalId = setInterval(fetchStatus, interval);

    return () => clearInterval(intervalId);
  }, [jobId, interval, polling]);

  return { 
    data, 
    loading, 
    error, 
    stopPolling: () => setPolling(false) 
  };
}
