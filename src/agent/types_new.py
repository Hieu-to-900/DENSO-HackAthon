"""Type definitions for the new demand forecasting agent workflow.

Contains State and Context definitions for the external data ingestion and parallel processing workflow.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List

from typing_extensions import TypedDict


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    """

    product_codes: List[str] | None
    chromadb_path: str | None
    xai_api_key: str | None
    num_batches: int


@dataclass
class State:
    """Input state for the new demand forecasting agent.

    Defines the structure of incoming data and intermediate results for the external data workflow.
    """

    # Input
    product_codes: List[str] = field(default_factory=list)

    # ========== Subgraph_DataCollection outputs ==========
    # Internal data (orders, inventory, production capacity)
    internal_data: Dict[str, Any] | None = None
    
    # Supply chain risk data (supplier status, logistics delays)
    supply_chain_risks: Dict[str, Any] | None = None
    
    # External data ingestion
    raw_external_data: List[Dict[str, Any]] | None = None
    ingestion_timestamp: str | None = None

    # Cleaning and tagging
    cleaned_external_data: List[Dict[str, Any]] | None = None
    cleaning_stats: Dict[str, Any] | None = None

    # ChromaDB storage
    chromadb_collection: str | None = None
    stored_document_ids: List[str] = field(default_factory=list)
    total_stored: int = 0
    storage_timestamp: str | None = None
    
    # Aggregated data from all sources
    aggregated_data: Dict[str, Any] | None = None

    # ========== Batch processing ==========
    # Legacy batch processing (random batching)
    product_batches: List[List[str]] = field(default_factory=list)
    total_batches: int = 0
    
    # Category-based batching (optimized)
    category_batches: List[Dict[str, Any]] = field(default_factory=list)
    total_categories: int = 0
    total_products: int = 0

    # Batch results (from parallel processing)
    # Use operator.add to automatically merge results from parallel category nodes
    batch_results: Annotated[List[Dict[str, Any]], operator.add] = field(default_factory=list)

    # Aggregation
    aggregated_forecasts: Dict[str, Any] | None = None

    # ========== Subgraph_Output outputs ==========
    # Capacity analysis
    capacity_analysis: Dict[str, Any] | None = None
    
    # Production suggestions
    production_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk alerts
    alerts_triggered: List[Dict[str, Any]] = field(default_factory=list)
    alert_summary: Dict[str, Any] | None = None
    
    # Notification
    notification_message: Dict[str, Any] | None = None
    notification_sent: bool = False
    notification_status: Dict[str, Any] | None = None

    # ========== Legacy/Output ==========
    output_file: str | None = None
    forecasts_saved: int = 0
    report_generated: bool = False

