"""Category-based product processing for efficient batch forecasting.

This module implements category-based batching where products in the same category
share market insights and context, reducing API calls and improving efficiency.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

import chromadb
from openai import AsyncOpenAI
import pandas as pd
from dotenv import load_dotenv
from langgraph.runtime import Runtime
from prophet import Prophet

from agent.category_products_mock import (
    get_all_categories,
    get_category_for_product,
    get_category_info,
    get_product_by_code,
    get_products_by_category,
)
from agent.types_new import Context, State

load_dotenv()


async def split_by_category(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Split products by category for efficient batch processing.
    
    Input: List of product codes
    Output: Category batches with products grouped by category
    
    Purpose: Group products by category to enable shared context and computation.
    """
    product_codes = state.product_codes or []
    
    if not product_codes:
        # Use all products from mock data
        from agent.category_products_mock import get_all_product_codes
        product_codes = get_all_product_codes()
    
    # Group products by category
    category_batches = {}
    for product_code in product_codes:
        try:
            category = get_category_for_product(product_code)
            if category not in category_batches:
                category_info = get_category_info(category)
                category_batches[category] = {
                    "category": category,
                    "category_name": category_info.get("category_name", category),
                    "category_name_vi": category_info.get("category_name_vi", ""),
                    "description": category_info.get("description", ""),
                    "products": []
                }
            category_batches[category]["products"].append(product_code)
        except ValueError as e:
            print(f"Warning: {e}")
            continue
    
    # Convert to list
    category_batch_list = list(category_batches.values())
    
    return {
        "category_batches": category_batch_list,
        "total_categories": len(category_batch_list),
        "total_products": len(product_codes),
    }


