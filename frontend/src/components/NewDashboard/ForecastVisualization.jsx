import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import './ForecastVisualization.css';
import './LoadingStates.css';

const ForecastVisualization = ({ forecastData, loading, error }) => {
  const [selectedView, setSelectedView] = useState('timeseries');

  // Loading state
  if (loading) {
    return (
      <div className="forecast-viz loading-state">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Đang tải dữ liệu dự báo...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="forecast-viz error-state">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <h3>Không thể tải dữ liệu dự báo</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!forecastData) {
    console.error('[ForecastVisualization] Invalid forecastData:', forecastData);
    return (
      <div className="forecast-viz empty-state">
        <p>Không có dữ liệu dự báo</p>
      </div>
    );
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{formatDate(label)}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderTimeSeries = () => (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={forecastData.timeSeries}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#6b7280"
          />
          <YAxis stroke="#6b7280" />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area
            type="monotone"
            dataKey="upper_bound"
            stroke="none"
            fill="#dbeafe"
            fillOpacity={0.3}
          />
          <Area
            type="monotone"
            dataKey="lower_bound"
            stroke="none"
            fill="#dbeafe"
            fillOpacity={0.3}
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Thực tế"
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Dự báo"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );

  const renderProductBreakdown = () => (
    <div className="products-grid">
      {forecastData.productBreakdown.map((product) => (
        <div key={product.product_id} className="product-card">
          <div className="product-header">
            <span className="product-name">{product.name}</span>
            <span className={`trend-badge ${product.trend}`}>
              {product.trend === 'up' ? '↑' : product.trend === 'down' ? '↓' : '→'}
              {product.change > 0 ? '+' : ''}{product.change}%
            </span>
          </div>
          <div className="product-forecast">
            <span className="forecast-label">Dự báo 30 ngày:</span>
            <span className="forecast-value">{product.forecast.toLocaleString()} đơn vị</span>
          </div>
          <div className="product-metrics">
            <div className="metric">
              <span className="metric-label">Độ tin cậy</span>
              <span className="metric-value">{product.confidence}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Rủi ro</span>
              <span className={`metric-value risk-${product.risk.toLowerCase()}`}>
                {product.risk}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderHeatmap = () => (
    <div className="heatmap-container">
      <table className="heatmap-table">
        <thead>
          <tr>
            <th>Sản phẩm</th>
            {forecastData.heatmap[0].values.map((val, idx) => (
              <th key={idx}>{val.month}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {forecastData.heatmap.map((row) => (
            <tr key={row.category}>
              <td className="category-cell">{row.category}</td>
              {row.values.map((val, idx) => (
                <td
                  key={idx}
                  className="heatmap-cell"
                  style={{
                    backgroundColor: `rgba(59, 130, 246, ${val.intensity})`,
                    color: val.intensity > 0.5 ? 'white' : '#111827'
                  }}
                >
                  {val.value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderMetrics = () => (
    <div className="metrics-grid">
      {forecastData.metrics.map((metric) => (
        <div key={metric.name} className="metric-card">
          <div className="metric-name">{metric.name}</div>
          <div className="metric-value-large">{metric.value}</div>
          <div className="metric-description">{metric.description}</div>
          <div className="metric-status" style={{ color: metric.status === 'excellent' ? '#10b981' : '#3b82f6' }}>
            {metric.status === 'excellent' ? '✓ Xuất sắc' : '✓ Tốt'}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="forecast-visualization">
      <div className="viz-header">
        <h2>Dự báo nhu cầu</h2>
        <div className="view-selector">
          <button
            className={selectedView === 'timeseries' ? 'active' : ''}
            onClick={() => setSelectedView('timeseries')}
          >
            📈 Xu hướng
          </button>
          <button
            className={selectedView === 'products' ? 'active' : ''}
            onClick={() => setSelectedView('products')}
          >
            📦 Sản phẩm
          </button>
          <button
            className={selectedView === 'heatmap' ? 'active' : ''}
            onClick={() => setSelectedView('heatmap')}
          >
            🔥 Bản đồ nhiệt
          </button>
          <button
            className={selectedView === 'metrics' ? 'active' : ''}
            onClick={() => setSelectedView('metrics')}
          >
            📊 Chỉ số
          </button>
        </div>
      </div>

      <div className="viz-content">
        {selectedView === 'timeseries' && renderTimeSeries()}
        {selectedView === 'products' && renderProductBreakdown()}
        {selectedView === 'heatmap' && renderHeatmap()}
        {selectedView === 'metrics' && renderMetrics()}
      </div>
    </div>
  );
};

export default ForecastVisualization;
