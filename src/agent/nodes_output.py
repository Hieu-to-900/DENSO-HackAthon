"""Nodes for output and alerting."""

from __future__ import annotations

import json
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.types_new import Context, State


async def aggregate_forecasts(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Aggregate forecasts from all batches.

    Input: Batch results from parallel processing
    Output: Aggregated forecasts for all products

    Purpose: Combine forecasts from all parallel batches into a single result set.
    """
    # Collect all batch results
    batch_results_list = state.batch_results or []
    
    # Debug logging
    print(f"\n{'='*60}")
    print(f"[AGGREGATE] Received {len(batch_results_list)} batch results from parallel categories")
    print(f"{'='*60}")
    
    all_forecasts = []

    for batch_result in batch_results_list:
        category = batch_result.get("category", "unknown")
        batch_forecasts = batch_result.get("batch_results", [])
        print(f"  [BATCH] Category: {category} - {len(batch_forecasts)} products")
        
        if isinstance(batch_result, dict) and "batch_results" in batch_result:
            all_forecasts.extend(batch_result["batch_results"])

    # Aggregate statistics
    total_forecast_units = sum(
        item.get("forecast", {}).get("forecast_units", 0) for item in all_forecasts
    )
    avg_forecast = total_forecast_units / len(all_forecasts) if all_forecasts else 0

    aggregated = {
        "total_products": len(all_forecasts),
        "total_forecast_units": total_forecast_units,
        "average_forecast_per_product": avg_forecast,
        "forecasts": all_forecasts,
        "aggregation_timestamp": "2024-10-15T10:20:00",
    }

    return {
        "aggregated_forecasts": aggregated,
    }


async def output_and_alert(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, Any]:
    """Output forecast and trigger alerts if needed.

    Input: Aggregated forecasts
    Output: Saved forecast, report, alerts (if triggered)

    Purpose: Save forecast to JSON/DB, generate report, and trigger alert (Slack/email) if demand change >10% or critical.
    """
    aggregated = state.aggregated_forecasts or {}
    forecasts = aggregated.get("forecasts", [])

    # Calculate demand changes and check for alerts
    alerts = []
    for forecast_item in forecasts:
        forecast = forecast_item.get("forecast", {})
        product_code = forecast.get("product_code", "")
        forecast_units = forecast.get("forecast_units", 0)

        # Mock previous forecast for comparison (in real implementation, would fetch from DB)
        previous_forecast = forecast_units * 0.9  # Simulate 10% change
        change_percent = ((forecast_units - previous_forecast) / previous_forecast * 100) if previous_forecast > 0 else 0

        if abs(change_percent) > 10:
            alerts.append({
                "product_code": product_code,
                "alert_type": "demand_change",
                "change_percent": round(change_percent, 2),
                "message": f"Demand change of {change_percent:.1f}% detected for {product_code}",
                "severity": "high" if abs(change_percent) > 20 else "medium",
            })

    # Save to JSON (mock - in real implementation, would save to DB)
    output_data = {
        "forecasts": forecasts,
        "aggregated_stats": {
            "total_products": aggregated.get("total_products", 0),
            "total_forecast_units": aggregated.get("total_forecast_units", 0),
        },
        "alerts": alerts,
        "generated_at": "2024-10-15T10:25:00",
    }

    # Mock file save
    output_file = "forecasts_output.json"
    # In real implementation: json.dump(output_data, open(output_file, "w"), indent=2)

    # Mock alert sending (Slack/email)
    alert_summary = {
        "total_alerts": len(alerts),
        "high_severity": len([a for a in alerts if a["severity"] == "high"]),
        "medium_severity": len([a for a in alerts if a["severity"] == "medium"]),
    }

    return {
        "output_file": output_file,
        "forecasts_saved": len(forecasts),
        "alerts_triggered": alerts,
        "alert_summary": alert_summary,
        "report_generated": True,
    }

