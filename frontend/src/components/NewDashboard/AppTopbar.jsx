// components/NewDashboard/AppTopbar.jsx
import React, { useState } from 'react';
import './Header.css';

/**
 * Topbar cho toàn bộ DENSO Forecast Suite
 * - Toggle sidebar (mobile)
 * - Search
 * - Global actions (Refresh, Dark Mode, Notifications, Demo)
 * - Role selector
 */
const AppTopbar = ({
  searchQuery,
  onSearchChange,
  onToggleSidebar,
  onRefresh,
  theme,
  onToggleTheme,
  role,
  onRoleChange,
  // callback từ NewDashboard để inject news vào Risk & News
  onDemoAlert
}) => {
  const [notificationCount, setNotificationCount] = useState(3);
  const [showNotifications, setShowNotifications] = useState(false);

  const roles = ['viewer', 'planner', 'marketing', 'manager', 'admin'];

  const handleSearchChange = (e) => {
    onSearchChange && onSearchChange(e.target.value);
  };

  const handleRoleSelect = (e) => {
    onRoleChange && onRoleChange(e.target.value);
  };

  const handleRefreshClick = () => {
    onRefresh && onRefresh();
  };

  const handleToggleTheme = () => {
    onToggleTheme && onToggleTheme();
  };

  const handleNotificationToggle = () => {
    setShowNotifications((prev) => !prev);
  };

  const handleMarkAllRead = () => {
    setNotificationCount(0);
    setShowNotifications(false);
  };

  // 🌟 Trigger demo alert: PURE MOCK, KHÔNG GỌI API
  const handleTriggerDemoAlert = () => {
    const demoAlert = {
      id: `demo-${Date.now()}`,
      title: 'Tắc nghẽn cảng Yokohama do bão Hagibis',
      message:
        'Bão Hagibis gây tắc nghẽn nghiêm trọng tại cảng Yokohama, ảnh hưởng lịch trình xuất khẩu phụ tùng ô tô.',
      severity: 'high',
      alert_type: 'logistics',
      source: 'Nikkei Asia',
      risk_score: 0.85,
      tags: ['bão', 'cảng biển', 'logistics', 'Nhật Bản'],
      created_at: new Date().toISOString(),
      read: false,
      dismissed: false
    };

    console.log('[AppTopbar] Demo alert (pure mock):', demoAlert);

    // Tăng badge
    setNotificationCount((prev) => prev + 1);

    // Mở panel
    setShowNotifications(true);

    // Báo lên parent để thêm card vào Risk & News
    if (onDemoAlert) {
      onDemoAlert(demoAlert);
    }
  };

  return (
    <nav className="topbar">
      <div className="topbar-inner">
        {/* LEFT: Logo + mobile sidebar toggle */}
        <div className="topbar-left">
          <button
            className="topbar-sidebar-toggle d-lg-none"
            id="btn-toggle-sidebar"
            type="button"
            onClick={onToggleSidebar}
          >
            <i className="fas fa-bars" />
          </button>

          <div className="topbar-brand">
            <i className="fas fa-chart-line text-primary fs-4" />
            <div className="topbar-brand-text">
              <span className="topbar-title">Denso Forecast Suite</span>
              <span className="topbar-subtitle">
                End-to-End Demand & Risk Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* CENTER: Search box */}
        <div className="topbar-center">
          <div className="search-box">
            <i className="fas fa-search" />
            <input
              type="text"
              className="search-input-inner"
              placeholder="Search SKU, region, channel..."
              value={searchQuery}
              onChange={handleSearchChange}
            />
          </div>
        </div>

        {/* RIGHT: Actions + Role */}
        <div className="topbar-right">
          {/* PILL chứa các action + logo DENSO */}
          <div className="header-actions">
            <div className="topbar-actions-pill">
              {/* Refresh */}
              <button
                className="action-button"
                title="Refresh"
                onClick={handleRefreshClick}
                type="button"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path
                    d="M14.5 4.5C13.2 3.2 11.4 2.5 9.5 2.5C5.9 2.5 3 5.4 3 9C3 12.6 5.9 15.5 9.5 15.5C12.5 15.5 15 13.4 15.4 10.6"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M12 4.5H14.5V7"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>

              {/* Dark Mode toggle – dùng emoji cho chắc ăn */}
              <button
                className="action-button"
                title="Toggle Dark Mode"
                type="button"
                onClick={handleToggleTheme}
              >
                <span className="topbar-icon-emoji">
                  {theme === 'light' ? '🌙' : '☀️'}
                </span>
              </button>

              {/* Notifications */}
              <button
                className="action-button notification-button"
                onClick={handleNotificationToggle}
                title="Notifications"
                type="button"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path
                    d="M6.5 15.5C6.5 16.6 7.4 17.5 8.5 17.5C9.6 17.5 10.5 16.6 10.5 15.5"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <path
                    d="M2.5 12.5H14.5V11.5C14.5 11.5 13.5 10.5 13.5 7.5C13.5 5.3 11.7 3.5 9.5 3.5H8.5C6.3 3.5 4.5 5.3 4.5 7.5C4.5 10.5 3.5 11.5 3.5 11.5V12.5H2.5Z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {notificationCount > 0 && (
                  <span className="notification-badge">{notificationCount}</span>
                )}
              </button>

              {/* Demo Yokohama Hagibis */}
              <button
                className="action-button"
                type="button"
                title="Trigger Yokohama Demo Alert"
                onClick={handleTriggerDemoAlert}
              >
                <span className="topbar-icon-emoji">⚡</span>
              </button>

              {/* Divider trong pill */}
              <span className="topbar-pill-divider" />

              {/* Logo DENSO */}
              <div className="denso-logo-pill">
                <span className="denso-logo-text">DENSO</span>
              </div>
            </div>
          </div>

          {/* Role Selector */}
          <div className="topbar-role-wrapper">
            <select
              className="topbar-role-select"
              id="role"
              value={role}
              onChange={handleRoleSelect}
            >
              {roles.map((r) => (
                <option key={r} value={r}>
                  {r.charAt(0).toUpperCase() + r.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Notification Panel (hiện tại vẫn mock tĩnh) */}
      {showNotifications && (
        <div className="notification-panel">
          <div className="panel-header">
            <h3>Notifications</h3>
            <button
              className="clear-button"
              onClick={handleMarkAllRead}
              type="button"
            >
              Mark all read
            </button>
          </div>
          <div className="panel-content">
            <div className="notification-item unread">
              <div className="notification-dot critical"></div>
              <div className="notification-body">
                <p className="notification-title">
                  High Risk Alert: Port congestion
                </p>
                <p className="notification-desc">
                  Yokohama delays affecting production
                </p>
                <span className="notification-time">5m ago</span>
              </div>
            </div>
            <div className="notification-item unread">
              <div className="notification-dot info"></div>
              <div className="notification-body">
                <p className="notification-title">Forecast Updated</p>
                <p className="notification-desc">
                  Q2 demand spike predicted +18%
                </p>
                <span className="notification-time">1h ago</span>
              </div>
            </div>
            <div className="notification-item">
              <div className="notification-dot success"></div>
              <div className="notification-body">
                <p className="notification-title">Action Completed</p>
                <p className="notification-desc">
                  Production schedule updated
                </p>
                <span className="notification-time">3h ago</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default AppTopbar;
