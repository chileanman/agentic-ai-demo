"""Tests for the per-file cost estimate.

The failure this guards against is a cost column that reads $0.0000 for every
file — which is what happens if compute time is not actually threaded through
from the agents, or if a sub-cent figure is formatted to two decimal places.
"""

import pytest

from utils.cost_utils import (
    BASE_TOKENS_BY_COMPLEXITY,
    COMPUTE_COST_PER_SECOND,
    LLM_COST_PER_1K_TOKENS,
    TOKENS_PER_QUESTION,
    calculate_costs,
    estimate_token_usage,
    format_cost,
)

AGENT_TIMES = {
    "Email Agent": 1.5,
    "Validation Agent": 0.8,
    "Question Agent": 0.3,
    "Transformation Agent": 2.4,
    "Upload Agent": 0.6,
}


def test_compute_cost_follows_the_reported_agent_times():
    """Compute cost must be derived from the pipeline's own timings, not a constant."""
    costs = calculate_costs(AGENT_TIMES, "medium", 0)

    assert costs["compute_seconds"] == pytest.approx(5.6)
    assert costs["compute_cost"] == pytest.approx(5.6 * COMPUTE_COST_PER_SECOND)


def test_slower_file_costs_more_than_a_faster_one():
    slow = calculate_costs({k: v * 2 for k, v in AGENT_TIMES.items()}, "medium", 0)
    fast = calculate_costs(AGENT_TIMES, "medium", 0)

    assert slow["total_cost"] > fast["total_cost"]


def test_total_is_the_sum_of_its_parts():
    costs = calculate_costs(AGENT_TIMES, "high", 3)

    assert costs["total_cost"] == pytest.approx(
        costs["compute_cost"] + costs["model_cost"]
    )


@pytest.mark.parametrize("complexity", ["low", "medium", "high"])
def test_every_cost_component_is_above_zero(complexity):
    """A file that used real time and real tokens must never show as free."""
    costs = calculate_costs(AGENT_TIMES, complexity, 0)

    assert costs["compute_cost"] > 0
    assert costs["model_cost"] > 0
    assert costs["total_cost"] > 0


def test_token_estimate_rises_with_complexity_and_questions():
    assert estimate_token_usage("high", 0) > estimate_token_usage("low", 0)
    assert estimate_token_usage("low", 2) == (
        BASE_TOKENS_BY_COMPLEXITY["low"] + 2 * TOKENS_PER_QUESTION
    )


def test_unknown_complexity_falls_back_to_medium():
    """An unrecognised band degrades rather than raising mid-pipeline."""
    assert estimate_token_usage("enormous", 0) == BASE_TOKENS_BY_COMPLEXITY["medium"]
    assert estimate_token_usage("HIGH", 0) == BASE_TOKENS_BY_COMPLEXITY["high"]


def test_model_cost_prices_the_estimated_tokens():
    costs = calculate_costs(AGENT_TIMES, "low", 1)
    expected_tokens = BASE_TOKENS_BY_COMPLEXITY["low"] + TOKENS_PER_QUESTION

    assert costs["estimated_tokens"] == expected_tokens
    assert costs["model_cost"] == pytest.approx(
        expected_tokens / 1000.0 * LLM_COST_PER_1K_TOKENS
    )


def test_missing_duration_counts_as_zero_rather_than_raising():
    costs = calculate_costs({"Email Agent": None, "Upload Agent": 1.0}, "low", 0)

    assert costs["compute_seconds"] == pytest.approx(1.0)


def test_negative_question_count_is_clamped():
    assert calculate_costs(AGENT_TIMES, "low", -5)["question_count"] == 0
    assert estimate_token_usage("low", -5) == BASE_TOKENS_BY_COMPLEXITY["low"]


def test_format_cost_keeps_sub_cent_amounts_visible():
    """Two decimal places would render every per-file cost as $0.00."""
    assert format_cost(0.0034) == "$0.0034"
    assert format_cost(0) == "$0.0000"
    assert format_cost(1234.5) == "$1,234.5000"