async def retrieve_category_context(
    category: str,
    category_info: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Retrieve relevant context from ChromaDB for an entire category.
    
    Input: Category information
    Output: Top-5 relevant external insights for the category
    
    Purpose: Query ChromaDB ONCE for entire category instead of per product.
    """
    embedding_base_url = os.getenv("EMBEDDING_API_BASE_URL")
    embedding_api_key = os.getenv("EMBEDDING_API_KEY")
    
    if not embedding_api_key:
        raise ValueError("EMBEDDING_API_KEY environment variable is not set")
    
    client = AsyncOpenAI(
        base_url=embedding_base_url,
        api_key=embedding_api_key
    )
    
    try:
        # Create category-level query
        category_name = category_info.get("category_name", category)
        description = category_info.get("description", "")
        query_text = f"{category_name} {description} automotive market trends demand forecast Vietnam"
        
        # Generate query embedding (async call)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text
        )
        
        query_embedding = response.data[0].embedding
        
        # Query ChromaDB
        chromadb_path = runtime.context.get("chromadb_path", "./chroma_db")
        chroma_client = chromadb.PersistentClient(path=chromadb_path)
        
        collection_name = state.chromadb_collection or "external_market_data"
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Query for top-5 similar documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        relevant_insights = []
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
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
            # Fallback to category-specific mock data
            if "Spark" in category_name or "Bugi" in category_info.get("category_name_vi", ""):
                relevant_insights = [
                    {
                        "content": "Vietnam automotive aftermarket growing 12% YoY - spark plug demand increasing",
                        "relevance_score": 0.88,
                        "source": "Vietnam Automotive Industry Report 2024",
                        "timestamp": "2024-12-01",
                        "type": "market_report",
                        "tags": {"region": "Vietnam", "sector": "automotive_aftermarket"},
                    },
                    {
                        "content": "Iridium spark plug adoption rate up 25% in Southeast Asia premium segment",
                        "relevance_score": 0.82,
                        "source": "ASEAN Auto Parts Trends",
                        "timestamp": "2024-11-15",
                        "type": "market_trend",
                        "tags": {"region": "ASEAN", "product_type": "spark_plugs"},
                    },
                ]
            else:  # AC System
                relevant_insights = [
                    {
                        "content": "Vietnam AC component market forecast to grow 18% annually due to rising vehicle sales and hot climate",
                        "relevance_score": 0.90,
                        "source": "Southeast Asia HVAC Market Report",
                        "timestamp": "2024-11-20",
                        "type": "market_forecast",
                        "tags": {"region": "Vietnam", "sector": "automotive_ac"},
                    },
                    {
                        "content": "Compressor and evaporator demand surge in Q4 2024 due to hot weather patterns",
                        "relevance_score": 0.85,
                        "source": "Vietnam Climate & Auto Parts Correlation Study",
                        "timestamp": "2024-12-05",
                        "type": "market_insight",
                        "tags": {"season": "Q4", "weather": "hot"},
                    },
                ]
    
    except Exception as e:
        print(f"Error retrieving category context for {category}: {e}")
        relevant_insights = [
            {
                "content": f"General market data for {category_name}",
                "relevance_score": 0.50,
                "source": "Default",
                "timestamp": "2024-12-15",
                "type": "fallback",
                "tags": {},
            }
        ]
    
    return {
        "category": category,
        "category_context": relevant_insights,
        "context_count": len(relevant_insights),
    }


async def analyze_category_with_api(
    category: str,
    category_info: Dict[str, Any],
    category_context: List[Dict[str, Any]],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Analyze category-level context with xAI API.
    
    Input: Category information and relevant context
    Output: Category-level market insight (shared across all products in category)
    
    Purpose: Call xAI API ONCE for entire category instead of per product.
    """
    xai_base_url = os.getenv("XAI_API_BASE_URL")
    xai_api_key = os.getenv("XAI_API_KEY")
    xai_model = os.getenv("XAI_MODEL_NAME", "gpt-4o-mini")
    
    if not xai_api_key:
        raise ValueError("XAI_API_KEY environment variable is not set")
    
    client = AsyncOpenAI(
        base_url=xai_base_url,
        api_key=xai_api_key
    )
    
    try:
        # Prepare context summary
        context_texts = []
        for item in category_context[:5]:
            context_texts.append(f"- {item['content']} (Source: {item.get('source', 'Unknown')}, {item.get('timestamp', 'N/A')})")
        
        context_summary = "\n".join(context_texts)
        
        category_name = category_info.get("category_name", category)
        category_name_vi = category_info.get("category_name_vi", "")
        
        # Create prompt
        prompt = f"""You are a market analysis expert for the Vietnamese automotive aftermarket. Analyze the following external market data for {category_name} ({category_name_vi}).

Category Description: {category_info.get('description', 'Automotive components')}

External Market Data:
{context_summary}

Please provide:
1. A concise market insight summary (2-3 sentences) specific to Vietnam market
2. 3-5 key findings that could impact demand for this product category
3. A confidence score (0-1) for this analysis

Return your response in JSON format:
{{
    "insight": "Brief market analysis summary",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "confidence": 0.85
}}"""

        # Call xAI API (async call)
        response = await client.chat.completions.create(
            model=xai_model,
            messages=[
                {"role": "system", "content": "You are an expert market analyst specializing in Vietnamese automotive aftermarket and DENSO products."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            parsed_response = json.loads(json_match.group())
            
            category_insight = {
                "category": category,
                "category_name": category_name,
                "insight": parsed_response.get("insight", response_text[:200]),
                "key_findings": parsed_response.get("key_findings", []),
                "confidence": parsed_response.get("confidence", 0.75),
                "analysis_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "model_used": xai_model,
            }
        else:
            category_insight = {
                "category": category,
                "category_name": category_name,
                "insight": response_text[:200],
                "key_findings": ["Analysis completed", "See insight for details"],
                "confidence": 0.70,
                "analysis_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "model_used": xai_model,
            }
    
    except Exception as e:
        print(f"Error calling xAI API for category {category}: {e}")
        
        # Fallback analysis
        context_summary = " ".join([item["content"] for item in category_context[:3]])
        category_insight = {
            "category": category,
            "category_name": category_info.get("category_name", category),
            "insight": f"Market analysis for {category}: {context_summary[:150]}...",
            "key_findings": [
                "Market growth trend detected",
                "Regional demand patterns identified",
                "Seasonal variations observed"
            ],
            "confidence": 0.60,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "model_used": "fallback",
        }
    
    return {
        "category": category,
        "category_insight": category_insight,
    }


async def process_category_batch(
    batch_index: int,
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Process all products in a category batch with shared context.
    
    Input: Category batch index
    Output: Forecasts for all products in the category
    
    Purpose: Process products efficiently by sharing category-level insights.
    """
    category_batches = state.category_batches or []
    if batch_index >= len(category_batches):
        return {"batch_results": []}
    
    category_batch = category_batches[batch_index]
    category = category_batch["category"]
    products = category_batch["products"]
    
    print(f"\n{'='*60}")
    print(f"Processing Category: {category_batch.get('category_name', category)}")
    print(f"Products: {len(products)}")
    print(f"{'='*60}\n")
    
    # Step 1: Retrieve category-level context ONCE
    category_info = get_category_info(category)
    context_result = await retrieve_category_context(category, category_info, state, runtime)
    category_context = context_result.get("category_context", [])
    
    # Step 2: Analyze category-level insights ONCE
    analysis_result = await analyze_category_with_api(
        category, category_info, category_context, state, runtime
    )
    category_insight = analysis_result.get("category_insight", {})
    
    # Step 3: Process each product with shared category context
    batch_results = []
    for product_code in products:
        try:
            # Get product data
            product_data = get_product_by_code(product_code)
            
            # Fuse product-specific data with shared category insight
            fused_data = {
                "product_code": product_code,
                "internal_data": product_data,
                "market_insight": category_insight,  # Shared!
                "combined_features": {
                    "category": category,
                    "market_signal": category_insight.get("key_findings", []),
                    "historical_trend": "increasing",  # Simplified for MVP
                },
            }
            
            # Generate forecast using Prophet
            forecast = await generate_category_forecast(product_code, fused_data, state, runtime)
            
            batch_results.append({
                "product_code": product_code,
                "product_name": product_data.get("product_name"),
                "category": category,
                "forecast": forecast,
                "used_shared_category_insight": True,
            })
            
            print(f"✓ Completed forecast for {product_data.get('product_name')}")
        
        except Exception as e:
            print(f"✗ Error processing {product_code}: {e}")
            continue
    
    # Return as list for LangGraph reducer to merge parallel results
    return {
        "batch_results": [{
            "batch_index": batch_index,
            "category": category,
            "category_name": category_batch.get("category_name"),
            "batch_results": batch_results,
            "products_processed": len(batch_results),
            "shared_category_insight": category_insight,
        }]
    }


async def generate_category_forecast(
    product_code: str,
    fused_data: Dict[str, Any],
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Generate forecast for a product using Prophet with category insights.
    
    Similar to generate_forecast but optimized for category batching.
    """
    try:
        # Extract historical sales
        product_data = fused_data["internal_data"]
        historical_sales = product_data.get("historical_sales", [])
        
        if len(historical_sales) < 3:
            raise ValueError("Insufficient historical data")
        
        # Prepare data for Prophet
        df_data = []
        for sale in historical_sales:
            df_data.append({
                "ds": pd.to_datetime(sale["period"] + "-01"),
                "y": sale["quantity"]
            })
        
        df = pd.DataFrame(df_data)
        
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05,
            interval_width=0.80
        )
        
        # Fit model
        model.fit(df)
        
        # Forecast next 3 months
        future = model.make_future_dataframe(periods=3, freq='MS')
        forecast_df = model.predict(future)
        
        # Extract forecast months
        forecast_months = forecast_df.tail(3)
        
        # Apply market adjustment from category insights
        category_insight = fused_data["market_insight"]
        confidence = category_insight.get("confidence", 0.5)
        key_findings = category_insight.get("key_findings", [])
        
        # Determine growth factor
        signal_text = " ".join(key_findings).lower()
        if "growth" in signal_text or "increasing" in signal_text or "surge" in signal_text:
            growth_factor = 1.0 + (confidence * 0.15)
        elif "declining" in signal_text or "decreasing" in signal_text:
            growth_factor = 1.0 - (confidence * 0.10)
        else:
            growth_factor = 1.0
        
        # Build monthly forecasts
        monthly_forecasts = []
        total_forecast = 0
        
        for _, row in forecast_months.iterrows():
            adjusted_forecast = row['yhat'] * growth_factor
            adjusted_lower = row['yhat_lower'] * growth_factor
            adjusted_upper = row['yhat_upper'] * growth_factor
            
            monthly_forecasts.append({
                "month": row['ds'].strftime("%Y-%m"),
                "forecast": max(0, int(adjusted_forecast)),
                "lower": max(0, int(adjusted_lower)),
                "upper": max(0, int(adjusted_upper)),
            })
            total_forecast += max(0, int(adjusted_forecast))
        
        lower_total = sum([m["lower"] for m in monthly_forecasts])
        upper_total = sum([m["upper"] for m in monthly_forecasts])
        
        forecast = {
            "product_code": product_code,
            "forecast_period": "Q1_2025",
            "forecast_units": total_forecast,
            "monthly_breakdown": monthly_forecasts,
            "confidence_interval": {
                "lower": lower_total,
                "upper": upper_total,
            },
            "method": "prophet_with_category_insight",
            "category_growth_factor": round(growth_factor, 3),
            "model_confidence": round(confidence, 3),
            "forecast_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
    
    except Exception as e:
        print(f"Prophet failed for {product_code}: {e}. Using fallback.")
        
        # Simple fallback
        historical_sales = fused_data["internal_data"].get("historical_sales", [])
        recent_qty = historical_sales[-1]["quantity"] if historical_sales else 100
        
        monthly_forecast = int(recent_qty * 1.1)
        total_forecast = monthly_forecast * 3
        
        forecast = {
            "product_code": product_code,
            "forecast_period": "Q1_2025",
            "forecast_units": total_forecast,
            "monthly_breakdown": [
                {"month": "2025-01", "forecast": monthly_forecast, "lower": int(monthly_forecast * 0.85), "upper": int(monthly_forecast * 1.15)},
                {"month": "2025-02", "forecast": monthly_forecast, "lower": int(monthly_forecast * 0.85), "upper": int(monthly_forecast * 1.15)},
                {"month": "2025-03", "forecast": monthly_forecast, "lower": int(monthly_forecast * 0.85), "upper": int(monthly_forecast * 1.15)},
            ],
            "confidence_interval": {
                "lower": int(total_forecast * 0.85),
                "upper": int(total_forecast * 1.15),
            },
            "method": "fallback_rule_based",
            "forecast_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
    
    return forecast
