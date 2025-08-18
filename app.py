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
    page_icon="🤖",
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

# Initialize agents
email_agent = EmailAgent()
validation_agent = ValidationAgent()
question_agent = QuestionAgent()
transformation_agent = TransformationAgent()
upload_agent = UploadAgent()

# Main app layout
st.title("Agentic AI File Processing Demo")
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
        # Set status to processing to prevent duplicate processing
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
        
        # Process the file through the agent pipeline
        with st.spinner(f"Processing example {example_id}..."):
            # Email agent receives the file
            file_info = email_agent.receive_email(example_data)
            time.sleep(0.5)  # Simulate processing time
            
            # Track processing stage for visualization
            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "email"
            
            # Validation agent checks the file
            validation_result = validation_agent.validate_file(file_info)
            time.sleep(0.5)  # Simulate processing time
            
            # Track processing stage for visualization
            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "validation"
            
            # If validation requires questions, ask them
            if validation_result.get("needs_clarification", False):
                questions = question_agent.generate_questions(validation_result)
                st.session_state.questions_asked.append({
                    "example_id": example_id,
                    "questions": questions,
                    "answered": False,
                    "timestamp": datetime.now()
                })
                
                # Track processing stage for visualization
                if 'file_processing_stages' in st.session_state:
                    st.session_state.file_processing_stages[example_id] = "question"
                
                # Add log entry for questions asked
                st.session_state.agent_logs.append({
                    "timestamp": datetime.now(),
                    "agent": "Question Agent",
                    "action": f"Generated {len(questions)} questions about the file",
                    "status": "pending",
                    "duration": random.uniform(0.5, 1.5),
                    "file_id": example_id
                })
            
            # Transform the data
            transformed_data = transformation_agent.transform_data(file_info, validation_result)
            time.sleep(1.0)  # Simulate processing time
            
            # Track processing stage for visualization
            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "transform"
            
            # Upload the data
            storage_result = upload_agent.store_data(transformed_data)
            time.sleep(0.5)  # Simulate processing time
            
            # Track processing stage for visualization
            if 'file_processing_stages' in st.session_state:
                st.session_state.file_processing_stages[example_id] = "upload"
            
            # Update processed files list
            st.session_state.processed_files.append({
                "example_id": example_id,
                "filename": example_data["filename"],
                "file_type": example_data["file_type"],
                "sender": example_data["sender"],
                "subject": example_data["subject"],
                "received_time": datetime.now(),
                "processing_time": random.uniform(1.0, 5.0),
                "status": "Processed" if not validation_result.get("needs_clarification", False) else "Awaiting Clarification",
                "complexity": example_data["complexity"]
            })
            
            # Update processing status
            st.session_state.processing_status[example_id] = "complete"
            
            # Add final log entry
            st.session_state.agent_logs.append({
                "timestamp": datetime.now(),
                "agent": "Upload Agent",
                "action": f"Data uploaded successfully in common format",
                "status": "complete",
                "duration": random.uniform(0.3, 1.0),
                "file_id": example_id
            })
            
            # Check if there are more files in the queue to process
            if st.session_state.process_queue:
                # Get the next example from the queue
                next_example = st.session_state.process_queue.pop(0)
                
                # Make sure we're not trying to process an already processed file
                while (next_example in st.session_state.processing_status and 
                       st.session_state.processing_status[next_example] == "complete" and 
                       st.session_state.process_queue):
                    next_example = st.session_state.process_queue.pop(0)
                    if not st.session_state.process_queue:
                        break
                
                # Only set the next example if it's not already processed
                if next_example not in st.session_state.processing_status or \
                   st.session_state.processing_status[next_example] != "complete":
                    st.session_state.selected_example = next_example
                else:
                    st.session_state.selected_example = None
            else:
                st.session_state.selected_example = None
                
            # Add a small delay before rerunning to prevent race conditions
            time.sleep(0.1)
            
            # Force a rerun to update the UI
            st.experimental_rerun()
