"""Tests for demo session-state setup and reset.

The defect these pin: "Reset Demo" cleared six hand-listed keys while startup
created nine, so per-file agent timings, cost breakdowns and processing
stages survived a reset and leaked into the next run.
"""

import pytest

from utils.demo_state import (
    DEMO_STATE_DEFAULTS,
    PERSISTENT_KEYS,
    initialise_session_state,
    reset_demo_state,
)


def test_reset_clears_every_key_that_init_creates():
    """The drift itself: any key created at startup must also be reset."""
    state = {}
    initialise_session_state(state)
    created = set(state)

    reset_demo_state(state)

    assert created <= set(state)
    assert all(state[key] in ([], {}, None) for key in created)


@pytest.mark.parametrize("key", ["agent_times", "file_costs", "file_processing_stages"])
def test_reset_clears_the_keys_that_used_to_leak(key):
    """These three were initialised but never cleared before this change."""
    state = {}
    initialise_session_state(state)
    state[key] = {"example_1": "stale"}

    reset_demo_state(state)

    assert state[key] == {}


def test_reset_hands_back_fresh_containers():
    """A reset that mutated in place would leave old references live."""
    state = {}
    initialise_session_state(state)
    old_files = state["processed_files"]
    old_costs = state["file_costs"]
    old_files.append("stale")
    old_costs["example_1"] = "stale"

    reset_demo_state(state)

    assert state["processed_files"] == []
    assert state["file_costs"] == {}
    assert state["processed_files"] is not old_files
    assert state["file_costs"] is not old_costs


def test_init_does_not_clobber_existing_values():
    """Streamlit re-runs the script on every interaction; init must be a no-op then."""
    state = {"processed_files": ["already here"], "agent_times": {"example_1": {}}}

    initialise_session_state(state)

    assert state["processed_files"] == ["already here"]
    assert state["agent_times"] == {"example_1": {}}


def test_reset_leaves_static_reference_data_alone():
    """examples_metadata describes the available files, not the state of a run."""
    state = {"examples_metadata": {"example_1": {"filename": "a.csv"}}}
    initialise_session_state(state)

    reset_demo_state(state)

    assert state["examples_metadata"] == {"example_1": {"filename": "a.csv"}}


def test_persistent_keys_are_not_also_reset_keys():
    """A key in both tables would be contradictory."""
    assert PERSISTENT_KEYS.isdisjoint(DEMO_STATE_DEFAULTS)


def test_every_default_is_callable_and_yields_a_new_object():
    """A bare [] or {} in the table would be shared across every reset."""
    for key, factory in DEMO_STATE_DEFAULTS.items():
        assert callable(factory), key
        first, second = factory(), factory()
        if first is not None:
            assert first is not second, key
