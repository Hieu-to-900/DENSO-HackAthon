"""Nodes for external data ingestion and processing."""

from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.types_new import Context, State


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

    # Mock ChromaDB storage - replace with actual ChromaDB implementation
    # For now, simulate storage
    stored_ids = []
    for idx, item in enumerate(cleaned_data):
        # In real implementation, would:
        # 1. Generate embeddings for item["cleaned_content"]
        # 2. Store in ChromaDB with metadata
        stored_ids.append(f"doc_{idx}_{item['timestamp']}")

    return {
        "chromadb_collection": "external_market_data",
        "stored_document_ids": stored_ids,
        "total_stored": len(stored_ids),
        "storage_timestamp": "2024-10-15T10:05:00",
    }

