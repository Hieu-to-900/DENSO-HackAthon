import React, { useState } from 'react';
import './ActionRecommendations.css';
import './LoadingStates.css';

const ActionRecommendations = ({ actions, loading, error, onActionUpdate }) => {
  const [filter, setFilter] = useState('all'); // all, high, medium, low
  const [assignModal, setAssignModal] = useState(null); // { actionId, actionTitle }
  const [selectedTeam, setSelectedTeam] = useState('');
  const [assignNotes, setAssignNotes] = useState('');
  const [detailModal, setDetailModal] = useState(null); // For showing action details

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

  // Debug log to check actionItems
  console.log('[ActionRecommendations] Actions data:', actions.map(a => ({
    id: a.id,
    title: a.title,
    actionItems: a.actionItems,
    actionItemsType: typeof a.actionItems,
    actionItemsIsArray: Array.isArray(a.actionItems)
  })));

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

  const handleStartAction = (action) => {
    // Open assign modal
    setAssignModal({
      actionId: action.id,
      actionTitle: action.title
    });
    setSelectedTeam('');
    setAssignNotes('');
  };

  const handleAssignSubmit = () => {
    if (!selectedTeam) {
      alert('Vui lòng chọn đơn vị phụ trách');
      return;
    }

    // Update action status to in_progress and assign team
    if (onActionUpdate) {
      onActionUpdate(assignModal.actionId, {
        status: 'in_progress',
        assignedTeam: selectedTeam,
        notes: assignNotes
      });
    }

    // Close modal
    setAssignModal(null);
    setSelectedTeam('');
    setAssignNotes('');
  };

  const handleAssignCancel = () => {
    setAssignModal(null);
    setSelectedTeam('');
    setAssignNotes('');
  };

  const teams = [
    { id: 'production', name: '🏭 Phòng Sản xuất', description: 'Quản lý dây chuyền và công suất' },
    { id: 'supply_chain', name: '🚚 Phòng Chuỗi cung ứng', description: 'Logistics và nhà cung cấp' },
    { id: 'warehouse', name: '📦 Phòng Kho', description: 'Quản lý tồn kho và xuất nhập' },
    { id: 'sales', name: '💼 Phòng Kinh doanh', description: 'Giá cả và quan hệ khách hàng' },
    { id: 'quality', name: '✅ Phòng Chất lượng', description: 'Kiểm soát và tuân thủ' },
    { id: 'operations', name: '⚙️ Phòng Vận hành', description: 'Điều phối chung' }
  ];

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
                {(() => {
                  // Parse actionItems if it's a JSON string
                  let items = action.actionItems;
                  if (typeof items === 'string') {
                    try {
                      items = JSON.parse(items);
                    } catch (e) {
                      console.error('Failed to parse actionItems:', e);
                      items = [];
                    }
                  }
                  
                  // Render items
                  if (items && Array.isArray(items) && items.length > 0) {
                    return items.map((item, idx) => (
                      <li key={idx}>
                        {typeof item === 'string' ? item : item.step || item.title || JSON.stringify(item)}
                      </li>
                    ));
                  } else {
                    return (
                      <li style={{ color: '#9ca3af', fontStyle: 'italic' }}>
                        Chưa có bước thực hiện cụ thể
                      </li>
                    );
                  }
                })()}
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
                  onClick={() => setDetailModal(action)}
                >
                  Chi tiết
                </button>
                <button
                  className="btn-primary"
                  onClick={() => handleStartAction(action)}
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

      {/* Assignment Modal */}
      {assignModal && (
        <div className="modal-overlay" onClick={handleAssignCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Phân công nhiệm vụ</h3>
              <button className="modal-close" onClick={handleAssignCancel}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="modal-section">
                <label className="modal-label">Nhiệm vụ:</label>
                <p className="modal-action-title">{assignModal.actionTitle}</p>
              </div>

              <div className="modal-section">
                <label className="modal-label">Chọn đơn vị phụ trách: *</label>
                <div className="team-grid">
                  {teams.map(team => (
                    <div
                      key={team.id}
                      className={`team-card ${selectedTeam === team.id ? 'selected' : ''}`}
                      onClick={() => setSelectedTeam(team.id)}
                    >
                      <div className="team-name">{team.name}</div>
                      <div className="team-description">{team.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="modal-section">
                <label className="modal-label">Ghi chú (tùy chọn):</label>
                <textarea
                  className="modal-textarea"
                  placeholder="Nhập ghi chú hoặc hướng dẫn bổ sung..."
                  value={assignNotes}
                  onChange={(e) => setAssignNotes(e.target.value)}
                  rows={4}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-modal-cancel" onClick={handleAssignCancel}>
                Hủy
              </button>
              <button 
                className="btn-modal-submit" 
                onClick={handleAssignSubmit}
                disabled={!selectedTeam}
              >
                Phân công & Bắt đầu
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {detailModal && (
        <div className="modal-overlay" onClick={() => setDetailModal(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="detail-modal-title">
                <span className="detail-severity-icon">{getSeverityIcon(detailModal.severity)}</span>
                <h3>{detailModal.title}</h3>
              </div>
              <button className="modal-close" onClick={() => setDetailModal(null)}>×</button>
            </div>
            
            <div className="modal-body detail-modal-body">
              {/* Status and Priority */}
              <div className="detail-badges">
                <span
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(detailModal.priority) }}
                >
                  {getPriorityLabel(detailModal.priority)}
                </span>
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusBadge(detailModal.status).color }}
                >
                  {getStatusBadge(detailModal.status).label}
                </span>
              </div>

              {/* Description */}
              <div className="detail-section">
                <h4 className="detail-section-title">📋 Mô tả</h4>
                <p className="detail-text">{detailModal.description}</p>
              </div>

              {/* Impact and Deadline */}
              <div className="detail-section">
                <h4 className="detail-section-title">📊 Thông tin quan trọng</h4>
                <div className="detail-info-grid">
                  <div className="detail-info-item">
                    <span className="detail-info-label">Tác động dự kiến:</span>
                    <span className="detail-info-value impact">{detailModal.estimated_impact}</span>
                  </div>
                  <div className="detail-info-item">
                    <span className="detail-info-label">Hạn chót:</span>
                    <span className="detail-info-value deadline">{formatDeadline(detailModal.deadline)}</span>
                  </div>
                  {detailModal.assignedTeam && (
                    <div className="detail-info-item">
                      <span className="detail-info-label">Đơn vị phụ trách:</span>
                      <span className="detail-info-value team">
                        {teams.find(t => t.id === detailModal.assignedTeam)?.name || detailModal.assignedTeam}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Affected Products */}
              {detailModal.affectedProducts && detailModal.affectedProducts.length > 0 && (
                <div className="detail-section">
                  <h4 className="detail-section-title">🏷️ Sản phẩm liên quan</h4>
                  <div className="product-tags">
                    {detailModal.affectedProducts.map((product, idx) => (
                      <span key={idx} className="product-tag detail-product-tag">
                        {product}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Items */}
              <div className="detail-section">
                <h4 className="detail-section-title">✅ Các bước thực hiện</h4>
                <ul className="detail-action-list">
                  {(() => {
                    let items = detailModal.actionItems;
                    if (typeof items === 'string') {
                      try {
                        items = JSON.parse(items);
                      } catch (e) {
                        items = [];
                      }
                    }
                    
                    if (items && Array.isArray(items) && items.length > 0) {
                      return items.map((item, idx) => (
                        <li key={idx} className="detail-action-item">
                          <span className="detail-step-number">{idx + 1}</span>
                          <span className="detail-step-text">
                            {typeof item === 'string' ? item : item.step || item.title || JSON.stringify(item)}
                          </span>
                        </li>
                      ));
                    } else {
                      return (
                        <li className="detail-action-item empty">
                          <span className="detail-step-text">Chưa có bước thực hiện cụ thể</span>
                        </li>
                      );
                    }
                  })()}
                </ul>
              </div>

              {/* Risk Warning */}
              {detailModal.riskIfIgnored && (
                <div className="detail-section">
                  <h4 className="detail-section-title">⚠️ Rủi ro nếu bỏ qua</h4>
                  <div className="detail-risk-box">
                    <p className="detail-risk-text">{detailModal.riskIfIgnored}</p>
                  </div>
                </div>
              )}

              {/* Additional Notes */}
              {detailModal.notes && (
                <div className="detail-section">
                  <h4 className="detail-section-title">📝 Ghi chú</h4>
                  <p className="detail-text">{detailModal.notes}</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-modal-cancel" onClick={() => setDetailModal(null)}>
                Đóng
              </button>
              {detailModal.status !== 'completed' && (
                <button 
                  className="btn-modal-submit" 
                  onClick={() => {
                    setDetailModal(null);
                    handleStartAction(detailModal);
                  }}
                >
                  Bắt đầu thực hiện
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionRecommendations;
