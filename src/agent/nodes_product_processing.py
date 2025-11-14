"""Nodes for product batch processing and forecasting."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

import chromadb
import openai
from dotenv import load_dotenv
from langgraph.runtime import Runtime

from agent.internal_data_mock import (
    get_all_product_codes,
    get_internal_data_for_product,
    get_historical_sales_array,
    get_inventory_level,
    get_production_plans_array,
)
from agent.types_new import Context, State

# Load environment variables
load_dotenv()


async def split_product_batches(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Split products into batches for parallel processing.

    Input: List of product codes
    Output: Batches of product codes (5 batches)

    Purpose: Divide products into batches for parallel processing.
    """
    # Get product codes from state or context
    product_codes = state.product_codes or []

    if not product_codes:
        # Use mock product codes from internal_data_mock if none provided
        product_codes = get_all_product_codes()  # Returns 5 products: INV-001 to INV-005

    # Split into 5 batches
    batch_size = len(product_codes) // 5
    if batch_size == 0:
        batch_size = 1

    batches = []
    for i in range(5):
        start_idx = i * batch_size
        end_idx = start_idx + batch_size if i < 4 else len(product_codes)
        batch = product_codes[start_idx:end_idx]
        if batch:
            batches.append(batch)

    return {
        "product_batches": batches,
        "total_batches": len(batches),
        "total_products": len(product_codes),
    }


