import React, { useState, useEffect } from 'react';
import './ActionProgressTracker.css';

const ActionProgressTracker = ({ actions, onFilterChange }) => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    in_progress: 0,
    completed: 0,
    overdue: 0
  });

  useEffect(() => {
    if (actions && Array.isArray(actions)) {
      const now = new Date();
      const calculated = {
        total: actions.length,
        pending: actions.filter(a => a.status === 'pending').length,
        in_progress: actions.filter(a => a.status === 'in_progress').length,
        completed: actions.filter(a => a.status === 'completed').length,
        overdue: actions.filter(a => 
          a.due_date && 
          new Date(a.due_date) < now && 
          a.status !== 'completed'
        ).length
      };
      setStats(calculated);
    }
  }, [actions]);

  const handleFilterClick = (filter) => {
    setActiveFilter(filter);
    if (onFilterChange) {
      onFilterChange(filter);
    }
  };

  const getCompletionRate = () => {
    if (stats.total === 0) return 0;
    return Math.round((stats.completed / stats.total) * 100);
  };

  const getProgressColor = (percent) => {
    if (percent >= 75) return '#10b981';
    if (percent >= 50) return '#3b82f6';
    if (percent >= 25) return '#f59e0b';
    return '#ef4444';
  };

  const completionRate = getCompletionRate();

  return (
    <div className="action-progress-tracker">
      {/* Summary Cards */}
      <div className="progress-summary">
        <div className="summary-card total">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <div className="card-value">{stats.total}</div>
            <div className="card-label">Tổng hành động</div>
          </div>
        </div>

        <div 
          className={`summary-card pending ${activeFilter === 'pending' ? 'active' : ''}`}
          onClick={() => handleFilterClick('pending')}
        >
          <div className="card-icon">⏳</div>
          <div className="card-content">
            <div className="card-value">{stats.pending}</div>
            <div className="card-label">Chờ xử lý</div>
          </div>
        </div>

        <div 
          className={`summary-card in-progress ${activeFilter === 'in_progress' ? 'active' : ''}`}
          onClick={() => handleFilterClick('in_progress')}
        >
          <div className="card-icon">🔄</div>
          <div className="card-content">
            <div className="card-value">{stats.in_progress}</div>
            <div className="card-label">Đang thực hiện</div>
          </div>
        </div>

        <div 
          className={`summary-card completed ${activeFilter === 'completed' ? 'active' : ''}`}
          onClick={() => handleFilterClick('completed')}
        >
          <div className="card-icon">✅</div>
          <div className="card-content">
            <div className="card-value">{stats.completed}</div>
            <div className="card-label">Hoàn thành</div>
          </div>
        </div>

        {stats.overdue > 0 && (
          <div 
            className={`summary-card overdue ${activeFilter === 'overdue' ? 'active' : ''}`}
            onClick={() => handleFilterClick('overdue')}
          >
            <div className="card-icon">⚠️</div>
            <div className="card-content">
              <div className="card-value">{stats.overdue}</div>
              <div className="card-label">Quá hạn</div>
            </div>
          </div>
        )}
      </div>

      {/* Overall Progress */}
      <div className="overall-progress-section">
        <div className="progress-header">
          <h3>🎯 Tiến độ tổng thể</h3>
          <button 
            className="view-all-button"
            onClick={() => handleFilterClick('all')}
          >
            Xem tất cả
          </button>
        </div>
        
        <div className="progress-visualization">
          <div className="progress-circle-container">
            <svg className="progress-circle" viewBox="0 0 120 120">
              <circle
                className="progress-circle-bg"
                cx="60"
                cy="60"
                r="54"
              />
              <circle
                className="progress-circle-fill"
                cx="60"
                cy="60"
                r="54"
                style={{
                  strokeDashoffset: 339.292 * (1 - completionRate / 100),
                  stroke: getProgressColor(completionRate)
                }}
              />
            </svg>
            <div className="progress-circle-text">
              <div className="progress-percent">{completionRate}%</div>
              <div className="progress-label">Hoàn thành</div>
            </div>
          </div>

          <div className="progress-breakdown">
            <div className="breakdown-item">
              <div className="breakdown-bar">
                <div 
                  className="breakdown-fill completed"
                  style={{ width: `${(stats.completed / stats.total) * 100}%` }}
                />
              </div>
              <div className="breakdown-label">
                <span className="breakdown-dot completed"></span>
                Hoàn thành: {stats.completed}
              </div>
            </div>

            <div className="breakdown-item">
              <div className="breakdown-bar">
                <div 
                  className="breakdown-fill in-progress"
                  style={{ width: `${(stats.in_progress / stats.total) * 100}%` }}
                />
              </div>
              <div className="breakdown-label">
                <span className="breakdown-dot in-progress"></span>
                Đang thực hiện: {stats.in_progress}
              </div>
            </div>

            <div className="breakdown-item">
              <div className="breakdown-bar">
                <div 
                  className="breakdown-fill pending"
                  style={{ width: `${(stats.pending / stats.total) * 100}%` }}
                />
              </div>
              <div className="breakdown-label">
                <span className="breakdown-dot pending"></span>
                Chờ xử lý: {stats.pending}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Pipeline */}
      <div className="status-pipeline">
        <h3>🔄 Quy trình xử lý</h3>
        <div className="pipeline-flow">
          <div className="pipeline-stage">
            <div className="stage-badge pending">⏳</div>
            <div className="stage-label">Chờ xử lý</div>
            <div className="stage-count">{stats.pending}</div>
          </div>

          <div className="pipeline-arrow">→</div>

          <div className="pipeline-stage">
            <div className="stage-badge in-progress">🔄</div>
            <div className="stage-label">Đang thực hiện</div>
            <div className="stage-count">{stats.in_progress}</div>
          </div>

          <div className="pipeline-arrow">→</div>

          <div className="pipeline-stage">
            <div className="stage-badge completed">✅</div>
            <div className="stage-label">Hoàn thành</div>
            <div className="stage-count">{stats.completed}</div>
          </div>
        </div>
      </div>

      {/* Team Performance (if actions have team data) */}
      {actions && actions.some(a => a.assigned_team) && (
        <div className="team-performance">
          <h3>👥 Hiệu suất theo Team</h3>
          <TeamPerformanceChart actions={actions} />
        </div>
      )}
    </div>
  );
};

