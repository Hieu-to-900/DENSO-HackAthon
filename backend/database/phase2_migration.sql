-- Phase 2 Week 1: Core Integrations
-- Add tables for forecasts, actions, and KPIs

-- ========================================
-- 1. FORECASTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(100) NOT NULL,
    product_code VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    
    -- Forecast data
    forecast_units INTEGER NOT NULL,
    current_stock INTEGER,
    trend VARCHAR(20) CHECK (trend IN ('up', 'down', 'stable')),
    change_percent DECIMAL(10, 2),
    confidence DECIMAL(5, 2) CHECK (confidence >= 0 AND confidence <= 100),
    
    -- Time horizon
    forecast_horizon VARCHAR(50) NOT NULL, -- '90_days', 'Q1_2025', etc.
    forecast_start_date DATE NOT NULL,
    forecast_end_date DATE NOT NULL,
    
    -- LangGraph metadata
    langgraph_job_id UUID,
    model_type VARCHAR(100) DEFAULT 'Prophet + LLM',
    model_metadata JSONB, -- Full LangGraph state output
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Validation
    is_validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP WITH TIME ZONE,
    validated_by VARCHAR(100)
);

-- Indexes for fast queries
CREATE INDEX idx_forecasts_product_code ON forecasts (product_code);
CREATE INDEX idx_forecasts_category ON forecasts (category);
CREATE INDEX idx_forecasts_created_at ON forecasts (created_at DESC);
CREATE INDEX idx_forecasts_horizon ON forecasts (forecast_horizon);
CREATE INDEX idx_forecasts_job_id ON forecasts (langgraph_job_id);
CREATE INDEX idx_forecasts_metadata ON forecasts USING GIN (model_metadata);

-- ========================================
-- 2. FORECAST TIME SERIES TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS forecast_timeseries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Values
    actual INTEGER, -- Historical actual value (if available)
    forecast INTEGER, -- Predicted value
    upper_bound INTEGER, -- Confidence interval upper
    lower_bound INTEGER, -- Confidence interval lower
    
    is_historical BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(forecast_id, date)
);

CREATE INDEX idx_timeseries_forecast_id ON forecast_timeseries (forecast_id);
CREATE INDEX idx_timeseries_date ON forecast_timeseries (date);

-- ========================================
-- 3. FORECAST METRICS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS forecast_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    
    -- Performance metrics
    mape DECIMAL(10, 4), -- Mean Absolute Percentage Error
    rmse DECIMAL(10, 2), -- Root Mean Squared Error
    mae DECIMAL(10, 2), -- Mean Absolute Error
    r_squared DECIMAL(10, 4), -- R-squared coefficient
    
    -- Model info
    training_data_points INTEGER,
    test_data_points INTEGER,
    last_trained_at TIMESTAMP WITH TIME ZONE,
    model_version VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_forecast_id ON forecast_metrics (forecast_id);

-- ========================================
-- 4. ACTION RECOMMENDATIONS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS action_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Classification
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    category VARCHAR(50) NOT NULL, -- 'supply_chain', 'inventory', 'pricing', 'production', 'marketing', 'competitor'
    
    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    impact TEXT,
    
    -- Cost & Timeline
    estimated_cost DECIMAL(12, 2) DEFAULT 0,
    estimated_cost_unit VARCHAR(10) DEFAULT 'USD',
    deadline DATE,
    
    -- Action items (checklist)
    action_items JSONB NOT NULL, -- Array of action steps
    affected_products TEXT[], -- Array of product codes
    risk_if_ignored TEXT,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'snoozed', 'cancelled')),
    snoozed_until TIMESTAMP WITH TIME ZONE,
    
    -- Completion tracking
    completed_at TIMESTAMP WITH TIME ZONE,
    completed_by VARCHAR(100),
    completion_notes TEXT,
    
    -- Source
    langgraph_job_id UUID,
    forecast_id UUID REFERENCES forecasts(id) ON DELETE SET NULL,
    source VARCHAR(50) DEFAULT 'langgraph',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_priority ON action_recommendations (priority);
CREATE INDEX idx_actions_category ON action_recommendations (category);
CREATE INDEX idx_actions_status ON action_recommendations (status);
CREATE INDEX idx_actions_deadline ON action_recommendations (deadline);
CREATE INDEX idx_actions_created_at ON action_recommendations (created_at DESC);
CREATE INDEX idx_actions_forecast_id ON action_recommendations (forecast_id);
CREATE INDEX idx_actions_affected_products ON action_recommendations USING GIN (affected_products);

-- ========================================
-- 5. KPI SNAPSHOTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS kpi_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- KPI identification
    metric_name VARCHAR(100) NOT NULL,
    metric_category VARCHAR(50) NOT NULL, -- 'forecast', 'inventory', 'production', 'risk'
    
    -- Values
    value DECIMAL(12, 4) NOT NULL,
    change DECIMAL(10, 4), -- Change from previous snapshot
    trend VARCHAR(20) CHECK (trend IN ('up', 'down', 'stable')),
    status VARCHAR(20) CHECK (status IN ('excellent', 'good', 'warning', 'critical')),
    
    -- Context
    unit VARCHAR(20), -- '%', 'units', 'days', etc.
    metadata JSONB,
    
    -- Timestamps
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(metric_name, snapshot_date)
);

