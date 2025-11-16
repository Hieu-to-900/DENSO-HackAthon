import React, { useState } from 'react';
import './ActionRecommendations.css';
import './LoadingStates.css';

const ActionRecommendations = ({ actions, loading, error, onActionUpdate }) => {
  const [filter, setFilter] = useState('all'); // all, high, medium, low

  // Loading state
  if (loading) {
    return (
      <div className="action-recommendations loading-state">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Đang tải khuyến nghị hành động...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="action-recommendations error-state">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <h3>Không thể tải khuyến nghị</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  // Add defensive check
  if (!actions || !Array.isArray(actions)) {
    console.error('[ActionRecommendations] Invalid actions prop:', actions);
    return (
      <div className="action-recommendations">
        <div className="action-header">
          <h2>Hành động được khuyến nghị</h2>
        </div>
        <div className="empty-state">
          <span className="empty-icon">⚠️</span>
          <p>Không có dữ liệu hành động</p>
        </div>
      </div>
    );
  }

  const getPriorityColor = (priority) => {
    const colors = {
      high: '#ef4444',
      medium: '#f59e0b',
      low: '#3b82f6'
    };
    return colors[priority] || '#6b7280';
  };

  const getPriorityLabel = (priority) => {
    const labels = {
      high: 'Ưu tiên cao',
      medium: 'Ưu tiên trung bình',
      low: 'Ưu tiên thấp'
    };
    return labels[priority] || priority;
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      critical: '🚨',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[severity] || '📋';
  };

  const formatDeadline = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return '⏰ Quá hạn';
    if (diffDays === 0) return '⏰ Hôm nay';
    if (diffDays === 1) return '⏰ Ngày mai';
    if (diffDays < 7) return `⏰ ${diffDays} ngày`;
    return `⏰ ${date.toLocaleDateString('vi-VN')}`;
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: { label: 'Chờ xử lý', color: '#6b7280' },
      in_progress: { label: 'Đang thực hiện', color: '#3b82f6' },
      completed: { label: 'Hoàn thành', color: '#10b981' },
      blocked: { label: 'Bị chặn', color: '#ef4444' }
    };
    return badges[status] || badges.pending;
  };

  const filteredActions = filter === 'all' 
    ? actions 
    : actions.filter(action => action.priority === filter);

  const handleStatusChange = (actionId, newStatus) => {
    if (onActionUpdate) {
      onActionUpdate(actionId, { status: newStatus });
    }
  };

  return (
    <div className="action-recommendations">
      <div className="action-header">
        <h2>Hành động được khuyến nghị</h2>
        <div className="action-filters">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            Tất cả ({actions.length})
          </button>
          <button
            className={filter === 'high' ? 'active' : ''}
            onClick={() => setFilter('high')}
          >
            🔴 Cao ({actions.filter(a => a.priority === 'high').length})
          </button>
          <button
            className={filter === 'medium' ? 'active' : ''}
            onClick={() => setFilter('medium')}
          >
            🟡 Trung bình ({actions.filter(a => a.priority === 'medium').length})
          </button>
          <button
            className={filter === 'low' ? 'active' : ''}
            onClick={() => setFilter('low')}
          >
            🔵 Thấp ({actions.filter(a => a.priority === 'low').length})
          </button>
        </div>
      </div>

      <div className="actions-grid">
        {filteredActions.map((action) => (
          <div
            key={action.id}
            className="action-card"
            style={{ borderLeftColor: getPriorityColor(action.priority) }}
          >
            <div className="action-card-header">
              <div className="action-title-row">
                <span className="action-severity">{getSeverityIcon(action.severity)}</span>
                <h3 className="action-title">{action.title}</h3>
              </div>
              <span
                className="priority-badge"
                style={{ backgroundColor: getPriorityColor(action.priority) }}
              >
                {getPriorityLabel(action.priority)}
              </span>
            </div>

            <p className="action-description">{action.description}</p>

            <div className="action-impact">
              <div className="impact-item">
                <span className="impact-label">Tác động dự kiến:</span>
                <span className="impact-value">{action.estimated_impact}</span>
              </div>
              <div className="impact-item">
                <span className="impact-label">Hạn chót:</span>
                <span className="impact-deadline">{formatDeadline(action.deadline)}</span>
              </div>
            </div>

            {action.affectedProducts && action.affectedProducts.length > 0 && (
              <div className="affected-products">
                <span className="affected-label">Sản phẩm liên quan:</span>
                <div className="product-tags">
                  {action.affectedProducts.map((product, idx) => (
                    <span key={idx} className="product-tag">
                      {product}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="action-items">
              <span className="action-items-label">Các bước thực hiện:</span>
              <ul className="action-list">
                {action.actionItems && action.actionItems.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="action-footer">
              <div className="action-status">
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusBadge(action.status).color }}
                >
                  {getStatusBadge(action.status).label}
                </span>
              </div>
              <div className="action-buttons">
                <button
                  className="btn-secondary"
                  onClick={() => alert(`Xem chi tiết: ${action.title}`)}
                >
                  Chi tiết
                </button>
                <button
                  className="btn-primary"
                  onClick={() => handleStatusChange(action.id, 'in_progress')}
                  disabled={action.status === 'completed'}
                >
                  {action.status === 'completed' ? '✓ Đã xong' : 'Bắt đầu'}
                </button>
              </div>
            </div>

            {action.riskIfIgnored && (
              <div className="risk-warning">
                <span className="warning-icon">⚠️</span>
                <span className="warning-text">
                  Rủi ro nếu bỏ qua: {action.riskIfIgnored}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredActions.length === 0 && (
        <div className="empty-state">
          <span className="empty-icon">✅</span>
          <p>Không có hành động nào với mức ưu tiên này</p>
        </div>
      )}
    </div>
  );
};

export default ActionRecommendations;
