import streamlit as st
import time
from datetime import datetime
import pandas as pd
import json
import os
import random
from agents.email_agent import EmailAgent
from agents.validation_agent import ValidationAgent
from agents.question_agent import QuestionAgent
from agents.transformation_agent import TransformationAgent
from agents.upload_agent import UploadAgent
from utils.file_utils import load_example_files, get_example_metadata
from ui.dashboard import render_dashboard, render_agent_details, render_file_details
from ui.sidebar import render_sidebar

# Set page configuration
st.set_page_config(
    page_title="Agentic AI Demo",
    page_icon="/assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = []
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {}
if 'selected_example' not in st.session_state:
    st.session_state.selected_example = None
if 'process_queue' not in st.session_state:
    st.session_state.process_queue = []
if 'examples_metadata' not in st.session_state:
    st.session_state.examples_metadata = get_example_metadata()
if 'agent_times' not in st.session_state:
    st.session_state.agent_times = {}

# Initialize agents
email_agent = EmailAgent()
validation_agent = ValidationAgent()
question_agent = QuestionAgent()
transformation_agent = TransformationAgent()
upload_agent = UploadAgent()

# Force Dava Sans font globally
st.markdown("""
<style>
html, body, [class*="css"], p, div, h1, h2, h3, h4, h5, h6, input, textarea {
    font-family: 'Dava Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

styles = {
    "h1": "font-weight: 500; font-style: Medium; font-size: 32px; line-height: 120%; letter-spacing: 0%;",
    "span": "color: #A3AAAE;"
}
# Endava logo
st.image("./assets/logo.png", width=122)

# Main app layout
st.markdown(f'<h1 style="{styles["h1"]}">Agentic AI File Processing <span style="{styles["span"]}">Demo</span></h1>', unsafe_allow_html=True)
st.markdown("""
This demo showcases a team of AI agents working together to process files from partners and suppliers.
The agents receive files via email, validate them, ask clarifying questions when needed, 
transform the data into a common format, and prepare it for storage in core systems.
""")

# Render sidebar for example selection
render_sidebar()

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "Agent Details", "File Details"])

with tab1:
    render_dashboard()

with tab2:
    render_agent_details()

with tab3:
    render_file_details()

# Process selected example if any
if st.session_state.selected_example:
    example_id = st.session_state.selected_example
    example_data = st.session_state.examples_metadata[example_id]
    
    # Only process if not already processed or in progress
    if example_id not in st.session_state.processing_status or st.session_state.processing_status[example_id] != "complete":
        st.session_state.processing_status[example_id] = "processing"

        # Add log entry for email received
        st.session_state.agent_logs.append({
            "timestamp": datetime.now(),
            "agent": "Email Agent",
            "action": f"Received email from {example_data['sender']} with subject '{example_data['subject']}'",
            "status": "complete",
            "duration": random.uniform(0.5, 2.0),
            "file_id": example_id
        })

        with st.spinner(f"Processing example {example_id}..."):
            agent_times = {
                "Email Agent": 0.0,
                "Validation Agent": 0.0,
                "Question Agent": 0.0,
                "Transformation Agent": 0.0,
                "Upload Agent": 0.0,
            }

            # Email agent
            t0 = time.perf_counter()
            file_info = email_agent.receive_email(example_data)
            agent_times["Email Agent"] = time.perf_counter() - t0
            time.sleep(0.5)

            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "email"

            # Validation agent
            t0 = time.perf_counter()
            validation_result = validation_agent.validate_file(file_info)
            agent_times["Validation Agent"] = time.perf_counter() - t0
            time.sleep(0.5)

            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "validation"

            question_duration = 0.0
            if validation_result.get("needs_clarification", False):
                t0 = time.perf_counter()
                questions = question_agent.generate_questions(validation_result)
                question_duration = time.perf_counter() - t0
                st.session_state.questions_asked.append({
                    "example_id": example_id,
                    "questions": questions,
                    "answered": False,
                    "timestamp": datetime.now()
                })
                agent_times["Question Agent"] = question_duration

                if 'file_processing_stages' in st.session_state:
                    st.session_state.file_processing_stages[example_id] = "question"

                st.session_state.agent_logs.append({
                    "timestamp": datetime.now(),
                    "agent": "Question Agent",
                    "action": f"Generated {len(questions)} questions about the file",
                    "status": "pending",
                    "duration": question_duration,
                    "file_id": example_id
                })
            else:
                agent_times["Question Agent"] = 0.0

            # Transformation agent
            t0 = time.perf_counter()
            transformed_data = transformation_agent.transform_data(file_info, validation_result)
            agent_times["Transformation Agent"] = time.perf_counter() - t0
            time.sleep(1.0)

            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "transform"

            t0 = time.perf_counter()
            storage_result = upload_agent.store_data(transformed_data)
            agent_times["Upload Agent"] = time.perf_counter() - t0
            time.sleep(0.5)

            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "upload"

            st.session_state.agent_times[example_id] = agent_times
            total_time = sum(agent_times.values())

            # Update processed files list
            st.session_state.processed_files.append({
                "example_id": example_id,
                "filename": example_data["filename"],
                "file_type": example_data["file_type"],
                "sender": example_data["sender"],
                "subject": example_data["subject"],
                "received_time": datetime.now(),
                "processing_time": total_time,
                "status": "Processed" if not validation_result.get("needs_clarification", False) else "Awaiting Clarification",
                "complexity": example_data["complexity"]
            })

            st.session_state.processing_status[example_id] = "complete"

            st.session_state.agent_logs.append({
                "timestamp": datetime.now(),
                "agent": "Upload Agent",
                "action": f"Data uploaded successfully in common format",
                "status": "complete",
                "duration": agent_times["Upload Agent"],
                "file_id": example_id
            })

            if st.session_state.process_queue:
                next_example = st.session_state.process_queue.pop(0)
                while (next_example in st.session_state.processing_status and 
                       st.session_state.processing_status[next_example] == "complete" and 
                       st.session_state.process_queue):
                    next_example = st.session_state.process_queue.pop(0)
                    if not st.session_state.process_queue:
                        break

                if next_example not in st.session_state.processing_status or \
                   st.session_state.processing_status[next_example] != "complete":
                    st.session_state.selected_example = next_example
                else:
                    st.session_state.selected_example = None
            else:
                st.session_state.selected_example = None

            time.sleep(0.1)
            st.rerun()
