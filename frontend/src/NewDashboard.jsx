import React, { useState, useEffect } from 'react';
import Header from './components/NewDashboard/Header';
import KPIOverview from './components/NewDashboard/KPIOverview';
import ForecastVisualization from './components/NewDashboard/ForecastVisualization';
import RiskIntelligence from './components/NewDashboard/RiskIntelligence';
import ActionRecommendations from './components/NewDashboard/ActionRecommendations';
import { mockData } from './data/mockData';
import { 
  useForecastData, 
  useActionRecommendations, 
  useRiskNews 
} from './hooks/useDashboardData';
import './components/NewDashboard/NewDashboard.css';

function NewDashboard() {
  const [filters, setFilters] = useState({
    timeRange: '90d',
    products: [],
    regions: [],
    searchQuery: ''
  });

  const [riskFilters, setRiskFilters] = useState({
    days: 30,
    riskThreshold: 50
  });

  // Fetch real data from backend APIs (Phase 1 Integration)
  const { 
    data: forecastData, 
    loading: forecastLoading, 
    error: forecastError,
    refetch: refetchForecast
  } = useForecastData({
    category: filters.products.length > 0 ? filters.products[0] : null,
    limit: 10
  });

  const { 
    data: actionsData, 
    loading: actionsLoading, 
    error: actionsError,
    refetch: refetchActions
  } = useActionRecommendations({
    priority: null,
    limit: 6
  });

  const { 
    data: riskNewsData, 
    loading: riskLoading, 
    error: riskError,
    refetch: refetchRisks
  } = useRiskNews(riskFilters);

  // Use mock data as fallback if API fails or data not loaded yet
  const forecast = forecastData || mockData.forecast;
  const actions = actionsData || mockData.actions;
  const newsRisks = riskNewsData || mockData.newsRisks;

  console.log('[NewDashboard] Data sources:', {
    forecastSource: forecastData ? '✅ API' : '⚠️ Mock',
    actionsSource: actionsData ? '✅ API' : '⚠️ Mock',
    newsSource: riskNewsData ? '✅ API' : '⚠️ Mock',
    forecastLoading,
    actionsLoading,
    riskLoading,
    forecastTimeSeries: forecast?.timeSeries?.length || 0,
    forecastTimeSeriesSample: forecast?.timeSeries?.[0]
  });

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };

  // Manual refresh all data
  const handleRefresh = () => {
    console.log('[NewDashboard] Refreshing all data...');
    refetchForecast();
    refetchActions();
    refetchRisks();
  };

  const handleActionUpdate = (actionId, status) => {
    // TODO: Update action via API
    console.log('[NewDashboard] Action updated:', actionId, status);
    refetchActions();
  };

  const handleRiskFilterChange = (newFilters) => {
    console.log('[NewDashboard] Risk filters changed:', newFilters);
    setRiskFilters({ ...riskFilters, ...newFilters });
  };

  return (
    <div className="new-dashboard">
      {/* HEADER - Global Control Center */}
      <Header
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
        categories={mockData.categories}
        regions={mockData.regions}
      />

      <div className="dashboard-content">
        {/* TIER 1 - KPI Overview (Still using mock data - Phase 2) */}
        <section className="tier-1">
          <KPIOverview 
            kpiData={mockData.kpis}
            loading={false}
          />
        </section>

        {/* TIER 2 - Demand Forecasting Visualization (Now using API ✅) */}
        <section className="tier-2">
          <ForecastVisualization 
            forecastData={forecast}
            loading={forecastLoading}
            error={forecastError}
          />
        </section>

        {/* TIER 3 - Risk & News Intelligence (Now using API ✅) */}
        <section className="tier-3">
          <RiskIntelligence 
            newsRisks={newsRisks}
            loading={riskLoading}
            error={riskError}
            onFilterChange={handleRiskFilterChange}
          />
        </section>

        {/* TIER 4 - Action Recommendations (Now using API ✅) */}
        <section className="tier-4">
          <ActionRecommendations
            actions={actions}
            loading={actionsLoading}
            error={actionsError}
            onActionUpdate={handleActionUpdate}
          />
        </section>
      </div>
    </div>
  );
}

export default NewDashboard;
