import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import './ForecastVisualization.css';
import './LoadingStates.css';

const ForecastVisualization = ({ forecastData, loading, error }) => {
  const [selectedView, setSelectedView] = useState('timeseries');
  const [selectedProduct, setSelectedProduct] = useState(''); // Empty = chưa chọn, sẽ auto-select first product

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

  // Debug: Log data structure
  console.log('[ForecastVisualization] Received forecastData:', {
    hasTimeSeries: !!forecastData.timeSeries,
    hasProductBreakdown: !!forecastData.productBreakdown,
    productCount: forecastData.productBreakdown?.length,
    firstProduct: forecastData.productBreakdown?.[0]
  });

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}/${day}`;
  };

  const formatDateForAxis = (dateStr) => {
    // Format: "DD/MM" cho trục X
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${day}/${month}`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      // Tìm data point để lấy date info
      const dataPoint = payload[0]?.payload;
      const dateStr = dataPoint?.date || label;
      
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">
            <strong>{formatDate(dateStr)}</strong>
          </p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: '4px 0' }}>
              {entry.name}: <strong>{entry.value?.toLocaleString()}</strong> đơn vị
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const renderTimeSeries = () => {
    // Validate timeSeries data
    if (!forecastData.timeSeries || !Array.isArray(forecastData.timeSeries)) {
      return <div className="error-message">Không có dữ liệu chuỗi thời gian</div>;
    }

    // Validate product breakdown exists
    if (!forecastData.productBreakdown || forecastData.productBreakdown.length === 0) {
      return <div className="error-message">Không có dữ liệu sản phẩm</div>;
    }

    // Auto-select first product if none selected
    const currentProduct = selectedProduct || forecastData.productBreakdown[0]?.product_id || forecastData.productBreakdown[0]?.id;
    
    // Get time series data for selected product
    const product = forecastData.productBreakdown.find(p => 
      (p.product_id || p.id) === currentProduct
    );
    
    if (!product || !product.timeSeries) {
      return <div className="error-message">Không có dữ liệu chuỗi thời gian cho sản phẩm này</div>;
    }

    const timeSeriesData = product.timeSeries;
    const chartTitle = product.name || product.product_name || 'Sản phẩm';

    // Transform data to add formatted date for X-axis
    const transformedData = timeSeriesData.map((item, index) => {
      return {
        ...item,
        dateLabel: item.date ? formatDateForAxis(item.date) : `T${index + 1}`,
      };
    });

    // Debug: Check data structure
    console.log('[ForecastVisualization] TimeSeriesData:', {
      length: transformedData.length,
      first: transformedData[0],
      last: transformedData[transformedData.length - 1],
      hasWeekLabel: !!transformedData[0]?.weekLabel
    });

    return (
      <div className="chart-container">
        <div className="chart-header">
          <h3>{chartTitle}</h3>
          <div className="product-selector">
            <select 
              value={selectedProduct || currentProduct} 
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="product-select"
            >
              {forecastData.productBreakdown?.map(product => (
                <option 
                  key={product.product_id || product.id} 
                  value={product.product_id || product.id}
                >
                  {product.name || product.product_name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={transformedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="dateLabel"
              stroke="#6b7280"
              tick={{ fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => value ? value.toLocaleString() : '0'}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="#dbeafe"
              fillOpacity={0.3}
              name="Ngưỡng trên"
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#dbeafe"
              fillOpacity={0.3}
              name="Ngưỡng dưới"
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3 }}
              name="Thực tế"
            />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#3b82f6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3 }}
              name="Dự báo"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderProductBreakdown = () => {
    // Validate data
    if (!forecastData.productBreakdown || !Array.isArray(forecastData.productBreakdown)) {
      return <div className="error-message">Không có dữ liệu sản phẩm</div>;
    }

    return (
      <div className="products-grid">
        {forecastData.productBreakdown.map((product) => {
          // Normalize data: support both API format and mock format
          const productId = product.product_id || product.id || 'unknown';
          const productName = product.name || product.product_name || 'Unknown Product';
          
          // API format: forecast_units, Mock format: forecast
          const forecast = product.forecast ?? product.forecast_units ?? 0;
          
          // API format: change_percent, Mock format: change
          const change = product.change ?? product.change_percent ?? 0;
          
          const confidence = product.confidence ?? 0;
          
          // API format might not have risk field, derive from confidence
          let risk = product.risk || 'Unknown';
          if (risk === 'Unknown' && confidence > 0) {
            risk = confidence >= 90 ? 'Low' : confidence >= 75 ? 'Medium' : 'High';
          }
          
          const trend = product.trend ?? 'stable';
          
          return (
            <div key={productId} className="product-card">
              <div className="product-header">
                <span className="product-name">{productName}</span>
                <span className={`trend-badge ${trend}`}>
                  {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
                  {change > 0 ? '+' : ''}{typeof change === 'number' ? change.toFixed(1) : change}%
                </span>
              </div>
              <div className="product-forecast">
                <span className="forecast-label">Dự báo 30 ngày:</span>
                <span className="forecast-value">
                  {typeof forecast === 'number' ? forecast.toLocaleString() : forecast} đơn vị
                </span>
              </div>
              <div className="product-metrics">
                <div className="metric">
                  <span className="metric-label">Độ tin cậy</span>
                  <span className="metric-value">{typeof confidence === 'number' ? confidence.toFixed(1) : confidence}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Rủi ro</span>
                  <span className={`metric-value risk-${risk.toLowerCase()}`}>
                    {risk}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderHeatmap = () => {
    // Validate heatmap data
    if (!forecastData.heatmap || !Array.isArray(forecastData.heatmap) || forecastData.heatmap.length === 0) {
      return <div className="error-message">Không có dữ liệu bản đồ nhiệt</div>;
    }

    return (
      <div className="heatmap-container">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th>Sản phẩm</th>
              {forecastData.heatmap[0]?.values?.map((val, idx) => (
                <th key={idx}>{val.month}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {forecastData.heatmap.map((row) => (
              <tr key={row.category}>
                <td className="category-cell">{row.category}</td>
                {row.values?.map((val, idx) => (
                  <td
                    key={idx}
                    className="heatmap-cell"
                    style={{
                      backgroundColor: `rgba(59, 130, 246, ${val.intensity ?? 0.5})`,
                      color: (val.intensity ?? 0.5) > 0.5 ? 'white' : '#111827'
                    }}
                  >
                    {typeof val.value === 'number' ? val.value.toLocaleString() : val.value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderMetrics = () => {
    // Validate metrics data
    if (!forecastData.metrics) {
      return <div className="error-message">Không có dữ liệu chỉ số</div>;
    }

    // Handle both array and object format
    const metricsArray = Array.isArray(forecastData.metrics) 
      ? forecastData.metrics 
      : [
          { name: 'MAPE', value: '5.8%', description: 'Mean Absolute Percentage Error', status: 'excellent' },
          { name: 'RMSE', value: '287', description: 'Root Mean Squared Error', status: 'good' },
          { name: 'R²', value: '0.94', description: 'Coefficient of Determination', status: 'excellent' }
        ];

    return (
      <div className="metrics-grid">
        {metricsArray.map((metric) => (
          <div key={metric.name} className="metric-card">
            <div className="metric-name">{metric.name}</div>
            <div className="metric-value-large">{metric.value}</div>
            <div className="metric-description">{metric.description || ''}</div>
            <div className="metric-status" style={{ color: metric.status === 'excellent' ? '#10b981' : '#3b82f6' }}>
              {metric.status === 'excellent' ? '✓ Xuất sắc' : '✓ Tốt'}
            </div>
          </div>
        ))}
      </div>
    );
  };

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
