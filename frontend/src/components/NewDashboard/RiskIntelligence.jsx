import React, { useState } from 'react';
import './RiskIntelligence.css';
import './LoadingStates.css';

const RiskIntelligence = ({ newsRisks, loading, error }) => {
  const [selectedRisk, setSelectedRisk] = useState(null);

  // Loading state
  if (loading) {
    return (
      <div className="risk-intelligence loading-state">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Đang tải thông tin rủi ro...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="risk-intelligence error-state">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <h3>Không thể tải thông tin rủi ro</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!newsRisks || !newsRisks.news || !Array.isArray(newsRisks.news)) {
    console.error('[RiskIntelligence] Invalid newsRisks:', newsRisks);
    return (
      <div className="risk-intelligence empty-state">
        <p>Không có dữ liệu rủi ro</p>
      </div>
    );
  }

  const getRiskColor = (score) => {
    if (score >= 80) return '#ef4444'; // High
    if (score >= 60) return '#f59e0b'; // Medium-High
    if (score >= 40) return '#eab308'; // Medium
    return '#10b981'; // Low
  };

  const getRiskLevel = (score) => {
    if (score >= 80) return 'Rất cao';
    if (score >= 60) return 'Cao';
    if (score >= 40) return 'Trung bình';
    return 'Thấp';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffHours < 24) return `${diffHours} giờ trước`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} ngày trước`;
    return date.toLocaleDateString('vi-VN');
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'supply_chain': '🚢',
      'market': '📊',
      'weather': '🌪️',
      'competition': '⚔️',
      'policy': '📋'
    };
    return icons[category] || '📰';
  };

  const getImpactBadge = (impact) => {
    const badges = {
      'positive': { label: 'Tích cực', color: '#10b981' },
      'negative': { label: 'Tiêu cực', color: '#ef4444' },
      'neutral': { label: 'Trung lập', color: '#6b7280' }
    };
    return badges[impact] || badges.neutral;
  };

  return (
    <div className="risk-intelligence">
      <div className="risk-header">
        <h2>Giám sát rủi ro thông minh</h2>
        <div className="risk-summary">
          <span className="risk-count">{newsRisks.news.length} tín hiệu rủi ro</span>
          <span className="risk-trend">↑ +3 so với tuần trước</span>
        </div>
      </div>

      <div className="risk-content">
        <div className="news-list">
          {newsRisks.news.map((news) => (
            <div
              key={news.id}
              className={`news-card ${selectedRisk === news.id ? 'selected' : ''}`}
              onClick={() => setSelectedRisk(news.id)}
            >
              <div className="news-header">
                <span className="news-category">
                  {getCategoryIcon(news.category)} {news.category_name}
                </span>
                <span
                  className="news-risk-score"
                  style={{ backgroundColor: getRiskColor(news.risk_score) }}
                >
                  {news.risk_score}
                </span>
              </div>

              <h3 className="news-title">{news.title}</h3>

              <p className="news-summary">{news.summary}</p>

              <div className="news-meta">
                <span className="news-source">📰 {news.source}</span>
                <span className="news-date">{formatDate(news.date)}</span>
              </div>

              <div className="news-tags">
                {news.tags.map((tag, idx) => (
                  <span key={idx} className="tag">
                    {tag}
                  </span>
                ))}
              </div>

              <div className="news-impact">
                <span
                  className="impact-badge"
                  style={{ color: getImpactBadge(news.impact).color }}
                >
                  {getImpactBadge(news.impact).label}
                </span>
                <span className="affected-products">
                  Ảnh hưởng: {news.affected_products.join(', ')}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="risk-sidebar">
          <div className="risk-timeline">
            <h3>Timeline rủi ro</h3>
            <div className="timeline-chart">
              {newsRisks.timeline.map((point, idx) => (
                <div key={idx} className="timeline-point">
                  <div className="timeline-date">{point.date}</div>
                  <div className="timeline-bar">
                    <div
                      className="timeline-fill"
                      style={{
                        width: `${(point.count / 10) * 100}%`,
                        backgroundColor: getRiskColor(point.avg_risk)
                      }}
                    />
                  </div>
                  <div className="timeline-count">{point.count} sự kiện</div>
                </div>
              ))}
            </div>
          </div>

          <div className="risk-keywords">
            <h3>Từ khóa nổi bật</h3>
            <div className="keywords-cloud">
              {newsRisks.keywords.map((kw, idx) => (
                <span
                  key={idx}
                  className="keyword"
                  style={{
                    fontSize: `${12 + kw.frequency * 2}px`,
                    opacity: 0.6 + kw.frequency * 0.4
                  }}
                >
                  {kw.word}
                </span>
              ))}
            </div>
          </div>

          <div className="risk-distribution">
            <h3>Phân bố theo danh mục</h3>
            <div className="distribution-bars">
              {Object.entries({
                'Chuỗi cung ứng': 35,
                'Thị trường': 25,
                'Cạnh tranh': 20,
                'Thời tiết': 12,
                'Chính sách': 8
              }).map(([category, percent], idx) => (
                <div key={idx} className="distribution-item">
                  <span className="dist-label">{category}</span>
                  <div className="dist-bar-container">
                    <div
                      className="dist-bar"
                      style={{
                        width: `${percent}%`,
                        backgroundColor: '#3b82f6'
                      }}
                    />
                  </div>
                  <span className="dist-percent">{percent}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskIntelligence;
