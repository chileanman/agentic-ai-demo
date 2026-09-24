"""Regression tests for the simulated agent pipeline.

These pin the two failure modes the dashboard has actually hit: agents
reporting a constant (or zero) processing time, and the pipeline raising
part-way through a file.
"""

import pytest

from agents import question_agent
from agents.email_agent import EmailAgent
from agents.question_agent import QuestionAgent
from agents.transformation_agent import TransformationAgent
from agents.upload_agent import UploadAgent
from agents.validation_agent import ValidationAgent


def make_email(index, complexity):
    return {
        "filename": f"example_{index}.csv",
        "file_type": "csv",
        "sender": "Acme Corp",
        "sender_email": "files@acme.example",
        "subject": f"File {index}",
        "email_body": "",
        "complexity": complexity,
    }


def run_pipeline(index, complexity):
    """Runs one file through every agent and returns their reported times."""
    file_info = EmailAgent().receive_email(make_email(index, complexity))
    validation_result = ValidationAgent().validate_file(file_info)
    question_review = QuestionAgent().generate_questions(validation_result)
    transformed = TransformationAgent().transform_data(file_info, validation_result)
    stored = UploadAgent().store_data(transformed)

    return {
        "email": file_info["processing_time"],
        "validation": validation_result["processing_time"],
        "question": question_review["processing_time"],
        "transformation": transformed["processing_time"],
        "upload": stored["processing_time"],
    }


@pytest.mark.parametrize("complexity", ["low", "medium", "high"])
def test_every_agent_reports_a_positive_processing_time(complexity):
    times = run_pipeline(0, complexity)
    for agent, seconds in times.items():
        assert seconds > 0, f"{agent} reported {seconds}s"


def test_processing_times_differ_between_files():
    """The dashboard once showed an identical 0.1s for every agent on every file."""
    runs = [run_pipeline(i, "medium") for i in range(5)]
    for agent in runs[0]:
        reported = [run[agent] for run in runs]
        assert len(set(reported)) > 1, f"{agent} reported a constant {reported[0]}s"


def test_transformation_cost_scales_with_complexity():
    """Complexity multipliers make the low and high ranges disjoint (<=2.0s vs >=3.5s)."""
    low = max(run_pipeline(i, "low")["transformation"] for i in range(5))
    high = min(run_pipeline(i, "high")["transformation"] for i in range(5))
    assert high > low


def make_validation_result(index, needs_clarification):
    return {
        "file_info": EmailAgent().receive_email(make_email(index, "high")),
        "is_valid": True,
        "needs_clarification": needs_clarification,
        "issues": (
            [{"type": "Missing required fields", "severity": "high"}]
            if needs_clarification
            else []
        ),
        "processing_time": 1.0,
    }


def test_question_agent_average_smooths_rather_than_overwrites(monkeypatch):
    """Averaging over a hardcoded count of 1 silently replaces the running
    average with the latest sample instead of smoothing it.

    Triage times are pinned so this asserts the arithmetic exactly: an
    overwrite leaves 0.35, a true running mean leaves 0.30.
    """
    agent = QuestionAgent()
    # Built before the patch so the email agent still draws its own timings.
    validations = [make_validation_result(i, False) for i in range(5)]

    samples = iter([0.20, 0.30, 0.40, 0.25, 0.35])
    monkeypatch.setattr(question_agent.random, "uniform", lambda low, high: next(samples))

    for validation in validations:
        agent.generate_questions(validation)

    assert agent.performance_metrics["avg_processing_time"] == pytest.approx(0.30)
    assert agent.performance_metrics["files_reviewed"] == 5


@pytest.mark.parametrize("needs_clarification", [False, True])
def test_question_agent_reports_timing_in_its_return_value(needs_clarification):
    """The deployed app crashed reading a QuestionAgent attribute that Streamlit's
    stale module cache did not have. Timing must travel with the call, and a file
    needing no questions still costs a triage pass rather than reporting 0.
    """
    file_info = EmailAgent().receive_email(make_email(0, "high"))
    validation_result = {
        "file_info": file_info,
        "is_valid": True,
        "needs_clarification": needs_clarification,
        "issues": (
            [{"type": "Missing required fields", "severity": "high"}]
            if needs_clarification
            else []
        ),
        "processing_time": 1.0,
    }

    review = QuestionAgent().generate_questions(validation_result)

    assert sorted(review) == ["processing_time", "questions"]
    assert review["processing_time"] > 0
    assert isinstance(review["questions"], list)
    assert bool(review["questions"]) is needs_clarification


def test_pipeline_completes_for_every_complexity():
    """Guards the crash class: a file must never raise part-way through the agents."""
    for complexity in ["low", "medium", "high"]:
        for index in range(5):
            run_pipeline(index, complexity)
