# New Demand Forecasting Workflow

## Overview

The new workflow implements a discrete step-by-step process for demand forecasting with external data ingestion, parallel processing, and ML-based forecasting.

## Workflow Steps

### 1. Ingest External Data (`ingest`)
- **Input**: None (starts the pipeline)
- **Output**: Raw external data (dict/list of documents)
- **Purpose**: Pull and extract raw market data from public sources (IEA, EV Volumes, Reuters, etc.) via API, web scraping, or PDF parsing
- **Implementation**: `nodes_external_data.ingest_external_data()`

### 2. Clean & Tag Data (`clean_tag`)
- **Input**: Raw external data
- **Output**: Cleaned and tagged data with metadata
- **Purpose**: Normalize, deduplicate, and tag external data (e.g., sentiment, region, EV trend) using Pandas and local NLP
- **Implementation**: `nodes_external_data.clean_and_tag()`

### 3. Store & Index in ChromaDB (`store_index`)
- **Input**: Cleaned and tagged data
- **Output**: Confirmation of storage with collection info
- **Purpose**: Embed processed data and store in local vector database with metadata (product relevance, timestamp)
- **Implementation**: `nodes_external_data.store_in_chromadb()`

### 4. Split Product Batches (`split_batches`)
- **Input**: List of product codes
- **Output**: Batches of product codes (5 batches)
- **Purpose**: Divide products into batches for parallel processing
- **Implementation**: `nodes_product_processing.split_product_batches()`

### 5. Process Product Batches (Parallel - 5 batches)
Each batch goes through the following sub-steps:

#### 5a. Retrieve Relevant Context
- **Input**: Product code
- **Output**: Top-N relevant external insights
- **Purpose**: Query ChromaDB to get top-N relevant external insights (e.g., "EV sales up 25% in EU")
- **Implementation**: `nodes_product_processing.retrieve_relevant_context()`

#### 5b. Analyze with API
- **Input**: Product code, relevant context
- **Output**: Market insight (anonymized)
- **Purpose**: Send retrieved public context to xAI (anonymized) to generate market insight
- **Implementation**: `nodes_product_processing.analyze_with_api()`

#### 5c. Fuse with Internal Data
- **Input**: Product code, market insight, internal data
- **Output**: Combined dataset ready for forecasting
- **Purpose**: Combine public insight with local historical sales, inventory, and production plans
- **Implementation**: `nodes_product_processing.fuse_with_internal_data()`

#### 5d. Generate Forecast
- **Input**: Product code, fused data
- **Output**: Forecast (units) for next quarter
- **Purpose**: Run local ML model (e.g., Prophet, LSTM) or rule-based adjustment to predict demand
- **Implementation**: `nodes_product_processing.generate_forecast()`

**Batch Processing**: `nodes_product_processing.process_product_batch()` orchestrates all sub-steps for a batch

### 6. Aggregate Forecasts (`aggregate`)
- **Input**: Batch results from parallel processing
- **Output**: Aggregated forecasts for all products
- **Purpose**: Combine forecasts from all parallel batches into a single result set
- **Implementation**: `nodes_output.aggregate_forecasts()`

### 7. Output & Alert (`output_alert`)
- **Input**: Aggregated forecasts
- **Output**: Saved forecast, report, alerts (if triggered)
- **Purpose**: Save forecast to JSON/DB, generate report, and trigger alert (Slack/email) if demand change >10% or critical
- **Implementation**: `nodes_output.output_and_alert()`

## Graph Structure

```
__start__ → ingest → clean_tag → store_index → split_batches
                                                      ↓
                                    ┌────────────────┼────────────────┐
                                    ↓                ↓                ↓
                            process_batch_0  process_batch_1  ...  process_batch_4
                                    ↓                ↓                ↓
                                    └────────────────┼────────────────┘
                                                      ↓
                                                 aggregate → output_alert → END
```

## Parallel Processing

- All 5 batch processors run in parallel after `split_batches`
- Each batch processes its assigned products independently
- All batches converge to `aggregate` which waits for all to complete
- LangGraph automatically handles parallel execution and synchronization

## State Management

The new `State` class (`types_new.py`) tracks:
- External data ingestion results
- ChromaDB storage information
- Product batches
- Batch processing results
- Aggregated forecasts
- Output and alerts

## Legacy Code

The original graph implementation is preserved in `graph_legacy.py` for reference and future use.

## Next Steps

1. Implement actual API calls for external data ingestion
2. Integrate ChromaDB for vector storage
3. Connect to xAI API for market analysis
4. Implement Prophet/LSTM models for forecasting
5. Add Slack/Email alerting
6. Connect to internal databases for historical data

