"""Utility functions for estimating processing costs."""
from __future__ import annotations

from typing import Dict

# Pricing assumptions (USD)
COMPUTE_COST_PER_SECOND = 0.0004  # Approx. $1.44 per compute hour
LLM_COST_PER_1000_TOKENS = 0.004  # $4.00 per 1M tokens
STORAGE_COST_PER_GB_MONTH = 0.023  # Standard cloud object storage pricing
EGRESS_COST_PER_GB = 0.09  # Typical inter-region/network egress rate

_BASE_TOKENS_BY_COMPLEXITY = {
    "low": 300,
    "medium": 700,
    "high": 1500,
}

TOKENS_PER_QUESTION = 200


def estimate_token_usage(complexity: str, question_count: int) -> int:
    """Estimate the number of tokens consumed based on file complexity and questions."""
    base_tokens = _BASE_TOKENS_BY_COMPLEXITY.get(complexity.lower(), _BASE_TOKENS_BY_COMPLEXITY["medium"])
    total_tokens = base_tokens + max(question_count, 0) * TOKENS_PER_QUESTION
    return total_tokens


def calculate_costs(
    agent_durations: Dict[str, float],
    complexity: str,
    question_count: int,
    file_size_bytes: float | int | None,
) -> Dict[str, float]:
    """Calculate the cost breakdown for a processed file."""
    compute_seconds = sum(float(duration or 0.0) for duration in agent_durations.values())
    compute_cost = compute_seconds * COMPUTE_COST_PER_SECOND

    estimated_tokens = estimate_token_usage(complexity, question_count)
    model_cost = (estimated_tokens / 1000.0) * LLM_COST_PER_1000_TOKENS

    file_size = float(file_size_bytes or 0.0)
    file_size_gb = file_size / (1024 ** 3)
    storage_cost = file_size_gb * STORAGE_COST_PER_GB_MONTH
    egress_cost = file_size_gb * EGRESS_COST_PER_GB

    total_cost = compute_cost + model_cost + storage_cost + egress_cost

    return {
        "compute_cost": compute_cost,
        "model_cost": model_cost,
        "storage_cost": storage_cost,
        "egress_cost": egress_cost,
        "total_cost": total_cost,
        "estimated_tokens": estimated_tokens,
        "compute_seconds": compute_seconds,
        "file_size_gb": file_size_gb,
        "question_count": max(question_count, 0),
    }