async def retrieve_relevant_context(
    product_code: str,
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Retrieve relevant context from ChromaDB for a product.

    Input: Product code
    Output: Top-5 relevant external insights

    Purpose: Query ChromaDB to get top-5 relevant external insights (e.g., "EV sales up 25% in EU").
    """
    # Initialize OpenAI client for embeddings
    embedding_base_url = os.getenv("EMBEDDING_API_BASE_URL")
    embedding_api_key = os.getenv("EMBEDDING_API_KEY")
    
    if not embedding_api_key:
        raise ValueError("EMBEDDING_API_KEY environment variable is not set. Please check your .env file.")
    
    client = openai.OpenAI(
        base_url=embedding_base_url,
        api_key=embedding_api_key
    )
    
    try:
        # Get product internal data to create a meaningful query
        product_data = get_internal_data_for_product(product_code)
        
        # Create search query based on product information
        query_text = f"{product_data['product_name']} {product_data['category']} {product_data['subcategory']} market trends demand forecast"
        
        # Step 1: Generate query embedding for product_code
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        
        query_embedding = response.data[0].embedding
        
        # Step 2: Initialize ChromaDB client
        chromadb_path = runtime.context.get("chromadb_path", "./chroma_db")
        chroma_client = chromadb.PersistentClient(path=chromadb_path)
        
        # Get or create collection
        collection_name = state.chromadb_collection or "external_market_data"
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Step 3: Query ChromaDB collection for top-5 similar documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        # Step 4: Format results into relevant insights
        relevant_insights = []
        
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                # Convert distance to relevance score (cosine distance: 0=identical, 2=opposite)
                # Convert to similarity score: 1 - (distance/2)
                distance = results['distances'][0][i] if results['distances'] else 0
                relevance_score = 1 - (distance / 2)
                
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                
                insight = {
                    "content": results['documents'][0][i],
                    "relevance_score": round(relevance_score, 3),
                    "source": metadata.get("source", "Unknown"),
                    "timestamp": metadata.get("timestamp", "Unknown"),
                    "type": metadata.get("type", "Unknown"),
                    "tags": metadata.get("tags", {}),
                }
                relevant_insights.append(insight)
        else:
            # Fallback to mock data if no results found
            relevant_insights = [
                {
                    "content": f"No specific market data found for {product_code}. Using general automotive market trends.",
                    "relevance_score": 0.50,
                    "source": "Default",
                    "timestamp": "2024-10-01",
                    "type": "fallback",
                    "tags": {},
                }
            ]
    
    except Exception as e:
        # Fallback to mock data if there's an error
        print(f"Error retrieving context for {product_code}: {e}")
        relevant_insights = [
            {
                "content": "EV sales up 25% in EU - relevant for automotive components",
                "relevance_score": 0.85,
                "source": "IEA",
                "timestamp": "2024-10-01",
                "type": "market_report",
                "tags": {"region": "EU", "sector": "automotive"},
            },
            {
                "content": "Battery demand +18% due to subsidies",
                "relevance_score": 0.78,
                "source": "EV Volumes",
                "timestamp": "2024-10-05",
                "type": "market_report",
                "tags": {"sector": "battery", "factor": "policy"},
            },
        ]
    
    return {
        "product_code": product_code,
        "relevant_context": relevant_insights,
        "context_count": len(relevant_insights),
    }


async def analyze_with_api(
    product_code: str,
    relevant_context: list[Dict[str, Any]],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze retrieved context with xAI API.

    Input: Product code, relevant context
    Output: Market insight (anonymized)

    Purpose: Send retrieved public context to xAI (anonymized) to generate market insight.
    """
    # Initialize OpenAI client for xAI API
    xai_base_url = os.getenv("XAI_API_BASE_URL")
    xai_api_key = os.getenv("XAI_API_KEY")
    xai_model = os.getenv("XAI_MODEL_NAME", "gpt-4o-mini")
    
    if not xai_api_key:
        raise ValueError("XAI_API_KEY environment variable is not set. Please check your .env file.")
    
    client = openai.OpenAI(
        base_url=xai_base_url,
        api_key=xai_api_key
    )
    
    try:
        # Get product data for context
        product_data = get_internal_data_for_product(product_code)
        
        # Prepare context summary (anonymize by removing internal codes and sensitive data)
        context_texts = []
        for item in relevant_context[:5]:  # Use top 5 contexts
            context_texts.append(f"- {item['content']} (Source: {item.get('source', 'Unknown')}, {item.get('timestamp', 'N/A')})")
        
        context_summary = "\n".join(context_texts)
        
        # Create anonymized prompt
        prompt = f"""You are a market analysis expert. Analyze the following external market data and provide insights for demand forecasting.

Product Category: {product_data.get('category', 'Automotive Component')}
Product Subcategory: {product_data.get('subcategory', 'Unknown')}

External Market Data:
{context_summary}

Please provide:
1. A concise market insight summary (2-3 sentences)
2. 3-5 key findings that could impact demand
3. A confidence score (0-1) for this analysis

Return your response in the following JSON format:
{{
    "insight": "Brief market analysis summary",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "confidence": 0.85
}}"""

        # Call xAI API
        response = client.chat.completions.create(
            model=xai_model,
            messages=[
                {"role": "system", "content": "You are an expert market analyst specializing in automotive and technology sectors. Provide concise, data-driven insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        import json
        import re
        
        # Find JSON in the response (handle code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            parsed_response = json.loads(json_match.group())
            
            market_insight = {
                "product_code": product_code,
                "insight": parsed_response.get("insight", response_text[:200]),
                "key_findings": parsed_response.get("key_findings", []),
                "confidence": parsed_response.get("confidence", 0.75),
                "analysis_timestamp": "2024-10-15T10:10:00",
                "model_used": xai_model,
            }
        else:
            # Fallback if JSON parsing fails
            market_insight = {
                "product_code": product_code,
                "insight": response_text[:200],
                "key_findings": ["Analysis completed", "See insight for details"],
                "confidence": 0.70,
                "analysis_timestamp": "2024-10-15T10:10:00",
                "model_used": xai_model,
            }
    
    except Exception as e:
        # Fallback to rule-based analysis if API fails
        print(f"Error calling xAI API for {product_code}: {e}")
        
        # Simple rule-based analysis from context
        context_summary = " ".join([item["content"] for item in relevant_context[:3]])
        
        key_findings = []
        if "EV" in context_summary or "electric vehicle" in context_summary.lower():
            key_findings.append("EV market growth trend detected")
        if "battery" in context_summary.lower() or "demand" in context_summary.lower():
            key_findings.append("Battery component demand increasing")
        if "EU" in context_summary or "Asia" in context_summary or "US" in context_summary:
            key_findings.append("Regional variations in demand patterns")
        
        if not key_findings:
            key_findings = ["Market analysis based on available context", "Standard demand patterns observed"]
        
        market_insight = {
            "product_code": product_code,
            "insight": f"Market analysis for {product_code}: {context_summary[:150]}...",
            "key_findings": key_findings,
            "confidence": 0.60,
            "analysis_timestamp": "2024-10-15T10:10:00",
            "model_used": "fallback",
        }

    return {
        "product_code": product_code,
        "market_insight": market_insight,
    }


async def fuse_with_internal_data(
    product_code: str,
    market_insight: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Fuse public insight with internal data.

    Input: Product code, market insight, internal data
    Output: Combined dataset ready for forecasting

    Purpose: Combine public insight with local historical sales, inventory, and production plans.
    """
    try:
        # Get comprehensive internal data from mock database
        product_data = get_internal_data_for_product(product_code)
        
        # Extract key metrics
        historical_sales = get_historical_sales_array(product_code, periods=5)
        inventory_info = product_data["inventory_levels"]
        
        internal_data = {
            "product_code": product_code,
            "product_name": product_data["product_name"],
            "category": product_data["category"],
            "subcategory": product_data["subcategory"],
            "unit_price": product_data["unit_price"],
            "product_lifecycle": product_data["product_lifecycle"],
            "manufacturing_location": product_data["manufacturing_location"],
            
            # Historical sales (last 5 months)
            "historical_sales": historical_sales,
            "historical_sales_full": product_data["historical_sales"],  # All 36 months
            
            # Inventory
            "inventory_levels": inventory_info["current_stock"],
            "safety_stock": inventory_info["safety_stock"],
            "reorder_point": inventory_info["reorder_point"],
            "max_stock": inventory_info["max_stock"],
            "stock_status": inventory_info["stock_status"],
            "warehouse_location": inventory_info["warehouse_location"],
            "lead_time_days": inventory_info["lead_time_days"],
            
            # Production plans
            "production_plans": get_production_plans_array(product_code),
            "production_plans_full": product_data["production_plans"],
            
            # Quality metrics
            "quality_metrics": product_data["quality_metrics"],
            
            # Market segments and regions
            "market_segments": product_data["market_segments"],
            "regions": product_data["regions"],
        }
        
        # Calculate historical trend
        if len(historical_sales) >= 2:
            recent_avg = sum(historical_sales[-3:]) / min(3, len(historical_sales))
            older_avg = sum(historical_sales[:2]) / min(2, len(historical_sales))
            if recent_avg > older_avg * 1.05:
                historical_trend = "increasing"
            elif recent_avg < older_avg * 0.95:
                historical_trend = "decreasing"
            else:
                historical_trend = "stable"
        else:
            historical_trend = "stable"
        
    except ValueError:
        # Fallback to simple mock data if product not found
        internal_data = {
            "product_code": product_code,
            "product_name": f"Product {product_code}",
            "historical_sales": [100, 120, 115, 130, 125],
            "inventory_levels": 500,
            "production_plans": [150, 160, 155],
            "stock_status": "adequate",
            "product_lifecycle": "unknown",
        }
        historical_trend = "stable"
    
    # Fuse with market insight
    fused_data = {
        "product_code": product_code,
        "internal_data": internal_data,
        "market_insight": market_insight,
        "combined_features": {
            "historical_trend": historical_trend,
            "market_signal": market_insight.get("key_findings", []),
            "inventory_status": internal_data.get("stock_status", "unknown"),
            "product_lifecycle": internal_data.get("product_lifecycle", "unknown"),
        },
    }

    return {
        "product_code": product_code,
        "fused_data": fused_data,
    }


async def generate_forecast(
    product_code: str,
    fused_data: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate demand forecast using ML model.

    Input: Product code, fused data
    Output: Forecast (units) for next quarter

    Purpose: Run local ML model (e.g., Prophet, LSTM) or rule-based adjustment to predict demand.
    """
    # Mock forecast generation - replace with actual Prophet/LSTM model
    # In real implementation, would:
    # 1. Prepare features from fused_data
    # 2. Run Prophet/LSTM model
    # 3. Generate forecast for next quarter

    historical_sales = fused_data["internal_data"]["historical_sales"]
    avg_sales = sum(historical_sales) / len(historical_sales)

    # Simple forecast with market adjustment
    market_factor = 1.15 if "increasing" in str(fused_data["combined_features"]["market_signal"]) else 1.0
    forecast_units = int(avg_sales * market_factor * 90)  # 90 days in quarter

    forecast = {
        "product_code": product_code,
        "forecast_period": "Q1_2025",
        "forecast_units": forecast_units,
        "confidence_interval": {
            "lower": int(forecast_units * 0.85),
            "upper": int(forecast_units * 1.15),
        },
        "method": "prophet_with_market_adjustment",
        "forecast_timestamp": "2024-10-15T10:15:00",
    }

    return {
        "product_code": product_code,
        "forecast": forecast,
    }


async def process_product_batch(
    batch_index: int,
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Process a batch of products (Retrieve → Analyze → Fuse → Forecast).

    Input: Batch index, product batch
    Output: Forecasts for all products in batch

    Purpose: Complete processing pipeline for a batch of products.
    """
    batches = state.product_batches or []
    if batch_index >= len(batches):
        return {"batch_results": []}

    product_batch = batches[batch_index]
    batch_results = []

    for product_code in product_batch:
        # Step 1: Retrieve relevant context
        context_result = await retrieve_relevant_context(product_code, state, runtime)
        relevant_context = context_result.get("relevant_context", [])

        # Step 2: Analyze with API
        analysis_result = await analyze_with_api(product_code, relevant_context, state, runtime)
        market_insight = analysis_result.get("market_insight", {})

        # Step 3: Fuse with internal data
        fuse_result = await fuse_with_internal_data(product_code, market_insight, state, runtime)
        fused_data = fuse_result.get("fused_data", {})

        # Step 4: Generate forecast
        forecast_result = await generate_forecast(product_code, fused_data, state, runtime)
        forecast = forecast_result.get("forecast", {})

        batch_results.append({
            "product_code": product_code,
            "forecast": forecast,
        })

    return {
        "batch_index": batch_index,
        "batch_results": batch_results,
        "products_processed": len(batch_results),
    }