// Sub-component for team performance
const TeamPerformanceChart = ({ actions }) => {
  const [teamStats, setTeamStats] = useState([]);

  useEffect(() => {
    const teams = {};
    
    actions.forEach(action => {
      if (action.assigned_team) {
        if (!teams[action.assigned_team]) {
          teams[action.assigned_team] = {
            name: action.assigned_team,
            total: 0,
            completed: 0,
            in_progress: 0,
            pending: 0,
            avg_progress: 0
          };
        }
        
        teams[action.assigned_team].total++;
        
        if (action.status === 'completed') teams[action.assigned_team].completed++;
        else if (action.status === 'in_progress') teams[action.assigned_team].in_progress++;
        else if (action.status === 'pending') teams[action.assigned_team].pending++;
      }
    });

    const stats = Object.values(teams).map(team => ({
      ...team,
      completion_rate: team.total > 0 ? Math.round((team.completed / team.total) * 100) : 0
    })).sort((a, b) => b.completion_rate - a.completion_rate);

    setTeamStats(stats);
  }, [actions]);

  return (
    <div className="team-chart">
      {teamStats.map((team, idx) => (
        <div key={idx} className="team-bar-container">
          <div className="team-bar-header">
            <span className="team-bar-name">{team.name}</span>
            <span className="team-bar-rate">{team.completion_rate}%</span>
          </div>
          <div className="team-bar">
            <div 
              className="team-bar-fill completed"
              style={{ width: `${(team.completed / team.total) * 100}%` }}
              title={`Hoàn thành: ${team.completed}`}
            />
            <div 
              className="team-bar-fill in-progress"
              style={{ width: `${(team.in_progress / team.total) * 100}%` }}
              title={`Đang thực hiện: ${team.in_progress}`}
            />
            <div 
              className="team-bar-fill pending"
              style={{ width: `${(team.pending / team.total) * 100}%` }}
              title={`Chờ xử lý: ${team.pending}`}
            />
          </div>
          <div className="team-bar-stats">
            <span>✅ {team.completed}</span>
            <span>🔄 {team.in_progress}</span>
            <span>⏳ {team.pending}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActionProgressTracker;
