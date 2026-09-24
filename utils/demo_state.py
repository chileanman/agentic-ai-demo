"""Single source of truth for the demo's session state.

Initialisation and "Reset Demo" were maintained as two separate hand-written
lists, and they drifted: `agent_times`, `file_costs` and
`file_processing_stages` were all created at startup but never cleared on
reset, so per-file detail from a previous run survived into the next one.

Both operations now read the same table, so a key added in one place cannot
be forgotten in the other.

These helpers take the state mapping as an argument rather than importing
Streamlit, so they can be tested against a plain dict.
"""

# Key -> zero-argument factory producing a fresh default value.
# Everything here is cleared by "Reset Demo".
DEMO_STATE_DEFAULTS = {
    "processed_files": list,
    "agent_logs": list,
    "questions_asked": list,
    "processing_status": dict,
    "selected_example": lambda: None,
    "process_queue": list,
    "agent_times": dict,
    "file_costs": dict,
    "file_processing_stages": dict,
}

# Static reference data. Initialised once and deliberately NOT cleared on
# reset: it describes the available examples, not the state of a demo run.
PERSISTENT_KEYS = frozenset({"examples_metadata"})


def initialise_session_state(state):
    """Fills in any missing demo key without disturbing existing values.

    Args:
        state: a mutable mapping, in practice ``st.session_state``.
    """
    for key, factory in DEMO_STATE_DEFAULTS.items():
        if key not in state:
            state[key] = factory()


def reset_demo_state(state):
    """Returns every demo key to a fresh default.

    A new container is built per key rather than mutating in place, so no
    caller keeps a live reference to the cleared list or dict. Keys in
    PERSISTENT_KEYS are left untouched.
    """
    for key, factory in DEMO_STATE_DEFAULTS.items():
        state[key] = factory()
