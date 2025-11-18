import React, { useState } from 'react';
import './ActionCard.css';

const ActionCard = ({ action, onAssign, onStatusUpdate, onViewDetails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAssignMenu, setShowAssignMenu] = useState(false);

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

  const getStatusInfo = (status) => {
    const statusMap = {
      pending: { label: 'Chờ xử lý', color: '#6b7280', icon: '⏳' },
      in_progress: { label: 'Đang thực hiện', color: '#3b82f6', icon: '🔄' },
      completed: { label: 'Hoàn thành', color: '#10b981', icon: '✅' },
      snoozed: { label: 'Tạm hoãn', color: '#9ca3af', icon: '💤' },
      cancelled: { label: 'Đã hủy', color: '#ef4444', icon: '❌' }
    };
    return statusMap[status] || statusMap.pending;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Chưa đặt';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return `⏰ Quá ${Math.abs(diffDays)} ngày`;
    if (diffDays === 0) return '⏰ Hôm nay';
    if (diffDays === 1) return '⏰ Ngày mai';
    if (diffDays < 7) return `⏰ ${diffDays} ngày nữa`;
    return `⏰ ${date.toLocaleDateString('vi-VN')}`;
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return '#10b981';
    if (progress >= 50) return '#3b82f6';
    if (progress >= 25) return '#f59e0b';
    return '#6b7280';
  };

  const handleStatusChange = (newStatus) => {
    if (onStatusUpdate) {
      onStatusUpdate(action.id, newStatus);
    }
  };

  const handleAssignClick = () => {
    if (onAssign) {
      onAssign(action);
    }
  };

  const statusInfo = getStatusInfo(action.status);
  const isOverdue = action.due_date && new Date(action.due_date) < new Date() && action.status !== 'completed';

  return (
    <div 
      className={`action-card ${isExpanded ? 'expanded' : ''} ${isOverdue ? 'overdue' : ''}`}
      style={{ borderLeftColor: getPriorityColor(action.priority) }}
    >
      {/* Header */}
      <div className="action-card-header">
        <div className="action-title-section">
          <div className="action-title-row">
            <span className="action-icon">{statusInfo.icon}</span>
            <h3 className="action-title">{action.title}</h3>
          </div>
          <div className="action-meta">
            <span 
              className="priority-badge"
              style={{ backgroundColor: getPriorityColor(action.priority) }}
            >
              {getPriorityLabel(action.priority)}
            </span>
            <span className="category-badge">{action.category}</span>
            {action.confidence_score && (
              <span className="confidence-badge" title="Độ tin cậy">
                📊 {Math.round(action.confidence_score)}%
              </span>
            )}
          </div>
        </div>
        <button 
          className="expand-button"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label={isExpanded ? 'Thu gọn' : 'Mở rộng'}
        >
          {isExpanded ? '▲' : '▼'}
        </button>
      </div>

      {/* Description */}
      <p className="action-description">{action.description}</p>

      {/* Status and Progress Bar */}
      <div className="action-status-section">
        <div className="status-row">
          <span 
            className="status-badge"
            style={{ backgroundColor: statusInfo.color }}
          >
            {statusInfo.label}
          </span>
          <span className="progress-text">{action.progress_percent || 0}%</span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ 
              width: `${action.progress_percent || 0}%`,
              backgroundColor: getProgressColor(action.progress_percent || 0)
            }}
          />
        </div>
      </div>

      {/* Assignment Info */}
      <div className="action-assignment">
        {action.assigned_team ? (
          <div className="assignment-info">
            <span className="assignment-icon">👥</span>
            <div className="assignment-details">
              <span className="team-name">{action.assigned_team}</span>
              {action.assigned_to && (
                <span className="assignee-name">• {action.assigned_to}</span>
              )}
            </div>
          </div>
        ) : (
          <button className="assign-button" onClick={handleAssignClick}>
            <span className="assign-icon">➕</span>
            Phân công nhiệm vụ
          </button>
        )}
        {action.due_date && (
          <span className={`due-date ${isOverdue ? 'overdue' : ''}`}>
            {formatDate(action.due_date)}
          </span>
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="action-expanded-content">
          {/* Impact & Expected Result */}
          {(action.impact || action.expected_impact) && (
            <div className="action-section">
              <h4>💡 Tác động dự kiến</h4>
              <p>{action.expected_impact || action.impact}</p>
            </div>
          )}

          {/* Action Items Checklist */}
          {action.action_items && Array.isArray(action.action_items) && action.action_items.length > 0 && (
            <div className="action-section">
              <h4>📋 Các bước thực hiện</h4>
              <ul className="action-checklist">
                {action.action_items.map((item, idx) => (
                  <li key={idx} className="checklist-item">
                    <input 
                      type="checkbox" 
                      id={`item-${action.id}-${idx}`}
                      disabled={action.status === 'completed'}
                    />
                    <label htmlFor={`item-${action.id}-${idx}`}>{item}</label>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Affected Products */}
          {action.affected_products && action.affected_products.length > 0 && (
            <div className="action-section">
              <h4>📦 Sản phẩm liên quan</h4>
              <div className="product-tags">
                {action.affected_products.map((product, idx) => (
                  <span key={idx} className="product-tag">{product}</span>
                ))}
              </div>
            </div>
          )}

          {/* Cost & Deadline */}
          <div className="action-section action-details-grid">
            {action.estimated_cost && (
              <div className="detail-item">
                <span className="detail-label">💰 Chi phí ước tính:</span>
                <span className="detail-value">
                  {new Intl.NumberFormat('vi-VN', { 
                    style: 'currency', 
                    currency: 'USD' 
                  }).format(action.estimated_cost)}
                </span>
              </div>
            )}
            {action.deadline && (
              <div className="detail-item">
                <span className="detail-label">📅 Hạn chót:</span>
                <span className="detail-value">
                  {new Date(action.deadline).toLocaleDateString('vi-VN')}
                </span>
              </div>
            )}
          </div>

          {/* Notes */}
          {action.notes && (
            <div className="action-section">
              <h4>📝 Ghi chú</h4>
              <p className="action-notes">{action.notes}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons-expanded">
            <select 
              className="status-select"
              value={action.status}
              onChange={(e) => handleStatusChange(e.target.value)}
            >
              <option value="pending">⏳ Chờ xử lý</option>
              <option value="in_progress">🔄 Đang thực hiện</option>
              <option value="completed">✅ Hoàn thành</option>
              <option value="snoozed">💤 Tạm hoãn</option>
              <option value="cancelled">❌ Hủy bỏ</option>
            </select>

            <button 
              className="btn-secondary"
              onClick={() => onViewDetails && onViewDetails(action)}
            >
              📊 Chi tiết đầy đủ
            </button>

            {!action.assigned_team && (
              <button 
                className="btn-primary"
                onClick={handleAssignClick}
              >
                👥 Phân công ngay
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionCard;
