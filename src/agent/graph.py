"""AI Demand Forecasting Graph - New workflow with external data ingestion and parallel processing.

This module defines the LangGraph workflow for demand forecasting with:
- External data ingestion from public sources
- ChromaDB storage and retrieval
- Parallel batch processing
- ML-based forecasting
- Alert generation
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from agent.nodes_external_data import clean_and_tag, ingest_external_data, store_in_chromadb
from agent.nodes_output import aggregate_forecasts, output_and_alert
from agent.nodes_product_processing import process_product_batch, split_product_batches
from agent.types_new import Context, State


# Create batch processor functions
def create_batch_processor(batch_idx: int):
    """Create a batch processor function for a specific batch index."""

    async def batch_processor(
        state: State,
        runtime: Runtime[Context],
    ) -> Dict[str, Any]:
        """Process a specific batch of products."""
        return await process_product_batch(batch_idx, state, runtime)

    return batch_processor


# Define the graph
graph = StateGraph(State, context_schema=Context)

# Add nodes
graph.add_node("ingest", ingest_external_data)
graph.add_node("clean_tag", clean_and_tag)
graph.add_node("store_index", store_in_chromadb)
graph.add_node("split_batches", split_product_batches)
graph.add_node("aggregate", aggregate_forecasts)
graph.add_node("output_alert", output_and_alert)

# Add parallel batch processing nodes (5 batches)
for i in range(5):
    batch_node = f"process_batch_{i}"
    graph.add_node(batch_node, create_batch_processor(i))

# Sequential edges
graph.add_edge("__start__", "ingest")
graph.add_edge("ingest", "clean_tag")
graph.add_edge("clean_tag", "store_index")
graph.add_edge("store_index", "split_batches")
graph.add_edge("aggregate", "output_alert")

# Parallel edges: split_batches -> all batch processors
for i in range(5):
    batch_node = f"process_batch_{i}"
    graph.add_edge("split_batches", batch_node)
    graph.add_edge(batch_node, "aggregate")

# Compile the graph
graph = graph.compile(name="AI Demand Forecasting - External Data Workflow")
