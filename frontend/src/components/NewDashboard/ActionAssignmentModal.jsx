import React, { useState, useEffect } from 'react';
import './ActionAssignmentModal.css';

const ActionAssignmentModal = ({ action, isOpen, onClose, onAssign }) => {
  const [formData, setFormData] = useState({
    assigned_team: '',
    assigned_to: '',
    due_date: '',
    notes: ''
  });

  const [teams] = useState([
    { id: 'production', name: 'Production Team', icon: '🏭' },
    { id: 'supply_chain', name: 'Supply Chain Team', icon: '🚚' },
    { id: 'warehouse', name: 'Warehouse Team', icon: '📦' },
    { id: 'sales', name: 'Sales Team', icon: '💰' },
    { id: 'quality', name: 'Quality Assurance', icon: '✅' },
    { id: 'operations', name: 'Operations Team', icon: '⚙️' }
  ]);

  const [teamMembers, setTeamMembers] = useState([]);

  // Mock team members data
  const mockTeamMembers = {
    production: [
      'Nguyễn Văn A',
      'Trần Thị B',
      'Lê Văn C',
      'Phạm Thị D'
    ],
    supply_chain: [
      'Hoàng Văn E',
      'Đặng Thị F',
      'Vũ Văn G'
    ],
    warehouse: [
      'Bùi Thị H',
      'Đỗ Văn I',
      'Ngô Thị J'
    ],
    sales: [
      'Phan Văn K',
      'Lý Thị L',
      'Mai Văn M'
    ],
    quality: [
      'Chu Thị N',
      'Tôn Văn O'
    ],
    operations: [
      'Đinh Thị P',
      'Hồ Văn Q',
      'Võ Thị R'
    ]
  };

  useEffect(() => {
    if (formData.assigned_team) {
      setTeamMembers(mockTeamMembers[formData.assigned_team] || []);
    } else {
      setTeamMembers([]);
    }
  }, [formData.assigned_team]);

  useEffect(() => {
    // Pre-fill with action's current assignment
    if (action && isOpen) {
      setFormData({
        assigned_team: action.assigned_team || '',
        assigned_to: action.assigned_to || '',
        due_date: action.due_date || '',
        notes: action.notes || ''
      });
    }
  }, [action, isOpen]);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Reset assigned_to when team changes
    if (field === 'assigned_team') {
      setFormData(prev => ({
        ...prev,
        assigned_to: ''
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.assigned_team) {
      alert('Vui lòng chọn team được phân công');
      return;
    }

    if (onAssign) {
      onAssign(action.id, {
        assigned_team: formData.assigned_team,
        assigned_to: formData.assigned_to || null,
        due_date: formData.due_date || null,
        notes: formData.notes || null,
        assigned_by: 'demo_user' // In production, get from auth
      });
    }

    handleClose();
  };

  const handleClose = () => {
    setFormData({
      assigned_team: '',
      assigned_to: '',
      due_date: '',
      notes: ''
    });
    onClose();
  };

  const getSuggestedDueDate = (priority) => {
    const today = new Date();
    let daysToAdd = 30;

    if (priority === 'high') daysToAdd = 7;
    else if (priority === 'medium') daysToAdd = 14;
    else if (priority === 'low') daysToAdd = 30;

    const dueDate = new Date(today.setDate(today.getDate() + daysToAdd));
    return dueDate.toISOString().split('T')[0];
  };

  const applySuggestedDate = () => {
    const suggestedDate = getSuggestedDueDate(action.priority);
    handleChange('due_date', suggestedDate);
  };

  if (!isOpen || !action) return null;

  const selectedTeam = teams.find(t => t.id === formData.assigned_team);

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="assignment-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>👥 Phân công nhiệm vụ</h2>
          <button className="close-button" onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Action Preview */}
          <div className="action-preview">
            <div className="action-preview-title">
              <span className={`priority-dot priority-${action.priority}`}></span>
              <h3>{action.title}</h3>
            </div>
            <p className="action-preview-desc">{action.description}</p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Team Selection */}
            <div className="form-group">
              <label htmlFor="assigned_team">
                <span className="required">*</span> Chọn Team
              </label>
              <div className="team-grid">
                {teams.map(team => (
                  <button
                    key={team.id}
                    type="button"
                    className={`team-card ${formData.assigned_team === team.id ? 'selected' : ''}`}
                    onClick={() => handleChange('assigned_team', team.id)}
                  >
                    <span className="team-icon">{team.icon}</span>
                    <span className="team-name">{team.name}</span>
                    {formData.assigned_team === team.id && (
                      <span className="check-mark">✓</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Individual Assignment */}
            {formData.assigned_team && (
              <div className="form-group">
                <label htmlFor="assigned_to">
                  Phân công cá nhân (Tùy chọn)
                </label>
                <select
                  id="assigned_to"
                  value={formData.assigned_to}
                  onChange={(e) => handleChange('assigned_to', e.target.value)}
                  className="form-select"
                >
                  <option value="">-- Chọn thành viên --</option>
                  {teamMembers.map((member, idx) => (
                    <option key={idx} value={member}>
                      {member}
                    </option>
                  ))}
                </select>
                <small className="form-hint">
                  {selectedTeam && `${selectedTeam.icon} ${selectedTeam.name}`}
                </small>
              </div>
            )}

            {/* Due Date */}
            <div className="form-group">
              <label htmlFor="due_date">
                Hạn hoàn thành
              </label>
              <div className="date-input-group">
                <input
                  type="date"
                  id="due_date"
                  value={formData.due_date}
                  onChange={(e) => handleChange('due_date', e.target.value)}
                  className="form-input"
                  min={new Date().toISOString().split('T')[0]}
                />
                <button
                  type="button"
                  className="btn-suggest"
                  onClick={applySuggestedDate}
                  title="Áp dụng hạn đề xuất"
                >
                  💡 Đề xuất
                </button>
              </div>
              <small className="form-hint">
                Đề xuất: {action.priority === 'high' ? '7 ngày' : action.priority === 'medium' ? '14 ngày' : '30 ngày'}
              </small>
            </div>

            {/* Notes */}
            <div className="form-group">
              <label htmlFor="notes">
                Ghi chú (Tùy chọn)
              </label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                className="form-textarea"
                rows="4"
                placeholder="Thêm hướng dẫn, yêu cầu đặc biệt, hoặc ghi chú khác..."
              />
            </div>

            {/* Action Summary */}
            <div className="assignment-summary">
              <h4>📋 Tóm tắt phân công</h4>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Team:</span>
                  <span className="summary-value">
                    {selectedTeam ? `${selectedTeam.icon} ${selectedTeam.name}` : 'Chưa chọn'}
                  </span>
                </div>
                {formData.assigned_to && (
                  <div className="summary-item">
                    <span className="summary-label">Người thực hiện:</span>
                    <span className="summary-value">{formData.assigned_to}</span>
                  </div>
                )}
                {formData.due_date && (
                  <div className="summary-item">
                    <span className="summary-label">Hạn chót:</span>
                    <span className="summary-value">
                      {new Date(formData.due_date).toLocaleDateString('vi-VN')}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Form Actions */}
            <div className="modal-actions">
              <button
                type="button"
                className="btn-cancel"
                onClick={handleClose}
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                className="btn-submit"
                disabled={!formData.assigned_team}
              >
                ✅ Phân công nhiệm vụ
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ActionAssignmentModal;
