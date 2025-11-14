import { useState, useEffect } from 'react';
import { getAllProductsStatus } from '../../services/api';
import './Dashboard.css';

function ProductsOverview() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProductsStatus();
  }, []);

  const loadProductsStatus = async () => {
    try {
      setLoading(true);
      const data = await getAllProductsStatus();
      setProducts(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load products status:', err);
      setError('Failed to load products status');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'adequate':
        return '#10b981'; // green
      case 'low':
        return '#f59e0b'; // amber
      case 'critical':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const getGrowthColor = (growth) => {
    if (growth > 5) return '#10b981'; // green
    if (growth < -5) return '#ef4444'; // red
    return '#6b7280'; // gray
  };

  const getLifecycleColor = (lifecycle) => {
    switch (lifecycle) {
      case 'new':
        return '#3b82f6'; // blue
      case 'growth':
        return '#10b981'; // green
      case 'mature':
        return '#6b7280'; // gray
      case 'decline':
        return '#ef4444'; // red
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-section">
        <div className="loading">Loading products status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-section">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-section">
      <div className="section-header">
        <h2>Products Overview</h2>
        <button onClick={loadProductsStatus} className="refresh-btn">
          Refresh
        </button>
      </div>

      <div className="products-grid">
        {products.map((product) => (
          <div key={product.product_code} className="product-card">
            <div className="product-card-header">
              <h3>{product.product_name}</h3>
              <span
                className="lifecycle-badge"
                style={{ backgroundColor: getLifecycleColor(product.product_lifecycle) }}
              >
                {product.product_lifecycle.toUpperCase()}
              </span>
            </div>

            <div className="product-code">{product.product_code}</div>

            <div className="product-metrics">
              <div className="metric-row">
                <span className="metric-label">Current Month Sales:</span>
                <span className="metric-value">{product.current_month_sales.toLocaleString()}</span>
              </div>

              <div className="metric-row">
                <span className="metric-label">5-Month Average:</span>
                <span className="metric-value">
                  {Math.round(product.last_5_months_avg).toLocaleString()}
                </span>
              </div>

              <div className="metric-row">
                <span className="metric-label">Growth Rate:</span>
                <span
                  className="metric-value"
                  style={{ color: getGrowthColor(product.growth_rate) }}
                >
                  {product.growth_rate > 0 ? '+' : ''}
                  {product.growth_rate.toFixed(1)}%
                </span>
              </div>

              <div className="metric-row">
                <span className="metric-label">Unit Price:</span>
                <span className="metric-value">${product.unit_price.toLocaleString()}</span>
              </div>
            </div>

            <div className="inventory-section">
              <div className="inventory-header">
                <span className="metric-label">Inventory Status</span>
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(product.stock_status) }}
                >
                  {product.stock_status.toUpperCase()}
                </span>
              </div>

              <div className="stock-bar">
                <div
                  className="stock-fill"
                  style={{
                    width: `${product.stock_ratio}%`,
                    backgroundColor: getStatusColor(product.stock_status),
                  }}
                />
              </div>

              <div className="stock-details">
                <div className="stock-item">
                  <span>Current:</span>
                  <strong>{product.current_stock.toLocaleString()}</strong>
                </div>
                <div className="stock-item">
                  <span>Safety:</span>
                  <strong>{product.safety_stock.toLocaleString()}</strong>
                </div>
                <div className="stock-item">
                  <span>Reorder Point:</span>
                  <strong>{product.reorder_point.toLocaleString()}</strong>
                </div>
              </div>

              <div className="warehouse-info">
                <span>📍 {product.warehouse_location}</span>
              </div>
            </div>

            <div className="quality-section">
              <div className="quality-metric">
                <span className="metric-label">Quality Score:</span>
                <span className="quality-value">{product.quality_score}/5.0</span>
              </div>
              <div className="quality-metric">
                <span className="metric-label">Defect Rate:</span>
                <span className="quality-value">{(product.defect_rate * 100).toFixed(2)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProductsOverview;

