// components/AppSidebar.jsx
import React from 'react';

/**
 * Sidebar điều hướng 4 mục chính:
 * - Overview
 * - Demand Forecast
 * - Risk & News
 * - Action Board
 */
const sections = [
  {
    id: 'overview',
    label: 'Overview',
    icon: 'fas fa-chart-pie',
    description: 'KPI & coverage snapshot'
  },
  {
    id: 'forecast',
    label: 'Demand Forecast',
    icon: 'fas fa-chart-line',
    description: 'Time-series & scenarios'
  },
  {
    id: 'risks',
    label: 'Risk & News',
    icon: 'fas fa-exclamation-triangle',
    description: 'Market & supply signals'
  },
  {
    id: 'actions',
    label: 'Action Board',
    icon: 'fas fa-tasks',
    description: 'Playbook & owner status'
  }
];

const AppSidebar = ({ activeSection, onSectionChange, isOpen }) => {
  const handleClick = (id) => {
    onSectionChange(id);
  };

  return (
    <aside
      className={`sidebar bg-white border-end ${isOpen ? 'open' : ''}`}
      id="sidebar"
    >
      <div className="p-3">
        {/* Nav Group: Dashboard */}
        <div className="nav-group">
          <div className="nav-group-header">
            <i className="fas fa-tachometer-alt" />
            <span>MVP Navigation Bar</span>
          </div>
          <div className="nav-group-content">
            {sections.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`nav-link ${
                  activeSection === s.id ? 'active' : ''
                }`}
                onClick={() => handleClick(s.id)}
              >
                <i className={s.icon} />
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* (Optional) You can add more nav-groups here later:
            Forecast / Planning / Data & Models... */}
      </div>
    </aside>
  );
};

export default AppSidebar;
