import { useState, useEffect } from 'react';
import Filters from './components/Filters';
import MainOverview from './components/Dashboard/MainOverview';
import ForecastAnalysis from './components/Dashboard/ForecastAnalysis';
import SupplyChain from './components/Dashboard/SupplyChain';
import ProductsOverview from './components/Dashboard/ProductsOverview';
import { getProducts, runForecast } from './services/api';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('INV-001');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('overview'); // 'overview' or 'detail'
  const [filters, setFilters] = useState({
    forecastMode: 'comprehensive',
    forecastHorizonDays: 30,
    startDate: null,
    endDate: null,
  });

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      loadForecast();
    }
  }, [selectedProduct, filters]);

  const loadProducts = async () => {
    try {
      const data = await getProducts();
      setProducts(data);
      if (data.length > 0 && !selectedProduct) {
        setSelectedProduct(data[0].product_id);
      }
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const loadForecast = async () => {
    setLoading(true);
    try {
      const request = {
        product_id: selectedProduct,
        forecast_mode: filters.forecastMode,
        forecast_horizon_days: filters.forecastHorizonDays,
        start_date: filters.startDate,
        end_date: filters.endDate,
      };
      const data = await runForecast(request);
      setForecastData(data);
    } catch (error) {
      console.error('Failed to load forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Demand Forecasting Dashboard</h1>
        <p>Denso EV Inverter Products - Demand Analysis</p>
      </header>

      {/* View mode toggle */}
      <div className="view-toggle">
        <button
          className={viewMode === 'overview' ? 'active' : ''}
          onClick={() => setViewMode('overview')}
        >
          Products Overview
        </button>
        <button
          className={viewMode === 'detail' ? 'active' : ''}
          onClick={() => setViewMode('detail')}
        >
          Product Detail
        </button>
      </div>

      {viewMode === 'overview' ? (
        <ProductsOverview />
      ) : (
        <>
          <Filters
            products={products}
            selectedProduct={selectedProduct}
            onProductChange={setSelectedProduct}
            filters={filters}
            onFilterChange={handleFilterChange}
          />

          {loading && (
            <div className="loading">
              <p>Loading forecast data...</p>
            </div>
          )}

          {forecastData && !loading && (
            <div className="dashboard-container">
              <MainOverview forecastData={forecastData} />
              <ForecastAnalysis forecastData={forecastData} />
              <SupplyChain forecastData={forecastData} />
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;

