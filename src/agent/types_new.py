"""Type definitions for the new demand forecasting agent workflow.

Contains State and Context definitions for the external data ingestion and parallel processing workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

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

    # Batch processing
    product_batches: List[List[str]] = field(default_factory=list)
    total_batches: int = 0
    total_products: int = 0

    # Batch results (from parallel processing)
    batch_results: List[Dict[str, Any]] = field(default_factory=list)

    # Aggregation
    aggregated_forecasts: Dict[str, Any] | None = None

    # Output
    output_file: str | None = None
    forecasts_saved: int = 0
    alerts_triggered: List[Dict[str, Any]] = field(default_factory=list)
    alert_summary: Dict[str, Any] | None = None
    report_generated: bool = False

