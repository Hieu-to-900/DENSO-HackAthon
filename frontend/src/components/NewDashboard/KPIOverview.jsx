import React from 'react';
import './KPIOverview.css';

const KPIOverview = ({ kpiData }) => {
  if (!kpiData || !Array.isArray(kpiData)) {
    console.error('[KPIOverview] Invalid kpiData:', kpiData);
    return <div>Loading KPIs...</div>;
  }

  const getStatusColor = (status) => {
    const colors = {
      excellent: '#10b981',
      good: '#3b82f6',
      warning: '#f59e0b',
      critical: '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '→';
  };

  const formatValue = (kpi) => {
    // % metrics
    if (
      kpi.id === 'forecast_accuracy' ||
      kpi.id === 'production_load' ||
      kpi.id === 'demand_change' ||
      kpi.id === 'service_level' ||
      kpi.id === 'data_coverage'
    ) {
      const signPrefix =
        kpi.id === 'demand_change' && Number(kpi.value) > 0 ? '+' : '';
      return `${signPrefix}${kpi.value}%`;
    }

    // Days of inventory
    if (kpi.id === 'inventory_cover') {
      return `${kpi.value} ngày`;
    }

    // Data latency (hours)
    if (kpi.id === 'data_latency') {
      return `${kpi.value} giờ`;
    }

    // Stockout risk hiển thị raw (có thanh risk bar riêng)
    if (kpi.id === 'stockout_risk') {
      return kpi.value;
    }

    // Default
    return kpi.value;
  };

  const formatChange = (change, trend) => {
    if (typeof change === 'string') return change;
    const sign = change > 0 ? '+' : '';
    return `${sign}${change}%`;
  };

  // ====== 4 GROUPS × 2 KPI (tối đa) ======
  // Bạn nhớ update mockData cho đúng các id bên dưới.
  const KPI_LAYOUT = [
    {
      id: 'forecast',
      title: 'Forecast Performance',
      description: 'Model accuracy and demand dynamics across key markets.',
      kpiIds: ['forecast_accuracy', 'demand_change']
    },
    {
      id: 'supply_inventory',
      title: 'Supply & Inventory Load',
      description: 'Production utilization and inventory buffer readiness.',
      kpiIds: ['production_load', 'inventory_cover']
    },
    {
      id: 'risk_service',
      title: 'Risk & Service Reliability',
      description: 'Stockout exposure and service performance.',
      kpiIds: ['stockout_risk', 'service_level']
    },
    {
      id: 'data_health',
      title: 'Data Health & Coverage',
      description:
        'Data completeness and freshness for forecasting pipelines.',
      // 2 KPI mới gợi ý cho admin:
      // - data_coverage: % SKU-region có dữ liệu đầy đủ
      // - data_latency: số giờ kể từ lần ETL/forecast gần nhất
      kpiIds: ['data_coverage', 'data_latency']
    }
  ];

  const renderKpiCard = (kpi) => (
    <div
      key={kpi.id}
      className="kpi-card"
      style={{ borderLeftColor: getStatusColor(kpi.status) }}
    >
      <div className="kpi-header">
        <span className="kpi-icon">{kpi.icon}</span>
        <span className="kpi-title">{kpi.title}</span>
      </div>
      <div className="kpi-value">{formatValue(kpi)}</div>
      <div className="kpi-footer">
        <span className={`kpi-change ${kpi.trend}`}>
          <span className="trend-icon">{getTrendIcon(kpi.trend)}</span>
          {formatChange(kpi.change, kpi.trend)}
        </span>
        <span className="kpi-period">vs 30 ngày trước</span>
      </div>
      {kpi.id === 'stockout_risk' && (
        <div className="risk-bar">
          <div
            className="risk-fill"
            style={{
              width: `${kpi.riskScore}%`,
              backgroundColor: getStatusColor(kpi.status)
            }}
          />
        </div>
      )}
    </div>
  );

  // Chia thành 2 hàng, mỗi hàng gồm 2 group
  const rows = [
    KPI_LAYOUT.slice(0, 2), // row 1
    KPI_LAYOUT.slice(2, 4) // row 2
  ];

  return (
    <div className="kpi-overview">
      {rows.map((rowGroups, rowIndex) => (
        <div className="kpi-row" key={`row-${rowIndex}`}>
          {rowGroups.map((group) => {
            // Lấy đúng các KPI thuộc group này theo id
            const items = group.kpiIds
              .map((id) => kpiData.find((k) => k.id === id))
              .filter(Boolean);

            // Nếu group không có KPI nào trong data thì bỏ qua
            if (items.length === 0) return null;

            return (
              <section key={group.id} className="kpi-group">
                <div className="kpi-group-header">
                  <div>
                    <h3 className="kpi-group-title">{group.title}</h3>
                    <p className="kpi-group-subtitle">
                      {group.description}
                    </p>
                  </div>
                  <span className="kpi-group-meta">
                    {items.length} metric{items.length > 1 ? 's' : ''}
                  </span>
                </div>
                <div className="kpi-grid">
                  {items.map((kpi) => renderKpiCard(kpi))}
                </div>
              </section>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default KPIOverview;
