"""Nodes for external data ingestion and processing."""

from __future__ import annotations

import os
from typing import Any, Dict

from openai import AsyncOpenAI
from dotenv import load_dotenv
from langgraph.runtime import Runtime

from agent.types_new import Context, State

# Load environment variables from .env file
load_dotenv()


async def ingest_external_data(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Ingest external data from public sources (IEA, EV Volumes, Reuters, etc.).

    Input: None (starts the pipeline)
    Output: Raw external data (dict/list of documents)

    Purpose: Pull and extract raw market data from public sources via API, web scraping, or PDF parsing.
    """
    # Mock implementation - replace with actual API calls, web scraping, or PDF parsing
    # For now, return mock external data
    external_data = [
        {
            "source": "IEA",
            "content": "Global EV sales increased by 25% in Q3 2024",
            "timestamp": "2024-10-01",
            "type": "market_trend",
        },
        {
            "source": "EV Volumes",
            "content": "Battery demand up 18% due to new subsidies in EU",
            "timestamp": "2024-10-05",
            "type": "demand_signal",
        },
        {
            "source": "Reuters",
            "content": "Automotive supply chain disruptions easing",
            "timestamp": "2024-10-10",
            "type": "supply_chain",
        },
        {
            "source": "Bloomberg",
            "content": "China leads global EV production with 60% market share in 2024",
            "timestamp": "2024-10-12",
            "type": "market_trend",
        },
        {
            "source": "Automotive News",
            "content": "Power inverter efficiency standards tightened in North America",
            "timestamp": "2024-10-14",
            "type": "regulation",
        },
        {
            "source": "TechCrunch",
            "content": "Solid-state battery breakthrough promises 50% faster charging",
            "timestamp": "2024-10-15",
            "type": "technology",
        },
        {
            "source": "Financial Times",
            "content": "European automakers invest $50B in EV manufacturing capacity",
            "timestamp": "2024-10-16",
            "type": "investment",
        },
        {
            "source": "IEA",
            "content": "Global charging infrastructure grows 40% year-over-year",
            "timestamp": "2024-10-18",
            "type": "infrastructure",
        },
        {
            "source": "EV Volumes",
            "content": "Hybrid vehicle sales surge 30% as transition accelerates",
            "timestamp": "2024-10-20",
            "type": "market_trend",
        },
        {
            "source": "Reuters",
            "content": "Semiconductor shortage impacts inverter production schedules",
            "timestamp": "2024-10-22",
            "type": "supply_chain",
        },
        {
            "source": "Wall Street Journal",
            "content": "Tesla announces new inverter technology reducing costs by 20%",
            "timestamp": "2024-10-24",
            "type": "technology",
        },
        {
            "source": "Automotive World",
            "content": "Japanese suppliers expand EV component production in Southeast Asia",
            "timestamp": "2024-10-25",
            "type": "supply_chain",
        },
        {
            "source": "IEA",
            "content": "Battery raw material prices stabilize after 6-month volatility",
            "timestamp": "2024-10-26",
            "type": "market_trend",
        },
        {
            "source": "EV Volumes",
            "content": "US EV adoption rate reaches 8% of new vehicle sales",
            "timestamp": "2024-10-28",
            "type": "market_trend",
        },
        {
            "source": "Bloomberg",
            "content": "European Union mandates 15% EV charging stations by 2026",
            "timestamp": "2024-10-30",
            "type": "regulation",
        },
        {
            "source": "TechCrunch",
            "content": "AI-powered battery management systems improve efficiency by 12%",
            "timestamp": "2024-11-01",
            "type": "technology",
        },
        {
            "source": "Financial Times",
            "content": "Automotive OEMs form consortium for standardized inverter protocols",
            "timestamp": "2024-11-03",
            "type": "industry_collaboration",
        },
        {
            "source": "Automotive News",
            "content": "Supply chain resilience programs reduce component lead times by 25%",
            "timestamp": "2024-11-05",
            "type": "supply_chain",
        },
        {
            "source": "IEA",
            "content": "Global EV battery recycling capacity doubles in 2024",
            "timestamp": "2024-11-07",
            "type": "sustainability",
        },
        {
            "source": "EV Volumes",
            "content": "Fast-charging infrastructure investment reaches $10B globally",
            "timestamp": "2024-11-09",
            "type": "infrastructure",
        },
        {
            "source": "Reuters",
            "content": "Automotive suppliers report strong Q4 demand for power electronics",
            "timestamp": "2024-11-11",
            "type": "demand_signal",
        },
        {
            "source": "Wall Street Journal",
            "content": "New regulations require 30% domestic content for EV tax credits",
            "timestamp": "2024-11-13",
            "type": "regulation",
        },
        {
            "source": "Automotive World",
            "content": "Wireless charging technology gains traction in commercial fleets",
            "timestamp": "2024-11-15",
            "type": "technology",
        },
        {
            "source": "Bloomberg",
            "content": "Lithium-ion battery prices drop 15% due to oversupply",
            "timestamp": "2024-11-17",
            "type": "market_trend",
        },
        {
            "source": "TechCrunch",
            "content": "Vehicle-to-grid technology enables bidirectional power flow",
            "timestamp": "2024-11-19",
            "type": "technology",
        },
        {
            "source": "Financial Times",
            "content": "Automotive industry faces skilled labor shortage in EV manufacturing",
            "timestamp": "2024-11-21",
            "type": "supply_chain",
        },
        {
            "source": "IEA",
            "content": "Global EV fleet reaches 40 million vehicles milestone",
            "timestamp": "2024-11-23",
            "type": "market_trend",
        },
        {
            "source": "EV Volumes",
            "content": "Inverter cooling systems improve thermal efficiency by 18%",
            "timestamp": "2024-11-25",
            "type": "technology",
        },
    ]

    return {
        "raw_external_data": external_data,
        "ingestion_timestamp": "2024-10-15T10:00:00",
    }


async def clean_and_tag(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Clean and tag external data.

    Input: Raw external data
    Output: Cleaned and tagged data with metadata

    Purpose: Normalize, deduplicate, and tag external data (e.g., sentiment, region, EV trend) using Pandas and local NLP.
    """
    raw_data = state.raw_external_data or []

    # Mock cleaning and tagging
    cleaned_data = []
    for item in raw_data:
        cleaned_item = {
            **item,
            "cleaned_content": item["content"].lower().strip(),
            "tags": {
                "sentiment": "positive" if "increased" in item["content"].lower() or "up" in item["content"].lower() else "neutral",
                "region": "EU" if "EU" in item["content"] else "global",
                "ev_trend": True if "EV" in item["content"] or "electric" in item["content"].lower() else False,
                "product_relevance": "high" if "battery" in item["content"].lower() or "inverter" in item["content"].lower() else "medium",
            },
            "normalized": True,
        }
        cleaned_data.append(cleaned_item)

    return {
        "cleaned_external_data": cleaned_data,
        "cleaning_stats": {
            "total_items": len(raw_data),
            "cleaned_items": len(cleaned_data),
            "duplicates_removed": 0,
        },
    }


async def store_in_chromadb(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Store and index processed data in ChromaDB.

    Input: Cleaned and tagged data
    Output: Confirmation of storage with collection info

    Purpose: Embed processed data and store in local vector database with metadata (product relevance, timestamp).
    """
    cleaned_data = state.cleaned_external_data or []

    # Initialize OpenAI client for embeddings
    # Load API credentials from environment variables
    embedding_base_url = os.getenv("EMBEDDING_API_BASE_URL")
    embedding_api_key = os.getenv("EMBEDDING_API_KEY")
    
    if not embedding_api_key:
        raise ValueError("EMBEDDING_API_KEY environment variable is not set. Please check your .env file.")

    client = AsyncOpenAI(
        base_url=embedding_base_url,
        api_key=embedding_api_key
    )

    # Generate embeddings and prepare for storage
    stored_ids = []
    embeddings_data = []
    
    for idx, item in enumerate(cleaned_data):
        try:
            # Generate embedding for cleaned content (async call)
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=item["cleaned_content"]
            )            # Extract embedding vector
            embedding = response.data[0].embedding
            
            # Store embedding data (in real implementation, would store in ChromaDB)
            embeddings_data.append({
                "id": f"doc_{idx}_{item['timestamp']}",
                "embedding": embedding,
                "metadata": {
                    "source": item.get("source"),
                    "timestamp": item.get("timestamp"),
                    "type": item.get("type"),
                    "tags": item.get("tags", {}),
                }
            })
            
            stored_ids.append(f"doc_{idx}_{item['timestamp']}")
        except Exception as e:
            # Log error but continue processing other items
            print(f"Error generating embedding for item {idx}: {e}")
            stored_ids.append(f"doc_{idx}_{item['timestamp']}")

    return {
        "chromadb_collection": "external_market_data",
        "stored_document_ids": stored_ids,
        "total_stored": len(stored_ids),
        "embeddings_generated": len(embeddings_data),
        "storage_timestamp": "2024-10-15T10:05:00",
    }