CREATE INDEX idx_kpi_metric_name ON kpi_snapshots (metric_name);
CREATE INDEX idx_kpi_snapshot_date ON kpi_snapshots (snapshot_date DESC);
CREATE INDEX idx_kpi_category ON kpi_snapshots (metric_category);

-- ========================================
-- 6. RISK NEWS TABLE (ChromaDB Cache)
-- ========================================

CREATE TABLE IF NOT EXISTS risk_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- External ID (from ChromaDB or news source)
    external_id VARCHAR(255) UNIQUE,
    chromadb_id VARCHAR(255),
    
    -- Content
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    source VARCHAR(100) NOT NULL,
    url TEXT,
    
    -- Classification
    category VARCHAR(50) NOT NULL, -- 'logistics', 'supply_chain', 'competition', 'regulatory', 'weather', 'market_trend'
    category_name VARCHAR(100),
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'mixed', 'neutral')),
    
    -- Risk assessment
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    impact TEXT,
    
    -- Product relations
    related_products TEXT[],
    affected_products TEXT[],
    tags TEXT[],
    
    -- Dates
    article_date DATE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Sync status
    last_synced_from_chromadb TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_risk_news_article_date ON risk_news (article_date DESC);
CREATE INDEX idx_risk_news_category ON risk_news (category);
CREATE INDEX idx_risk_news_risk_score ON risk_news (risk_score DESC);
CREATE INDEX idx_risk_news_chromadb_id ON risk_news (chromadb_id);
CREATE INDEX idx_risk_news_related_products ON risk_news USING GIN (related_products);
CREATE INDEX idx_risk_news_tags ON risk_news USING GIN (tags);

-- ========================================
-- 7. RISK KEYWORDS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS risk_keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    word VARCHAR(100) NOT NULL,
    keyword VARCHAR(100), -- Original keyword (e.g., Japanese)
    
    -- Statistics
    count INTEGER NOT NULL DEFAULT 1,
    frequency DECIMAL(5, 4), -- Normalized 0-1
    sentiment DECIMAL(5, 4) CHECK (sentiment >= -1 AND sentiment <= 1),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(word, period_start, period_end)
);

CREATE INDEX idx_keywords_word ON risk_keywords (word);
CREATE INDEX idx_keywords_count ON risk_keywords (count DESC);
CREATE INDEX idx_keywords_period ON risk_keywords (period_start, period_end);

-- ========================================
-- TRIGGERS
-- ========================================

-- Auto-update updated_at for forecasts
CREATE TRIGGER update_forecasts_updated_at 
    BEFORE UPDATE ON forecasts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at for actions
CREATE TRIGGER update_actions_updated_at 
    BEFORE UPDATE ON action_recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at for risk_news
CREATE TRIGGER update_risk_news_updated_at 
    BEFORE UPDATE ON risk_news
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at for keywords
CREATE TRIGGER update_keywords_updated_at 
    BEFORE UPDATE ON risk_keywords
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- VIEWS FOR DASHBOARD
-- ========================================

-- Latest forecasts view
CREATE OR REPLACE VIEW latest_forecasts AS
SELECT DISTINCT ON (product_code)
    id, product_code, product_name, category,
    forecast_units, current_stock, trend, change_percent, confidence,
    forecast_horizon, created_at
FROM forecasts
ORDER BY product_code, created_at DESC;

-- Active actions view
CREATE OR REPLACE VIEW active_actions AS
SELECT 
    id, priority, category, title, description, impact,
    estimated_cost, deadline, affected_products, status,
    created_at
FROM action_recommendations
WHERE status IN ('pending', 'in_progress', 'snoozed')
    AND (snoozed_until IS NULL OR snoozed_until < CURRENT_TIMESTAMP)
ORDER BY 
    CASE priority
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END,
    deadline ASC NULLS LAST;

-- Latest KPIs view
CREATE OR REPLACE VIEW latest_kpis AS
SELECT DISTINCT ON (metric_name)
    metric_name, metric_category, value, change, trend, status, unit, snapshot_date
FROM kpi_snapshots
ORDER BY metric_name, snapshot_date DESC;

-- Recent risk news view
CREATE OR REPLACE VIEW recent_risk_news AS
SELECT 
    id, title, summary, source, category, category_name,
    sentiment, risk_score, impact, related_products, affected_products, tags,
    article_date, created_at
FROM risk_news
WHERE article_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY article_date DESC, risk_score DESC;

-- ========================================
-- COMMENTS
-- ========================================

COMMENT ON TABLE forecasts IS 'Stores demand forecast results from LangGraph pipeline';
COMMENT ON TABLE forecast_timeseries IS 'Time series data for each forecast (historical + predicted)';
COMMENT ON TABLE forecast_metrics IS 'Model performance metrics for forecast validation';
COMMENT ON TABLE action_recommendations IS 'Actionable recommendations generated from forecasts and risks';
COMMENT ON TABLE kpi_snapshots IS 'Time-series snapshots of key performance indicators';
COMMENT ON TABLE risk_news IS 'External market news and risk intelligence (synced from ChromaDB)';
COMMENT ON TABLE risk_keywords IS 'Extracted keywords from risk news with frequency and sentiment';

COMMENT ON VIEW latest_forecasts IS 'Most recent forecast for each product';
COMMENT ON VIEW active_actions IS 'All pending and in-progress actions sorted by priority';
COMMENT ON VIEW latest_kpis IS 'Most recent value for each KPI metric';
COMMENT ON VIEW recent_risk_news IS 'Risk news from the last 30 days';
