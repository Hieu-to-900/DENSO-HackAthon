# AI Demand Forecasting Dashboard

Web dashboard for visualizing demand forecasting data for Denso EV Inverter.

## Project Structure

```
workspace/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
└── src/agent/       # LangGraph forecasting agent
```

## Setup Instructions

### Backend Setup

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
pip install -e ..  # Install agent package
```

2. Set up environment variables (create `.env` file):
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the backend server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Run the frontend development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Endpoints

- `GET /api/products` - List available products
- `GET /api/historical/{product_id}` - Get historical sales data
- `POST /api/forecast` - Run forecast
- `GET /api/forecast/{product_id}` - Get latest forecast
- `GET /api/supply-chain/{product_id}` - Get supply chain metrics
- `GET /api/scenarios/{product_id}` - Get scenario planning data

## Features

### Main Overview Dashboard
- Historical sales time series chart
- Forecast visualization with confidence bands
- Key metrics cards (Total Sales, Avg Daily Demand, Growth Rate, Current Stock)

### Forecast Analysis Section
- Seasonal forecast chart with Prophet confidence intervals
- Scenario comparison (Optimistic, Realistic, Pessimistic)
- Anomaly detection visualization

### Supply Chain Optimization Section
- Inventory metrics (Current Stock, Reorder Point, Safety Stock, Optimal Order Quantity)
- Cost analysis chart
- Reorder recommendations and alerts

## Filters

- Product selector
- Date range picker
- Forecast mode selector (comprehensive/seasonal/promotional/new_product)
- Forecast horizon slider (7-90 days)

