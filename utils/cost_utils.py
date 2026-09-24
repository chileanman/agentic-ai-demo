"""Estimates what it would cost to run a file through the agent pipeline.

The demo simulates agent work rather than doing it, so these are illustrative
rates applied to the pipeline's own simulated numbers: the per-agent processing
times it reports, the file's complexity, and how many clarifying questions the
Question Agent raised.

Only the two costs the demo can actually ground are modelled. Storage and
egress are deliberately absent: nothing in this demo has a real file size
(``file_path`` points at an ``examples/`` directory that does not exist), so
those line items could only ever read $0.00 and would imply a precision the
simulation does not have.
"""

# Pricing assumptions (USD), illustrative only.
COMPUTE_COST_PER_SECOND = 0.0004  # ~$1.44 per compute hour
LLM_COST_PER_1K_TOKENS = 0.004  # ~$4.00 per million tokens

# A more complex file gives the agents more to read and reason about.
BASE_TOKENS_BY_COMPLEXITY = {
    "low": 300,
    "medium": 700,
    "high": 1500,
}

TOKENS_PER_QUESTION = 200


def estimate_token_usage(complexity, question_count):
    """Estimates tokens consumed for one file.

    Args:
        complexity (str): "low", "medium" or "high"; anything else is treated
            as "medium" so an unrecognised value degrades rather than raises.
        question_count (int): clarifying questions the Question Agent raised.

    Returns:
        int: estimated total tokens.
    """
    base_tokens = BASE_TOKENS_BY_COMPLEXITY.get(
        str(complexity).lower(), BASE_TOKENS_BY_COMPLEXITY["medium"]
    )
    return base_tokens + max(int(question_count), 0) * TOKENS_PER_QUESTION


def calculate_costs(agent_durations, complexity, question_count):
    """Builds the cost breakdown for one processed file.

    Args:
        agent_durations (dict): agent name -> seconds, as recorded in
            ``st.session_state.agent_times``. A None duration counts as zero
            so a partially-processed file still costs something rather than
            raising.
        complexity (str): the file's complexity band.
        question_count (int): clarifying questions raised for this file.

    Returns:
        dict: compute_cost, model_cost, total_cost, plus the compute_seconds
            and estimated_tokens they were derived from, so the dashboard can
            show the working rather than just the total.
    """
    compute_seconds = sum(
        float(duration or 0.0) for duration in agent_durations.values()
    )
    compute_cost = compute_seconds * COMPUTE_COST_PER_SECOND

    estimated_tokens = estimate_token_usage(complexity, question_count)
    model_cost = (estimated_tokens / 1000.0) * LLM_COST_PER_1K_TOKENS

    return {
        "compute_cost": compute_cost,
        "model_cost": model_cost,
        "total_cost": compute_cost + model_cost,
        "compute_seconds": compute_seconds,
        "estimated_tokens": estimated_tokens,
        "question_count": max(int(question_count), 0),
    }


def format_cost(amount):
    """Formats a USD amount, keeping sub-cent figures legible.

    Per-file costs here land in the thousandths of a dollar, where a plain
    two-decimal format would render every file as "$0.00".
    """
    return "${:,.4f}".format(float(amount))
