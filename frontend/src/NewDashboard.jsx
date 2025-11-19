// NewDashboard.jsx
import React, { useState, useEffect } from 'react';

// Layout components
import AppTopbar from './components/NewDashboard/AppTopbar';
import AppSidebar from './components/NewDashboard/AppSidebar';

// Existing dashboard components
import Header from './components/NewDashboard/Header';
import KPIOverview from './components/NewDashboard/KPIOverview';
import ForecastVisualization from './components/NewDashboard/ForecastVisualization';
import RiskIntelligence from './components/NewDashboard/RiskIntelligence';
import ActionRecommendations from './components/NewDashboard/ActionRecommendations';
import { sendAssignmentEmail } from './services/api';
import { mockData } from './data/mockData';
import {
  useForecastData,
  useActionRecommendations,
  useRiskNews
} from './hooks/useDashboardData';

import './components/NewDashboard/NewDashboard.css';

function NewDashboard() {
  // ====== GLOBAL FILTERS ======
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

  // ====== LAYOUT / UI STATE ======
  const [theme, setTheme] = useState('light'); // 'light' | 'dark'
  const [activeSection, setActiveSection] = useState('overview');
  // 'overview' | 'forecast' | 'risks' | 'actions'
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [role, setRole] = useState('viewer');

  // 🌟 State riêng cho Risk & News (để inject Hagibis mock)
  const [newsRisksState, setNewsRisksState] = useState(mockData.newsRisks);

  // 🌟 State cho popup đề xuất giải pháp
  const [solutionPromptOpen, setSolutionPromptOpen] = useState(false);
  const [selectedNews, setSelectedNews] = useState(null);
  const [isSuggesting, setIsSuggesting] = useState(false);

  // Apply theme to <html>
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', theme);
    }
  }, [theme]);

  // ====== DATA HOOKS ======
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

  // Nếu sau này có API thật cho riskNewsData thì sync vào state,
  // còn hiện tại vẫn pure mock: newsRisksState khởi tạo từ mockData.newsRisks
  useEffect(() => {
    if (riskNewsData) {
      setNewsRisksState(riskNewsData);
    }
  }, [riskNewsData]);

  // Fallback sang mockData nếu API chưa có hoặc lỗi
  const forecast = forecastData || mockData.forecast;
  const actions = actionsData || mockData.actions;
  const newsRisks = newsRisksState;

  console.log('[NewDashboard] Data sources:', {
    forecastSource: forecastData ? '✅ API' : '⚠️ Mock',
    actionsSource: actionsData ? '✅ API' : '⚠️ Mock',
    newsSource: riskNewsData ? '✅ API' : '⚠️ Mock (state from mockData)',
    forecastLoading,
    actionsLoading,
    riskLoading,
    forecastTimeSeries: forecast?.timeSeries?.length || 0,
    forecastTimeSeriesSample: forecast?.timeSeries?.[0]
  });

  // ====== HANDLERS ======

  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleSearchChange = (searchQuery) => {
    setFilters((prev) => ({ ...prev, searchQuery }));
  };

  const handleRiskFilterChange = (newFilters) => {
    console.log('[NewDashboard] Risk filters changed:', newFilters);
    setRiskFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleRefreshAll = () => {
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

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const handleToggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  const handleSectionChange = (sectionId) => {
    setActiveSection(sectionId);
    // Close sidebar on mobile after navigation
    setIsSidebarOpen(false);
    // Scroll to top for better UX
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    console.log('[NewDashboard] Role changed to:', newRole);
  };

  // 🌟 Khi Topbar trigger demo alert → thêm news Hagibis vào Risk & News
  const handleDemoAlert = (alert) => {
    console.log('[NewDashboard] handleDemoAlert got:', alert);

    // Auto switch qua tab Risk & News
    setActiveSection('risks');

    setNewsRisksState((prev) => {
      const baseItem =
        prev && prev.news && prev.news.length > 0 ? prev.news[0] : {};

      const riskScorePercent =
        alert.risk_score != null
          ? Math.round(alert.risk_score * 100)
          : baseItem.riskScore ?? baseItem.risk_score ?? 85;

      const hagibisNews = {
        // clone mọi field đang có để giữ đúng structure
        ...baseItem,
        id: `demo-hagibis-${Date.now()}`,
        title:
          alert.title ||
          'Tắc nghẽn cảng Yokohama do bão Hagibis',
        summary:
          alert.message ||
          'Bão Hagibis gây tắc nghẽn nghiêm trọng tại cảng Yokohama, ảnh hưởng lịch trình xuất khẩu phụ tùng ô tô.',
        source: alert.source || baseItem.source || 'Nikkei Asia',
        date: alert.created_at || new Date().toISOString(),

        // cả hai kiểu tên để chắc cú (camelCase + snake_case)
        riskScore: riskScorePercent,
        risk_score: riskScorePercent,

        category: 'logistics',
        category_name: baseItem.category_name || 'Logistics',
        tags: ['bão', 'cảng biển', 'logistics', 'Nhật Bản']
      };

      return {
        ...prev,
        news: [hagibisNews, ...(prev.news || [])]
      };
    });
  };

  // 🌟 Khi user click vào 1 news card (Hagibis hoặc news khác)
  const handleNewsClick = (newsItem) => {
    console.log('[NewDashboard] News clicked:', newsItem);
    setSelectedNews(newsItem);
    setSolutionPromptOpen(true);
  };
const ownerEmail = 'phuoc.dang2104@gmail.com';
const ownerName = 'DENSO ADMIN';
  const handleConfirmSolution = async () => {
  setIsSuggesting(true);

  try {
    await sendAssignmentEmail({
      to_email: 'phuoc.dang2104@gmail.com',         // gmail thật để test
      assignee_name: 'GMAIL_TEST_DENSO',
      risk_title: selectedNews?.title || 'Rủi ro chưa đặt tên',
    });
    console.log('[NewDashboard] Assignment email sent!');
  } catch (err) {
    console.error('[NewDashboard] Failed to send assignment email:', err);
  }

  setTimeout(() => {
    setIsSuggesting(false);
    setSolutionPromptOpen(false);
    setSelectedNews(null);
    setActiveSection('actions');
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, 800);
};

  const handleCancelSolution = () => {
    setSolutionPromptOpen(false);
    setSelectedNews(null);
  };

  const shouldShowHeader =
    activeSection === 'overview' || activeSection === 'forecast';

  return (
    <div className="new-dashboard">
      {/* TOPBAR: Global controls, search, dark mode, notifications */}
      <AppTopbar
        searchQuery={filters.searchQuery}
        onSearchChange={handleSearchChange}
        onToggleSidebar={handleToggleSidebar}
        onRefresh={handleRefreshAll}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        role={role}
        onRoleChange={handleRoleChange}
        // 🌟 callback mock demo alert
        onDemoAlert={handleDemoAlert}
      />

      {/* APP WRAPPER: Sidebar + Main content */}
      <div className="app-wrap">
        <AppSidebar
          activeSection={activeSection}
          onSectionChange={handleSectionChange}
          isOpen={isSidebarOpen}
        />

        <main className="main" id="main">
          {/* Page-level header: chỉ hiện ở Overview & Forecast */}
          {shouldShowHeader && (
            <Header
              filters={filters}
              onFilterChange={handleFilterChange}
              onRefresh={handleRefreshAll}
              categories={mockData.categories}
              regions={mockData.regions}
            />
          )}

          <div className="dashboard-content">
            {/* ====== SECTION: KPI OVERVIEW ====== */}
            {activeSection === 'overview' && (
              <section className="tier-1 fade-in">
                <KPIOverview kpiData={mockData.kpis} loading={false} />
              </section>
            )}

            {/* ====== SECTION: DEMAND FORECAST ====== */}
            {activeSection === 'forecast' && (
              <section className="tier-2 fade-in">
                <ForecastVisualization
                  forecastData={forecast}
                  loading={forecastLoading}
                  error={forecastError}
                />
              </section>
            )}

            {/* ====== SECTION: RISK & NEWS INTELLIGENCE ====== */}
            {activeSection === 'risks' && (
              <section className="tier-3 fade-in">
                <RiskIntelligence
                  newsRisks={newsRisks}
                  loading={riskLoading}
                  error={riskError}
                  onFilterChange={handleRiskFilterChange}
                  // 🌟 callback: click vào 1 news để mở popup đề xuất
                  onNewsClick={handleNewsClick}
                />
              </section>
            )}

            {/* ====== SECTION: ACTION RECOMMENDATIONS ====== */}
            {activeSection === 'actions' && (
              <section className="tier-4 fade-in">
                <ActionRecommendations
                  actions={actions}
                  loading={actionsLoading}
                  error={actionsError}
                  onActionUpdate={handleActionUpdate}
                />
              </section>
            )}
          </div>

          {/* 🌟 Modal hỏi có muốn đề xuất giải pháp không */}
          {solutionPromptOpen && (
            <div className="solution-modal-overlay">
              <div className="solution-modal">
                {!isSuggesting ? (
                  <>
                    <h3>Đề xuất giải pháp cho rủi ro này?</h3>
                    <p>
                      {selectedNews?.title
                        ? `Rủi ro: ${selectedNews.title}`
                        : 'Bạn có muốn để hệ thống đề xuất giải pháp hành động cho rủi ro này không?'}
                    </p>
                    <div className="solution-modal-actions">
                      <button
                        type="button"
                        className="btn-secondary"
                        onClick={handleCancelSolution}
                      >
                        Để sau
                      </button>
                      <button
                        type="button"
                        className="btn-primary"
                        onClick={handleConfirmSolution}
                      >
                        Có, xem đề xuất
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="solution-modal-loading">
                    <div className="spinner" />
                    <p>Đang phân tích & đề xuất hành động...</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default NewDashboard;
