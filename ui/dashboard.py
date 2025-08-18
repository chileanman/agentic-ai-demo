import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import random

# Import custom views
from ui.validation_view import render_validation_tab
from ui.transformation_view import render_transformation_tab

# Helper function to get agent color
def get_agent_color(agent_name):
    """Returns a color for the given agent name."""
    agent_colors = {
        "Email Agent": "blue",
        "Validation Agent": "green",
        "Question Agent": "orange",
        "Transformation Agent": "purple",
        "Upload Agent": "red"
    }
    return agent_colors.get(agent_name, "gray")

def render_dashboard():
    """
    Renders the main dashboard with key metrics and visualizations.
    """
    
    # Initialize selected file for detailed view if not exists
    if 'selected_file_for_details' not in st.session_state:
        st.session_state.selected_file_for_details = None
        
    # Initialize file processing stages tracking if not exists
    if 'file_processing_stages' not in st.session_state:
        st.session_state.file_processing_stages = {}

    st.header("Dashboard")
    
    # Display processing queue if any
    if st.session_state.process_queue:
        st.subheader("Processing Queue")
        queue_df = pd.DataFrame({
            "Position": list(range(1, len(st.session_state.process_queue) + 1)),
            "File ID": st.session_state.process_queue,
            "File Name": [st.session_state.examples_metadata[id]["filename"] 
                         for id in st.session_state.process_queue],
            "Sender": [st.session_state.examples_metadata[id]["sender"] 
                      for id in st.session_state.process_queue],
            "File Type": [st.session_state.examples_metadata[id]["file_type"] 
                         for id in st.session_state.process_queue]
        })
        st.dataframe(queue_df, use_container_width=True)
        
        # Show progress
        total_files = len(st.session_state.process_queue) + 1  # +1 for the current file
        processed = 0
        current = 1
        
        progress_text = f"Processing file 1 of {total_files}"
        progress_bar = st.progress(0, text=progress_text)
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_files = len(st.session_state.processed_files)
        st.metric("Files Processed", total_files)
    
    with col2:
        if total_files > 0:
            avg_time = sum(f["processing_time"] for f in st.session_state.processed_files) / total_files
            st.metric("Avg. Processing Time", f"{avg_time:.2f}s")
        else:
            st.metric("Avg. Processing Time", "0.00s")
    
    with col3:
        # Count unique senders
        if total_files > 0:
            unique_senders = len(set(f["sender"] for f in st.session_state.processed_files))
            st.metric("Unique Senders", unique_senders)
        else:
            st.metric("Unique Senders", 0)
    
    with col4:
        # Count files by complexity
        if total_files > 0:
            high_complexity = sum(1 for f in st.session_state.processed_files if f["complexity"] == "high")
            st.metric("High Complexity Files", high_complexity)
        else:
            st.metric("High Complexity Files", 0)
    
    # Create tabs for different visualizations
    tab1, tab2 = st.tabs(["Files by Type", "Processing Time"])
    
    with tab1:
        if st.session_state.processed_files:
            # Count files by type
            file_types = {}
            for file in st.session_state.processed_files:
                file_type = file["file_type"]
                if file_type in file_types:
                    file_types[file_type] += 1
                else:
                    file_types[file_type] = 1
            
            # Create a pie chart
            fig = px.pie(
                values=list(file_types.values()),
                names=list(file_types.keys()),
                title="Files Processed by Type",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
    
    with tab2:
        if st.session_state.processed_files:
            # Create a bar chart of processing times
            processing_data = pd.DataFrame({
                "File": [f["filename"] for f in st.session_state.processed_files],
                "Processing Time (s)": [f["processing_time"] for f in st.session_state.processed_files],
                "Complexity": [f["complexity"] for f in st.session_state.processed_files]
            })
            
            fig = px.bar(
                processing_data,
                x="File",
                y="Processing Time (s)",
                color="Complexity",
                title="Processing Time by File",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
    
    # Agent Activity Timeline moved to agent details section
    
    # File picker for detailed view
    st.subheader("File Processing Details")
    
    # Create file picker if there are processed files
    if st.session_state.processed_files:
        file_options = ["All Files (Overview)"] + [
            f"{f['filename']} - {f['sender']} - {f['file_type']}" 
            for f in st.session_state.processed_files
        ]
        
        selected_file_option = st.selectbox(
            "Select a file to view detailed processing information:",
            options=file_options,
            key="file_picker"
        )
        
        # Update selected file in session state
        if selected_file_option == "All Files (Overview)":
            st.session_state.selected_file_for_details = None
        else:
            # Extract the file index from the selection
            selected_index = file_options.index(selected_file_option) - 1  # -1 because of "All Files" option
            st.session_state.selected_file_for_details = st.session_state.processed_files[selected_index]["example_id"]
    else:
        st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        st.session_state.selected_file_for_details = None
    
    # Add a visual DAG of agent workflow
    st.subheader("Agent Workflow")
    
    # Create a DAG visualization using Plotly
    fig = go.Figure()
    
    # Define agent nodes
    agents = [
        {"id": "email", "name": "Email Agent", "x": 0, "y": 0, "color": "blue"},
        {"id": "validation", "name": "Validation Agent", "x": 1, "y": 0, "color": "green"},
        {"id": "question", "name": "Question Agent", "x": 1, "y": -1, "color": "orange"},
        {"id": "transform", "name": "Transformation Agent", "x": 2, "y": 0, "color": "purple"},
        {"id": "upload", "name": "Upload Agent", "x": 3, "y": 0, "color": "red"}
    ]
    
    # Get current processing stage for selected file
    current_stage = None
    if st.session_state.selected_file_for_details and st.session_state.selected_file_for_details in st.session_state.file_processing_stages:
        current_stage = st.session_state.file_processing_stages[st.session_state.selected_file_for_details]
    
    # Add nodes
    for agent in agents:
        # Determine if this agent is the current processing stage
        is_current_stage = (current_stage == agent["id"])
        
        # Adjust node size and color based on whether it's the current stage
        node_size = 40 if is_current_stage else 30
        node_color = agent["color"]
        node_opacity = 1.0 if is_current_stage else 0.7
        node_line_width = 2 if is_current_stage else 0
        node_line_color = "black" if is_current_stage else agent["color"]
        
        # Add node with appropriate styling
        fig.add_trace(go.Scatter(
            x=[agent["x"]],
            y=[agent["y"]],
            mode="markers+text",
            marker=dict(
                size=node_size, 
                color=node_color,
                opacity=node_opacity,
                line=dict(width=node_line_width, color=node_line_color)
            ),
            text=[agent["name"]],
            textposition="bottom center",
            name=agent["name"],
            hoverinfo="text",
            hovertext=agent["name"] + (" (Current Stage)" if is_current_stage else "")
        ))
    
    # Add edges
    edges = [
        {"from": "email", "to": "validation", "color": "gray"},
        {"from": "validation", "to": "question", "color": "orange", "dash": "dash"},
        {"from": "validation", "to": "transform", "color": "gray"},
        {"from": "question", "to": "transform", "color": "orange", "dash": "dash"},
        {"from": "transform", "to": "upload", "color": "gray"},
        {"from": "question", "to": "email", "color": "orange", "dash": "dash"}
    ]
    
    # Determine active edges based on current processing stage
    active_edges = []
    if current_stage:
        # Define which edges should be active based on the current stage
        stage_to_active_edges = {
            "email": [{"from": "email", "to": "validation"}],
            "validation": [{"from": "email", "to": "validation"}, {"from": "validation", "to": "transform"}],
            "question": [{"from": "email", "to": "validation"}, {"from": "validation", "to": "question"}, {"from": "question", "to": "transform"}],
            "transform": [{"from": "email", "to": "validation"}, {"from": "validation", "to": "transform"}, {"from": "transform", "to": "upload"}],
            "upload": [{"from": "email", "to": "validation"}, {"from": "validation", "to": "transform"}, {"from": "transform", "to": "upload"}]
        }
        active_edges = stage_to_active_edges.get(current_stage, [])
    
    for edge in edges:
        from_agent = next(a for a in agents if a["id"] == edge["from"])
        to_agent = next(a for a in agents if a["id"] == edge["to"])
        
        # Check if this edge is active based on current processing stage
        is_active_edge = False
        if current_stage:
            is_active_edge = any(ae["from"] == edge["from"] and ae["to"] == edge["to"] for ae in active_edges)
        
        # Adjust edge styling based on whether it's active
        edge_width = 3 if is_active_edge else 1.5
        # For inactive edges, use a lighter color to simulate opacity
        if is_active_edge:
            edge_color = edge.get("color", "gray")
        else:
            # Convert color to a lighter version to simulate opacity
            base_color = edge.get("color", "gray")
            # If it's a named color, we'll use a lighter version
            if base_color == "gray":
                edge_color = "lightgray"
            elif base_color == "orange":
                edge_color = "#FFCC99"  # Lighter orange
            elif base_color == "blue":
                edge_color = "#99CCFF"  # Lighter blue
            elif base_color == "green":
                edge_color = "#99FFCC"  # Lighter green
            elif base_color == "purple":
                edge_color = "#CC99FF"  # Lighter purple
            elif base_color == "red":
                edge_color = "#FF9999"  # Lighter red
            else:
                edge_color = base_color
        
        fig.add_trace(go.Scatter(
            x=[from_agent["x"], to_agent["x"]],
            y=[from_agent["y"], to_agent["y"]],
            mode="lines",
            line=dict(
                width=edge_width, 
                color=edge_color, 
                dash=edge.get("dash", "solid")
            ),
            hoverinfo="none",
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title="Agent Interaction Workflow",
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add file processing summary section
    st.subheader("Processing Summary")
    
    if st.session_state.selected_file_for_details:
        # Get the selected file details
        selected_file = next((f for f in st.session_state.processed_files if f["example_id"] == st.session_state.selected_file_for_details), None)
        
        if selected_file:
            # Display file information
            st.markdown(f"### File: {selected_file['filename']}")
            
            # Create columns for file metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Sender", selected_file['sender'])
            with col2:
                st.metric("File Type", selected_file['file_type'])
            with col3:
                st.metric("Complexity", selected_file['complexity'])
            with col4:
                st.metric("Processing Time", f"{selected_file['processing_time']:.2f}s")
            
            # Create a timeline of processing stages
            st.markdown("### Processing Timeline")
            
            # Get agent logs for this file
            file_logs = [log for log in st.session_state.agent_logs 
                        if log.get("file_id") == selected_file["example_id"] or 
                        ("example_id" in selected_file and log.get("action", "").find(selected_file["example_id"]) >= 0)]
            
            if file_logs:
                # Create a timeline dataframe
                timeline_data = []
                for log in file_logs:
                    timeline_data.append({
                        "Agent": log["agent"],
                        "Action": log["action"],
                        "Time": log["timestamp"],
                        "Duration": log.get("duration", 0),
                        "Status": log.get("status", "complete")
                    })
                
                timeline_df = pd.DataFrame(timeline_data)
                if not timeline_df.empty:
                    timeline_df = timeline_df.sort_values("Time")
                    
                    # Display the timeline
                    for i, row in timeline_df.iterrows():
                        with st.container():
                            html_content = f"<div style='border-left: 3px solid {get_agent_color(row['Agent'])}; padding-left: 10px; margin-bottom: 10px;'>"
                            html_content += f"<strong>{row['Time'].strftime('%H:%M:%S')}</strong> - {row['Agent']}<br/>"
                            html_content += f"{row['Action']}<br/>"
                            html_content += f"<small>Duration: {row['Duration']:.2f}s | Status: {row['Status']}</small>"
                            html_content += "</div>"
                            st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("No detailed processing logs available for this file.")
            
            # Add agent-specific metrics for this file
            st.markdown("### Agent Performance")
            
            # Create tabs for each agent's metrics
            agent_tabs = st.tabs(["Email Agent", "Validation Agent", "Question Agent", "Transformation Agent", "Upload Agent"])
            
            with agent_tabs[0]:  # Email Agent
                st.markdown("#### Email Processing Details")
                st.metric("Processing Time", f"{random.uniform(0.1, 0.5):.2f}s")
                st.markdown(f"**Subject:** {selected_file.get('subject', 'N/A')}")
                st.markdown(f"**Received:** {selected_file.get('received_time', 'N/A')}")
            
            with agent_tabs[1]:  # Validation Agent
                st.markdown("#### Validation Details")
                st.metric("Validation Time", f"{random.uniform(0.3, 1.0):.2f}s")
                
                # Show validation issues if any
                if "validation_issues" in selected_file and selected_file["validation_issues"]:
                    st.markdown("**Issues Found:**")
                    for issue in selected_file["validation_issues"]:
                        st.markdown(f"- {issue}")
                else:
                    st.success("No validation issues found")
            
            with agent_tabs[2]:  # Question Agent
                st.markdown("#### Clarification Questions")
                
                # Find questions for this file
                file_questions = [q for q in st.session_state.questions_asked 
                                if q["example_id"] == selected_file["example_id"]]
                
                if file_questions:
                    st.metric("Questions Generated", len(file_questions[0]["questions"]))
                    st.markdown("**Questions:**")
                    for i, question in enumerate(file_questions[0]["questions"]):
                        st.markdown(f"{i+1}. {question}")
                else:
                    st.info("No clarification questions were needed for this file.")
            
            with agent_tabs[3]:  # Transformation Agent
                st.markdown("#### Transformation Details")
                st.metric("Transformation Time", f"{random.uniform(0.5, 2.0):.2f}s")
                
                # Show sample of transformed data
                st.markdown("**Sample Transformed Data:**")
                sample_data = {
                    "id": "sample-123",
                    "timestamp": "2023-06-15T14:30:00Z",
                    "customer_id": "cust-456",
                    "product_code": "PROD-789",
                    "quantity": 5,
                    "unit_price": 29.99
                }
                st.json(sample_data)
            
            with agent_tabs[4]:  # Upload Agent
                st.markdown("#### Upload Details")
                st.metric("Upload Time", f"{random.uniform(0.2, 0.8):.2f}s")
                st.markdown("**Target Systems:**")
                st.markdown("- Core Transaction System")
                st.markdown("- Data Warehouse")
                st.markdown("- Reporting Database")
        else:
            st.error("Selected file details not found.")
    else:
        # Show aggregate metrics when no file is selected
        st.info("Select a specific file above to view detailed processing information.")
        
        if st.session_state.processed_files:
            # Calculate aggregate metrics
            total_files = len(st.session_state.processed_files)
            avg_processing_time = sum(f["processing_time"] for f in st.session_state.processed_files) / total_files
            
            # Display aggregate metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Files Processed", total_files)
            with col2:
                st.metric("Avg. Processing Time", f"{avg_processing_time:.2f}s")
            with col3:
                file_types = {}
                for file in st.session_state.processed_files:
                    file_type = file["file_type"]
                    if file_type in file_types:
                        file_types[file_type] += 1
                    else:
                        file_types[file_type] = 1
                most_common_type = max(file_types.items(), key=lambda x: x[1])[0]
                st.metric("Most Common File Type", most_common_type)
            with col4:
                high_complexity = sum(1 for f in st.session_state.processed_files if f["complexity"] == "high")
                st.metric("High Complexity Files", high_complexity)
            

            
            # Show agent performance comparison
            st.markdown("### Agent Performance Comparison")
            agent_perf = {
                "Email Agent": random.uniform(0.1, 0.5),
                "Validation Agent": random.uniform(0.3, 1.0),
                "Question Agent": random.uniform(0.2, 0.8),
                "Transformation Agent": random.uniform(0.5, 2.0),
                "Upload Agent": random.uniform(0.2, 0.8)
            }
            agent_perf_df = pd.DataFrame({
                "Agent": list(agent_perf.keys()),
                "Avg. Processing Time (s)": list(agent_perf.values())
            })
            fig = px.bar(agent_perf_df, x="Agent", y="Avg. Processing Time (s)", title="Average Processing Time by Agent")
            st.plotly_chart(fig, use_container_width=True)
            
            # Show processing time table by agent
            st.markdown("### Processing Time by Agent (seconds)")
            
            # Function to get agent processing times for a specific file
            def get_agent_times(file_id):
                agent_times = {
                    "Email Agent": 0.01,  # Minimum value to ensure >0
                    "Validation Agent": 0.01,
                    "Question Agent": 0.01,
                    "Transformation Agent": 0.01,
                    "Upload Agent": 0.01
                }
                
                # Extract agent-specific processing times from agent_logs
                for log in st.session_state.agent_logs:
                    if "file_id" in log and log["file_id"] == file_id:
                        agent = log["agent"]
                        if agent in agent_times:
                            # Add to the minimum value to ensure >0
                            agent_times[agent] = max(0.01, agent_times[agent] + log["duration"])
                    # For backward compatibility with existing logs that might not have file_id
                    elif "example_id" in log and log["example_id"] == file_id:
                        agent = log["agent"]
                        if agent in agent_times:
                            # Add to the minimum value to ensure >0
                            agent_times[agent] = max(0.01, agent_times[agent] + log["duration"])
                
                return agent_times
            
            if st.session_state.processed_files:
                # Create a dataframe with processing times by agent for each file
                data = []
                for file in st.session_state.processed_files:
                    file_id = file["example_id"]
                    agent_times = get_agent_times(file_id)
                    
                    # Calculate total processing time
                    total_time = sum(agent_times.values())
                    
                    # Add row to data
                    row = {
                        "File ID": file_id,
                        "Filename": file["filename"],
                        "Email Agent": round(agent_times["Email Agent"], 2),
                        "Validation Agent": round(agent_times["Validation Agent"], 2),
                        "Question Agent": round(agent_times["Question Agent"], 2),
                        "Transformation Agent": round(agent_times["Transformation Agent"], 2),
                        "Upload Agent": round(agent_times["Upload Agent"], 2),
                        "Total": round(total_time, 2)
                    }
                    data.append(row)
                
                # Create dataframe
                df = pd.DataFrame(data)
                
                # Calculate averages
                avg_row = {
                    "File ID": "Average",
                    "Filename": "",
                }
                
                for agent in ["Email Agent", "Validation Agent", "Question Agent", "Transformation Agent", "Upload Agent", "Total"]:
                    avg_row[agent] = round(df[agent].mean(), 2)
                
                # Add average row
                df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
                
                # Pagination
                if len(df) > 21:  # 20 files + 1 average row
                    # Keep only the last 20 files + average row
                    df = pd.concat([df.iloc[-21:-1], df.iloc[-1:]], ignore_index=True)
                
                # Display the table without color highlighting
                st.dataframe(df, use_container_width=True)

def render_file_details():
    """
    Renders detailed information about processed files.
    """
    st.header("File Details")
    
    # Add tabs for different views
    file_tab, email_tab, validation_tab, transformation_tab = st.tabs(["File Info", "Email Communication", "Validation Details", "Data Transformation"])
    
    # File Info Tab
    with file_tab:
        if not st.session_state.processed_files:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
            return
    
        # File selection
        file_options = [f"{f['example_id']}: {f['filename']}" for f in st.session_state.processed_files]
        selected_file = st.selectbox("Select a file to view details", file_options)
    
        if selected_file:
            file_id = selected_file.split(":")[0].strip()
            file = next((f for f in st.session_state.processed_files if f["example_id"] == file_id), None)
        
        if file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("File Information")
                st.markdown(f"**Filename:** {file['filename']}")
                st.markdown(f"**File Type:** {file['file_type']}")
                st.markdown(f"**Sender:** {file['sender']}")
                st.markdown(f"**Subject:** {file['subject']}")
                st.markdown(f"**Received:** {file['received_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Processing Time:** {file['processing_time']:.2f}s")
                st.markdown(f"**Status:** {file['status']}")
                st.markdown(f"**Complexity:** {file['complexity']}")
            
            with col2:
                st.subheader("Processing Timeline")
                
                # Filter logs for this file
                file_logs = [log for log in st.session_state.agent_logs if file_id in log.get("action", "")]
                
                if file_logs:
                    for log in file_logs:
                        with st.container():
                            status_color = "green" if log["status"] == "complete" else "orange" if log["status"] == "pending" else "red"
                            html_content = "<div style='padding: 10px; border-left: 5px solid " + status_color + ";'>"
                            html_content += "<strong>" + log['timestamp'].strftime('%H:%M:%S') + "</strong> - <strong>" + log['agent'] + "</strong><br/>"
                            html_content += log['action'] + "<br/>"
                            html_content += "<em>Duration: " + f"{log['duration']:.2f}" + "s</em>"
                            html_content += "</div>"
                            st.markdown(html_content, unsafe_allow_html=True)
                            st.markdown("---")
                else:
                    st.info("No detailed logs available for this file")
            
            # Check if there are questions for this file
            file_questions = next((q for q in st.session_state.questions_asked if q["example_id"] == file_id), None)
            
            if file_questions:
                st.subheader("Clarification Questions")
                for i, question in enumerate(file_questions["questions"]):
                    with st.expander(f"Question {i+1} - {question['priority']} priority"):
                        st.markdown(f"**Question:** {question['question']}")
                        st.markdown(f"**Context:** {question['context']}")
                        
                        # Add simulated response if not answered
                        if not file_questions.get("answered", False):
                            st.text_input("Your response:", key=f"response_{file_id}_{i}", 
                                         placeholder="Type your response here...")
                            if st.button("Send Response", key=f"send_{file_id}_{i}"):
                                st.success("Response sent! The agent will process your answer.")
                                # In a real app, this would trigger further processing
    
    # Email Communication Tab
    with email_tab:
        if not st.session_state.processed_files:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        elif 'selected_file' in locals():
            file_id = selected_file.split(":")[0].strip()
            file = next((f for f in st.session_state.processed_files if f["example_id"] == file_id), None)
            
            if file:
                st.subheader("Email Communication")
                
                # Incoming Email
                with st.expander("Incoming Email", expanded=True):
                    sender_email = file['sender'].lower().replace(' ', '.')
                    html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                    html_content += "<strong>From:</strong> " + file['sender'] + " &lt;" + sender_email + "@example.com&gt;<br/>"
                    html_content += "<strong>To:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                    html_content += "<strong>Subject:</strong> " + file['subject'] + "<br/>"
                    html_content += "<strong>Date:</strong> " + file['received_time'].strftime('%a, %d %b %Y %H:%M:%S') + "<br/>"
                    html_content += "<strong>Attachments:</strong> " + file['filename'] + "<br/>"
                    html_content += "<hr/>"
                    html_content += "<p>Hello Data Processing Team,</p>"
                    html_content += "<p>Please find attached the latest data file for processing.</p>"
                    html_content += "<p>We need this processed as soon as possible for our monthly reporting.</p>"
                    html_content += "<p>Thank you for your assistance.</p>"
                    html_content += "<p>Best regards,<br/>" + file['sender'] + "</p>"
                    html_content += "</div>"
                    st.markdown(html_content, unsafe_allow_html=True)
                
                # Questions Email (if any)
                file_questions = next((q for q in st.session_state.questions_asked if q["example_id"] == file_id), None)
                if file_questions:
                    with st.expander("Outgoing Email - Clarification Questions", expanded=True):
                        # Format questions
                        questions_text = "\n".join([f"{i+1}. {q['question']}" for i, q in enumerate(file_questions["questions"])])
                        questions_html = questions_text.replace('\n', '<br/>')
                        sender_first_name = file['sender'].split()[0]
                        
                        html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                        html_content += "<strong>From:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                        html_content += "<strong>To:</strong> " + file['sender'] + " &lt;" + sender_email + "@example.com&gt;<br/>"
                        html_content += "<strong>Subject:</strong> Re: " + file['subject'] + " - Clarification Needed<br/>"
                        html_content += "<strong>Date:</strong> " + (file['received_time'] + timedelta(minutes=5)).strftime('%a, %d %b %Y %H:%M:%S') + "<br/>"
                        html_content += "<hr/>"
                        html_content += "<p>Hello " + sender_first_name + ",</p>"
                        html_content += "<p>Thank you for sending the data file. Before we can complete processing, we need clarification on a few points:</p>"
                        html_content += "<p>" + questions_html + "</p>"
                        html_content += "<p>Your prompt response will help us process this data accurately and efficiently.</p>"
                        html_content += "<p>Best regards,<br/>Data Processing Team</p>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
                
                # Confirmation Email
                if file['status'] == "Processed":
                    with st.expander("Outgoing Email - Processing Confirmation", expanded=True):
                        sender_first_name = file['sender'].split()[0]
                        html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                        html_content += "<strong>From:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                        html_content += "<strong>To:</strong> " + file['sender'] + " &lt;" + sender_email + "@example.com&gt;<br/>"
                        html_content += "<strong>Subject:</strong> Re: " + file['subject'] + " - Processing Complete<br/>"
                        html_content += "<strong>Date:</strong> " + (file['received_time'] + timedelta(minutes=15)).strftime('%a, %d %b %Y %H:%M:%S') + "<br/>"
                        html_content += "<hr/>"
                        html_content += "<p>Hello " + sender_first_name + ",</p>"
                        html_content += "<p>We have successfully processed the data file you sent (" + file['filename'] + ").</p>"
                        html_content += "<p>The data has been transformed into our standard format and loaded into the following systems:</p>"
                        html_content += "<ul>"
                        html_content += "<li>Core Transaction System</li>"
                        html_content += "<li>Data Warehouse</li>"
                        html_content += "</ul>"
                        html_content += "<p>Processing Summary:</p>"
                        html_content += "<ul>"
                        html_content += "<li>Records Processed: " + str(random.randint(10, 100)) + "</li>"
                        html_content += "<li>Processing Time: " + f"{file['processing_time']:.2f}" + " seconds</li>"
                        html_content += "<li>Validation Status: Passed</li>"
                        html_content += "</ul>"
                        html_content += "<p>If you have any questions or need further assistance, please let us know.</p>"
                        html_content += "<p>Best regards,<br/>Data Processing Team</p>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
    
    # Validation Details Tab
    with validation_tab:
        if not st.session_state.processed_files:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        elif 'selected_file' in locals():
            render_validation_tab(selected_file)
    
    # Data Transformation Tab
    with transformation_tab:
        if not st.session_state.processed_files:
            st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        elif 'selected_file' in locals():
            render_transformation_tab(selected_file)

def render_agent_info(name, description, capabilities, metrics):
    """
    Renders information about an AI agent.
    """
    st.subheader(name)
    st.markdown(description)
    
    with st.expander("Capabilities"):
        for capability in capabilities:
            st.markdown(f"- {capability}")
    
    cols = st.columns(len(metrics))
    for i, (metric_name, metric_value) in enumerate(metrics.items()):
        with cols[i]:
            st.metric(metric_name, metric_value)

def render_agent_details():
    """
    Renders detailed information about AI agents.
    """
    st.header("Agent Details")
    
    # Create tabs for each agent type
    email_tab, validation_tab, question_tab, transform_tab, storage_tab = st.tabs([
        "Email Agent", "Validation Agent", "Question Agent", "Transformation Agent", "Storage Agent"
    ])
    
    # Email Agent Tab
    with email_tab:
        st.subheader("Email Agent")
        st.markdown("Handles incoming emails, extracts attachments, and routes files to the appropriate processing pipeline.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Emails Processed", len(st.session_state.processed_files))
        with col2:
            st.metric("Avg. Response Time", f"{random.uniform(0.5, 2.0):.2f}s")
        with col3:
            st.metric("Success Rate", f"{random.uniform(95, 99.9):.1f}%")
        
        # Capabilities
        with st.expander("Capabilities", expanded=True):
            st.markdown("- Email parsing and classification")
            st.markdown("- Attachment extraction and validation")
            st.markdown("- Sender verification and prioritization")
            st.markdown("- Response generation and sending")
        
        # Processing Details
        with st.expander("Processing Details", expanded=True):
            st.markdown("### Email Processing Workflow")
            st.markdown("""
            1. **Receive Email**: Parse incoming email metadata (sender, subject, timestamp)
            2. **Extract Attachments**: Identify and extract file attachments
            3. **Validate Sender**: Check sender against known partners/suppliers
            4. **Classify Email**: Determine priority and processing path
            5. **Route to Processing**: Send to appropriate validation agent
            """)
            
            # Show sample email processing
            if st.session_state.processed_files:
                st.markdown("### Recent Email Processing")
                for file in st.session_state.processed_files[-3:]:  # Show last 3 processed files
                    with st.container():
                        sender_email = file['sender'].lower().replace(' ', '.')
                        html_content = "<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                        html_content += "<strong>From:</strong> " + file['sender'] + " &lt;" + sender_email + "@example.com&gt;<br/>"
                        html_content += "<strong>Subject:</strong> " + file['subject'] + "<br/>"
                        html_content += "<strong>Received:</strong> " + file['received_time'].strftime('%Y-%m-%d %H:%M:%S') + "<br/>"
                        html_content += "<strong>Attachment:</strong> " + file['filename'] + "<br/>"
                        html_content += "<strong>Processing Time:</strong> " + f"{random.uniform(0.1, 0.5):.2f}s" + "<br/>"
                        html_content += "<strong>Status:</strong> Processed" + "<br/>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("No emails have been processed yet. Select an example from the sidebar to begin.")
        
        # Performance Metrics
        with st.expander("Performance Metrics"):
            # Create some random performance data
            dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
            performance_data = pd.DataFrame({
                'Date': dates,
                'Emails Received': [random.randint(5, 20) for _ in range(7)],
                'Processing Time (s)': [random.uniform(0.3, 1.5) for _ in range(7)]
            })
            
            st.line_chart(performance_data.set_index('Date')['Emails Received'])
            st.line_chart(performance_data.set_index('Date')['Processing Time (s)'])
    
    # Validation Agent Tab
    with validation_tab:
        st.subheader("Validation Agent")
        st.markdown("Validates incoming data files for format correctness, data integrity, and business rule compliance.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Validated", len(st.session_state.processed_files))
        with col2:
            st.metric("Avg. Validation Time", f"{random.uniform(0.3, 1.5):.2f}s")
        with col3:
            issues_detected = random.randint(0, 10)
            st.metric("Issues Detected", issues_detected)
        
        # Capabilities
        with st.expander("Capabilities", expanded=True):
            st.markdown("- File format validation")
            st.markdown("- Data schema validation")
            st.markdown("- Business rule checking")
            st.markdown("- Error detection and reporting")
        
        # Processing Details
        with st.expander("Processing Details", expanded=True):
            st.markdown("### Validation Workflow")
            st.markdown("""
            1. **Format Check**: Verify file format matches expected type
            2. **Schema Validation**: Check data structure against expected schema
            3. **Data Type Validation**: Ensure data types match expectations
            4. **Business Rule Validation**: Apply business-specific validation rules
            5. **Issue Detection**: Identify and categorize validation issues
            6. **Decision Point**: Route to question agent or transformation agent
            """)
            
            # Show sample validation issues
            st.markdown("### Common Validation Issues")
            validation_issues = [
                {"type": "Missing Data", "severity": "High", "frequency": "32%", "description": "Required fields are empty or null"},
                {"type": "Format Error", "severity": "Medium", "frequency": "28%", "description": "Data not in expected format (e.g., dates, numbers)"},
                {"type": "Duplicate Records", "severity": "Low", "frequency": "15%", "description": "Multiple entries with same key identifiers"},
                {"type": "Range Violation", "severity": "Medium", "frequency": "12%", "description": "Values outside acceptable ranges"},
                {"type": "Inconsistent Data", "severity": "High", "frequency": "8%", "description": "Data conflicts with other records or systems"},
                {"type": "Other", "severity": "Various", "frequency": "5%", "description": "Miscellaneous validation issues"}
            ]
            
            validation_df = pd.DataFrame(validation_issues)
            st.dataframe(validation_df, use_container_width=True)
        
        # Performance Metrics
        with st.expander("Performance Metrics"):
            # Create some random performance data
            file_types = ['CSV', 'Excel', 'JSON', 'Word', 'PDF']
            validation_perf = pd.DataFrame({
                'File Type': file_types,
                'Avg. Validation Time (s)': [random.uniform(0.2, 1.5) for _ in range(5)],
                'Issue Rate (%)': [random.uniform(5, 25) for _ in range(5)]
            })
            
            st.bar_chart(validation_perf.set_index('File Type')['Avg. Validation Time (s)'])
            st.bar_chart(validation_perf.set_index('File Type')['Issue Rate (%)'])
    
    # Question Generation Agent Tab
    with question_tab:
        st.subheader("Question Generation Agent")
        st.markdown("Generates clarifying questions when data validation issues are detected.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Generated", len(st.session_state.questions_asked))
        with col2:
            st.metric("Avg. Generation Time", f"{random.uniform(0.2, 1.0):.2f}s")
        with col3:
            st.metric("Response Rate", f"{random.uniform(80, 95):.1f}%")
        
        # Capabilities
        with st.expander("Capabilities", expanded=True):
            st.markdown("- Context-aware question generation")
            st.markdown("- Priority-based question sorting")
            st.markdown("- Response processing and integration")
            st.markdown("- Follow-up question generation")
        
        # Processing Details
        with st.expander("Processing Details", expanded=True):
            st.markdown("### Question Generation Workflow")
            st.markdown("""
            1. **Analyze Issues**: Review validation issues to identify areas needing clarification
            2. **Generate Questions**: Create specific questions to resolve data issues
            3. **Prioritize Questions**: Rank questions by importance and impact
            4. **Format Email**: Create email with questions for sender
            5. **Process Responses**: Integrate answers back into data processing
            """)
            
            # Show sample questions
            st.markdown("### Sample Clarification Questions")
            if st.session_state.questions_asked:
                for q_item in st.session_state.questions_asked[:3]:  # Show first 3 question sets
                    st.markdown(f"**File:** {q_item['example_id']}")
                    for i, question in enumerate(q_item['questions']):
                        with st.container():
                            priority_color = "red" if question['priority'] == "high" else "orange" if question['priority'] == "medium" else "blue"
                            html_content = "<div style='border: 1px solid " + priority_color + "; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                            html_content += "<strong>Question " + str(i+1) + ":</strong> " + question['question'] + "<br/>"
                            html_content += "<strong>Priority:</strong> <span style='color: " + priority_color + ";'>" + question['priority'] + "</span><br/>"
                            html_content += "<strong>Context:</strong> " + question['context'] + "<br/>"
                            html_content += "</div>"
                            st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("No questions have been generated yet. Select an example from the sidebar to begin.")
        
        # Performance Metrics
        with st.expander("Performance Metrics"):
            # Create some random performance data
            question_types = ['Missing Data', 'Format Issues', 'Business Rules', 'Inconsistencies', 'Other']
            question_perf = pd.DataFrame({
                'Question Type': question_types,
                'Frequency': [random.randint(5, 30) for _ in range(5)],
                'Avg. Response Time (hrs)': [random.uniform(1, 24) for _ in range(5)]
            })
            
            st.bar_chart(question_perf.set_index('Question Type')['Frequency'])
            st.bar_chart(question_perf.set_index('Question Type')['Avg. Response Time (hrs)'])
    
    # Transformation Agent Tab
    with transform_tab:
        st.subheader("Transformation Agent")
        st.markdown("Transforms data from various formats into a standardized structure for downstream processing.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Transformed", len(st.session_state.processed_files))
        with col2:
            st.metric("Avg. Transform Time", f"{random.uniform(0.5, 2.0):.2f}s")
        with col3:
            st.metric("Formats Supported", 5)
        
        # Capabilities
        with st.expander("Capabilities", expanded=True):
            st.markdown("- Multi-format data parsing (CSV, Excel, JSON, Word, PDF)")
            st.markdown("- Schema mapping and normalization")
            st.markdown("- Data enrichment and augmentation")
            st.markdown("- Output formatting and validation")
        
        # Processing Details
        with st.expander("Processing Details", expanded=True):
            st.markdown("### Transformation Workflow")
            st.markdown("""
            1. **Parse Input**: Extract data from source format
            2. **Map Schema**: Map source fields to target schema
            3. **Normalize Data**: Standardize formats, units, and representations
            4. **Enrich Data**: Add derived or supplementary information
            5. **Format Output**: Structure data in standard output format
            6. **Validate Result**: Verify transformed data meets requirements
            """)
            
            # Show sample transformations
            st.markdown("### Transformation Examples by File Type")
            
            # Create tabs for different file types
            csv_tab, excel_tab, json_tab, word_tab, pdf_tab = st.tabs(["CSV", "Excel", "JSON", "Word", "PDF"])
            
            with csv_tab:
                st.markdown("#### CSV Transformation")
                st.markdown("**Input Format:** Comma-separated values with header row")
                st.markdown("**Processing Steps:**")
                st.markdown("1. Parse CSV structure and detect delimiter")
                st.markdown("2. Map column headers to standard schema")
                st.markdown("3. Convert data types and normalize values")
                st.markdown("4. Generate standardized output")
                st.markdown("**Avg. Processing Time:** 0.3s")
                
                # Sample before/after
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Before:**")
                    st.code("""date,client_id,value,category
2023-01-15,A123,1500.50,Insurance
2023-01-16,B456,750.25,Benefits
2023-01-17,C789,2100.75,Retirement""", language="csv")
                with col2:
                    st.markdown("**After:**")
                    st.code("""{
  "records": [
    {
      "transaction_date": "2023-01-15",
      "client_identifier": "A123",
      "transaction_amount": 1500.50,
      "transaction_category": "INSURANCE"
    },
    ...
  ]
}""", language="json")
            
            with excel_tab:
                st.markdown("#### Excel Transformation")
                st.markdown("**Input Format:** Excel workbook with multiple sheets")
                st.markdown("**Processing Steps:**")
                st.markdown("1. Identify relevant sheets and data ranges")
                st.markdown("2. Extract tabular data and handle merged cells")
                st.markdown("3. Process formulas and calculated values")
                st.markdown("4. Map to standard schema and normalize")
                st.markdown("**Avg. Processing Time:** 0.8s")
            
            with json_tab:
                st.markdown("#### JSON Transformation")
                st.markdown("**Input Format:** Nested JSON objects and arrays")
                st.markdown("**Processing Steps:**")
                st.markdown("1. Parse JSON structure")
                st.markdown("2. Flatten nested objects as needed")
                st.markdown("3. Map fields to standard schema")
                st.markdown("4. Normalize and validate data types")
                st.markdown("**Avg. Processing Time:** 0.4s")
            
            with word_tab:
                st.markdown("#### Word Document Transformation")
                st.markdown("**Input Format:** Formatted text with tables and sections")
                st.markdown("**Processing Steps:**")
                st.markdown("1. Extract text content and table data")
                st.markdown("2. Identify document structure and sections")
                st.markdown("3. Parse tables into structured data")
                st.markdown("4. Apply NLP for context understanding")
                st.markdown("**Avg. Processing Time:** 1.2s")
            
            with pdf_tab:
                st.markdown("#### PDF Transformation")
                st.markdown("**Input Format:** Text, tables, and forms in PDF format")
                st.markdown("**Processing Steps:**")
                st.markdown("1. Extract text using OCR if needed")
                st.markdown("2. Identify and parse tables and forms")
                st.markdown("3. Recognize document structure")
                st.markdown("4. Map extracted data to standard schema")
                st.markdown("**Avg. Processing Time:** 1.5s")
        
        # Performance Metrics
        with st.expander("Performance Metrics"):
            # Create some random performance data
            transform_perf = pd.DataFrame({
                'File Type': ['CSV', 'Excel', 'JSON', 'Word', 'PDF'],
                'Avg. Transform Time (s)': [0.3, 0.8, 0.4, 1.2, 1.5],
                'Success Rate (%)': [99.5, 98.2, 99.8, 95.3, 94.1]
            })
            
            st.bar_chart(transform_perf.set_index('File Type')['Avg. Transform Time (s)'])
            st.bar_chart(transform_perf.set_index('File Type')['Success Rate (%)'])
    
    # Storage Agent Tab
    with storage_tab:
        st.subheader("Storage Agent")
        st.markdown("Prepares and loads processed data into core systems and data warehouse.")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Stored", len(st.session_state.processed_files))
        with col2:
            st.metric("Avg. Storage Time", f"{random.uniform(0.2, 1.0):.2f}s")
        with col3:
            st.metric("Storage Efficiency", f"{random.uniform(90, 99):.1f}%")
        
        # Capabilities
        with st.expander("Capabilities", expanded=True):
            st.markdown("- Data partitioning and optimization")
            st.markdown("- System-specific formatting")
            st.markdown("- Load verification and validation")
            st.markdown("- Audit trail generation")
        
        # Processing Details
        with st.expander("Processing Details", expanded=True):
            st.markdown("### Storage Workflow")
            st.markdown("""
            1. **Prepare Data**: Format data for target systems
            2. **Optimize Storage**: Apply partitioning and indexing
            3. **Load Data**: Insert into core systems and data warehouse
            4. **Verify Load**: Confirm data integrity after loading
            5. **Generate Audit**: Create audit trail of data lineage
            6. **Archive Original**: Store original files for reference
            """)
            
            # Show storage systems
            st.markdown("### Target Storage Systems")
            storage_systems = [
                {"System": "Core Transaction System", "Data Format": "Normalized Tables", "Update Frequency": "Real-time", "Retention": "1 year"},
                {"System": "Data Warehouse", "Data Format": "Star Schema", "Update Frequency": "Daily", "Retention": "7 years"},
                {"System": "Reporting Database", "Data Format": "Denormalized Views", "Update Frequency": "Hourly", "Retention": "2 years"},
                {"System": "Archive Storage", "Data Format": "Compressed Original", "Update Frequency": "On Arrival", "Retention": "10 years"}
            ]
            
            storage_df = pd.DataFrame(storage_systems)
            st.dataframe(storage_df, use_container_width=True)
            
            # Show recent storage operations
            if st.session_state.processed_files:
                st.markdown("### Recent Storage Operations")
                for file in st.session_state.processed_files[-3:]:  # Show last 3 processed files
                    with st.container():
                        html_content = "<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                        html_content += "<strong>File:</strong> " + file['filename'] + "<br/>"
                        html_content += "<strong>Processed:</strong> " + file['received_time'].strftime('%Y-%m-%d %H:%M:%S') + "<br/>"
                        html_content += "<strong>Storage Time:</strong> " + f"{random.uniform(0.1, 0.5):.2f}s" + "<br/>"
                        html_content += "<strong>Systems Updated:</strong> Core Transaction System, Data Warehouse<br/>"
                        html_content += "<strong>Records Stored:</strong> " + str(random.randint(10, 100)) + "<br/>"
                        html_content += "<strong>Status:</strong> Complete<br/>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("No files have been stored yet. Select an example from the sidebar to begin.")
        
        # Performance Metrics
        with st.expander("Performance Metrics"):
            # Create some random performance data
            dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
            storage_perf = pd.DataFrame({
                'Date': dates,
                'Files Stored': [random.randint(3, 15) for _ in range(7)],
                'Storage Time (s)': [random.uniform(0.2, 0.8) for _ in range(7)],
                'Data Volume (MB)': [random.uniform(5, 50) for _ in range(7)]
            })
            
            st.line_chart(storage_perf.set_index('Date')['Files Stored'])
            st.line_chart(storage_perf.set_index('Date')['Storage Time (s)'])
            st.line_chart(storage_perf.set_index('Date')['Data Volume (MB)'])
