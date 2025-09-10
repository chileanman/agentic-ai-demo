import random
from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.transformation_view import render_transformation_tab

# Import custom views
from ui.validation_view import render_validation_tab


def render_dashboard():
    """
    Renders the main dashboard with key metrics and visualizations.
    """
    st.header("Dashboard")

    # Display processing queue if any
    if st.session_state.process_queue:
        st.subheader("Processing Queue")
        queue_df = pd.DataFrame(
            {
                "Position": list(range(1, len(st.session_state.process_queue) + 1)),
                "File ID": st.session_state.process_queue,
                "File Name": [
                    st.session_state.examples_metadata[id]["filename"]
                    for id in st.session_state.process_queue
                ],
                "Sender": [
                    st.session_state.examples_metadata[id]["sender"]
                    for id in st.session_state.process_queue
                ],
                "File Type": [
                    st.session_state.examples_metadata[id]["file_type"]
                    for id in st.session_state.process_queue
                ],
            }
        )
        st.dataframe(queue_df, use_container_width=True)

        # Show progress
        total_files = len(st.session_state.process_queue) + 1  # +1 for the current file

        progress_text = f"Processing file 1 of {total_files}"
        st.progress(0, text=progress_text)

    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_files = len(st.session_state.processed_files)
        st.metric("Files Processed", total_files)

    with col2:
        if total_files > 0:
            avg_time = (
                sum(f["processing_time"] for f in st.session_state.processed_files)
                / total_files
            )
            st.metric("Avg. Processing Time", f"{avg_time:.2f}s")
        else:
            st.metric("Avg. Processing Time", "0.00s")

    with col3:
        # Count unique senders
        if total_files > 0:
            unique_senders = len(
                set(f["sender"] for f in st.session_state.processed_files)
            )
            st.metric("Unique Senders", unique_senders)
        else:
            st.metric("Unique Senders", 0)

    with col4:
        # Count files by complexity
        if total_files > 0:
            high_complexity = sum(
                1 for f in st.session_state.processed_files if f["complexity"] == "high"
            )
            st.metric("High Complexity Files", high_complexity)
        else:
            st.metric("High Complexity Files", 0)

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Files by Type", "Processing Time", "Agent Activity"])

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
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )

    with tab2:
        if st.session_state.processed_files:
            # Create a bar chart of processing times
            processing_data = pd.DataFrame(
                {
                    "File": [f["filename"] for f in st.session_state.processed_files],
                    "Processing Time (s)": [
                        f["processing_time"] for f in st.session_state.processed_files
                    ],
                    "Complexity": [
                        f["complexity"] for f in st.session_state.processed_files
                    ],
                }
            )

            fig = px.bar(
                processing_data,
                x="File",
                y="Processing Time (s)",
                color="Complexity",
                title="Processing Time by File",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )

    with tab3:
        st.subheader("Agent Activity Timeline")

        if st.session_state.agent_logs:
            # Create a timeline of agent activities
            for log in st.session_state.agent_logs[-10:]:  # Show last 10 logs
                with st.container():
                    status_color = (
                        "green"
                        if log["status"] == "complete"
                        else "orange" if log["status"] == "pending" else "red"
                    )
                    html_content = (
                        "<div style='padding: 10px; border-left: 5px solid "
                        + status_color
                        + ";'>"
                    )
                    html_content += (
                        "<strong>"
                        + log["timestamp"].strftime("%H:%M:%S")
                        + "</strong> - <strong>"
                        + log["agent"]
                        + "</strong><br/>"
                    )
                    html_content += log["action"] + "<br/>"
                    html_content += (
                        "<em>Duration: " + f"{log['duration']:.2f}" + "s</em>"
                    )
                    html_content += "</div>"
                    st.markdown(html_content, unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info(
                "No agent activity recorded yet. Select an example from the sidebar to begin."
            )

    # Add a visual DAG of agent workflow
    st.subheader("Agent Workflow")

    # Create a DAG visualization using Plotly
    fig = go.Figure()

    # Define agent nodes
    agents = [
        {"id": "email", "name": "Email Agent", "x": 0, "y": 0, "color": "blue"},
        {
            "id": "validation",
            "name": "Validation Agent",
            "x": 1,
            "y": 0,
            "color": "green",
        },
        {
            "id": "question",
            "name": "Question Agent",
            "x": 1,
            "y": -1,
            "color": "orange",
        },
        {
            "id": "transform",
            "name": "Transformation Agent",
            "x": 2,
            "y": 0,
            "color": "purple",
        },
        {"id": "storage", "name": "Storage Agent", "x": 3, "y": 0, "color": "red"},
    ]

    # Add nodes
    for agent in agents:
        fig.add_trace(
            go.Scatter(
                x=[agent["x"]],
                y=[agent["y"]],
                mode="markers+text",
                marker=dict(size=30, color=agent["color"]),
                text=[agent["name"]],
                textposition="bottom center",
                name=agent["name"],
                hoverinfo="text",
                hovertext=agent["name"],
            )
        )

    # Add edges
    edges = [
        {"from": "email", "to": "validation", "color": "gray"},
        {"from": "validation", "to": "question", "color": "orange", "dash": "dash"},
        {"from": "validation", "to": "transform", "color": "gray"},
        {"from": "question", "to": "transform", "color": "orange", "dash": "dash"},
        {"from": "transform", "to": "storage", "color": "gray"},
    ]

    for edge in edges:
        from_agent = next(a for a in agents if a["id"] == edge["from"])
        to_agent = next(a for a in agents if a["id"] == edge["to"])

        fig.add_trace(
            go.Scatter(
                x=[from_agent["x"], to_agent["x"]],
                y=[from_agent["y"], to_agent["y"]],
                mode="lines",
                line=dict(
                    width=2,
                    color=edge.get("color", "gray"),
                    dash=edge.get("dash", "solid"),
                ),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Update layout
    fig.update_layout(
        title="Agent Interaction Workflow",
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add legend explaining the workflow
    with st.expander("Workflow Explanation"):
        st.markdown(
            """
        1. **Email Agent** receives files from partners/suppliers via email
        2. **Validation Agent** checks files for issues and validates data
        3. **Question Agent** generates clarifying questions if needed (dotted line)
        4. **Transformation Agent** processes files into a common data structure
        5. **Storage Agent** prepares data for core systems and data warehouse
        """
        )

        # Add information about processing times
        st.markdown("### Processing Performance")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Email Processing", f"{random.uniform(0.1, 0.5):.2f}s")
        with col2:
            st.metric("Validation", f"{random.uniform(0.3, 1.0):.2f}s")
        with col3:
            st.metric("Transformation", f"{random.uniform(0.5, 2.0):.2f}s")

        # Add information about deployment options
        st.markdown("### Deployment Options")

        systems = [
            {
                "Component": "Email Processing",
                "Cloud Cost": "$50-100/month",
                "On-Prem Cost": "$500-1000 setup + maintenance",
            },
            {
                "Component": "AI Processing",
                "Cloud Cost": "$200-500/month",
                "On-Prem Cost": "$2000-5000 setup + maintenance",
            },
            {
                "Component": "Data Storage",
                "Cloud Cost": "$100-300/month",
                "On-Prem Cost": "$1000-3000 setup + maintenance",
            },
        ]

        systems_df = pd.DataFrame(systems)
        st.dataframe(systems_df, use_container_width=True)


def render_file_details():
    """
    Renders detailed information about processed files.
    """
    st.header("File Details")

    # Add tabs for different views
    file_tab, email_tab, validation_tab, transformation_tab = st.tabs(
        [
            "File Info",
            "Email Communication",
            "Validation Details",
            "Data Transformation",
        ]
    )

    # File Info Tab
    with file_tab:
        if not st.session_state.processed_files:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )
            return

        # File selection
        file_options = [
            f"{f['example_id']}: {f['filename']}"
            for f in st.session_state.processed_files
        ]
        selected_file = st.selectbox("Select a file to view details", file_options)

        if selected_file:
            file_id = selected_file.split(":")[0].strip()
            file = next(
                (
                    f
                    for f in st.session_state.processed_files
                    if f["example_id"] == file_id
                ),
                None,
            )

        if file:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("File Information")
                st.markdown(f"**Filename:** {file['filename']}")
                st.markdown(f"**File Type:** {file['file_type']}")
                st.markdown(f"**Sender:** {file['sender']}")
                st.markdown(f"**Subject:** {file['subject']}")
                st.markdown(
                    f"**Received:** {file['received_time'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
                st.markdown(f"**Processing Time:** {file['processing_time']:.2f}s")
                st.markdown(f"**Status:** {file['status']}")
                st.markdown(f"**Complexity:** {file['complexity']}")

            with col2:
                st.subheader("Processing Timeline")

                # Filter logs for this file
                file_logs = [
                    log
                    for log in st.session_state.agent_logs
                    if file_id in log.get("action", "")
                ]

                if file_logs:
                    for log in file_logs:
                        with st.container():
                            status_color = (
                                "green"
                                if log["status"] == "complete"
                                else "orange" if log["status"] == "pending" else "red"
                            )
                            html_content = (
                                "<div style='padding: 10px; border-left: 5px solid "
                                + status_color
                                + ";'>"
                            )
                            html_content += (
                                "<strong>"
                                + log["timestamp"].strftime("%H:%M:%S")
                                + "</strong> - <strong>"
                                + log["agent"]
                                + "</strong><br/>"
                            )
                            html_content += log["action"] + "<br/>"
                            html_content += (
                                "<em>Duration: " + f"{log['duration']:.2f}" + "s</em>"
                            )
                            html_content += "</div>"
                            st.markdown(html_content, unsafe_allow_html=True)
                            st.markdown("---")
                else:
                    st.info("No detailed logs available for this file")

            # Check if there are questions for this file
            file_questions = next(
                (
                    q
                    for q in st.session_state.questions_asked
                    if q["example_id"] == file_id
                ),
                None,
            )

            if file_questions:
                st.subheader("Clarification Questions")
                for i, question in enumerate(file_questions["questions"]):
                    with st.expander(
                        f"Question {i+1} - {question['priority']} priority"
                    ):
                        st.markdown(f"**Question:** {question['question']}")
                        st.markdown(f"**Context:** {question['context']}")

                        # Add simulated response if not answered
                        if not file_questions.get("answered", False):
                            st.text_input(
                                "Your response:",
                                key=f"response_{file_id}_{i}",
                                placeholder="Type your response here...",
                            )
                            if st.button("Send Response", key=f"send_{file_id}_{i}"):
                                st.success(
                                    "Response sent! The agent will process your answer."
                                )
                                # In a real app, this would trigger further processing

    # Email Communication Tab
    with email_tab:
        if not st.session_state.processed_files:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )
        elif "selected_file" in locals():
            file_id = selected_file.split(":")[0].strip()
            file = next(
                (
                    f
                    for f in st.session_state.processed_files
                    if f["example_id"] == file_id
                ),
                None,
            )

            if file:
                st.subheader("Email Communication")

                # Incoming Email
                with st.expander("Incoming Email", expanded=True):
                    sender_email = file["sender"].lower().replace(" ", ".")
                    html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                    html_content += (
                        "<strong>From:</strong> "
                        + file["sender"]
                        + " &lt;"
                        + sender_email
                        + "@example.com&gt;<br/>"
                    )
                    html_content += "<strong>To:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                    html_content += (
                        "<strong>Subject:</strong> " + file["subject"] + "<br/>"
                    )
                    html_content += (
                        "<strong>Date:</strong> "
                        + file["received_time"].strftime("%a, %d %b %Y %H:%M:%S")
                        + "<br/>"
                    )
                    html_content += (
                        "<strong>Attachments:</strong> " + file["filename"] + "<br/>"
                    )
                    html_content += "<hr/>"
                    html_content += "<p>Hello Data Processing Team,</p>"
                    html_content += "<p>Please find attached the latest data file for processing.</p>"
                    html_content += "<p>We need this processed as soon as possible for our monthly reporting.</p>"
                    html_content += "<p>Thank you for your assistance.</p>"
                    html_content += "<p>Best regards,<br/>" + file["sender"] + "</p>"
                    html_content += "</div>"
                    st.markdown(html_content, unsafe_allow_html=True)

                # Questions Email (if any)
                file_questions = next(
                    (
                        q
                        for q in st.session_state.questions_asked
                        if q["example_id"] == file_id
                    ),
                    None,
                )
                if file_questions:
                    with st.expander(
                        "Outgoing Email - Clarification Questions", expanded=True
                    ):
                        # Format questions
                        questions_text = "\n".join(
                            [
                                f"{i+1}. {q['question']}"
                                for i, q in enumerate(file_questions["questions"])
                            ]
                        )
                        questions_html = questions_text.replace("\n", "<br/>")
                        sender_first_name = file["sender"].split()[0]

                        html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                        html_content += "<strong>From:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                        html_content += (
                            "<strong>To:</strong> "
                            + file["sender"]
                            + " &lt;"
                            + sender_email
                            + "@example.com&gt;<br/>"
                        )
                        html_content += (
                            "<strong>Subject:</strong> Re: "
                            + file["subject"]
                            + " - Clarification Needed<br/>"
                        )
                        html_content += (
                            "<strong>Date:</strong> "
                            + (file["received_time"] + timedelta(minutes=5)).strftime(
                                "%a, %d %b %Y %H:%M:%S"
                            )
                            + "<br/>"
                        )
                        html_content += "<hr/>"
                        html_content += "<p>Hello " + sender_first_name + ",</p>"
                        html_content += "<p>Thank you for sending the data file. Before we can complete processing, we need clarification on a few points:</p>"
                        html_content += "<p>" + questions_html + "</p>"
                        html_content += "<p>Your prompt response will help us process this data accurately and efficiently.</p>"
                        html_content += "<p>Best regards,<br/>Data Processing Team</p>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)

                # Confirmation Email
                if file["status"] == "Processed":
                    with st.expander(
                        "Outgoing Email - Processing Confirmation", expanded=True
                    ):
                        sender_first_name = file["sender"].split()[0]
                        html_content = "<div style='border: 1px solid #ddd; padding: 15px; border-radius: 5px;'>"
                        html_content += "<strong>From:</strong> Data Processing Team &lt;data.processing@ourcompany.com&gt;<br/>"
                        html_content += (
                            "<strong>To:</strong> "
                            + file["sender"]
                            + " &lt;"
                            + sender_email
                            + "@example.com&gt;<br/>"
                        )
                        html_content += (
                            "<strong>Subject:</strong> Re: "
                            + file["subject"]
                            + " - Processing Complete<br/>"
                        )
                        html_content += (
                            "<strong>Date:</strong> "
                            + (file["received_time"] + timedelta(minutes=15)).strftime(
                                "%a, %d %b %Y %H:%M:%S"
                            )
                            + "<br/>"
                        )
                        html_content += "<hr/>"
                        html_content += "<p>Hello " + sender_first_name + ",</p>"
                        html_content += (
                            "<p>We have successfully processed the data file you sent ("
                            + file["filename"]
                            + ").</p>"
                        )
                        html_content += "<p>The data has been transformed into our standard format and loaded into the following systems:</p>"
                        html_content += "<ul>"
                        html_content += "<li>Core Transaction System</li>"
                        html_content += "<li>Data Warehouse</li>"
                        html_content += "</ul>"
                        html_content += "<p>Processing Summary:</p>"
                        html_content += "<ul>"
                        html_content += (
                            "<li>Records Processed: "
                            + str(random.randint(10, 100))
                            + "</li>"
                        )
                        html_content += (
                            "<li>Processing Time: "
                            + f"{file['processing_time']:.2f}"
                            + " seconds</li>"
                        )
                        html_content += "<li>Validation Status: Passed</li>"
                        html_content += "</ul>"
                        html_content += "<p>If you have any questions or need further assistance, please let us know.</p>"
                        html_content += "<p>Best regards,<br/>Data Processing Team</p>"
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)

    # Validation Details Tab
    with validation_tab:
        if not st.session_state.processed_files:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )
        elif "selected_file" in locals():
            render_validation_tab(selected_file)

    # Data Transformation Tab
    with transformation_tab:
        if not st.session_state.processed_files:
            st.info(
                "No files have been processed yet. Select an example from the sidebar to begin."
            )
        elif "selected_file" in locals():
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

    # Email Agent
    render_agent_info(
        "Email Agent",
        "Handles incoming emails, extracts attachments, and routes files to the appropriate processing pipeline.",
        [
            "Email parsing and classification",
            "Attachment extraction and validation",
            "Sender verification and prioritization",
            "Response generation and sending",
        ],
        {
            "Emails Processed": len(st.session_state.processed_files),
            "Avg. Response Time": f"{random.uniform(0.5, 2.0):.2f}s",
            "Success Rate": f"{random.uniform(95, 99.9):.1f}%",
        },
    )

    # Validation Agent
    render_agent_info(
        "Validation Agent",
        "Validates incoming data files for format correctness, data integrity, and business rule compliance.",
        [
            "File format validation",
            "Data schema validation",
            "Business rule checking",
            "Error detection and reporting",
        ],
        {
            "Files Validated": len(st.session_state.processed_files),
            "Avg. Validation Time": f"{random.uniform(0.3, 1.5):.2f}s",
            "Issues Detected": random.randint(0, 10),
        },
    )

    # Question Generation Agent
    render_agent_info(
        "Question Generation Agent",
        "Generates clarifying questions when data validation issues are detected.",
        [
            "Context-aware question generation",
            "Priority-based question sorting",
            "Response processing and integration",
            "Follow-up question generation",
        ],
        {
            "Questions Generated": len(st.session_state.questions_asked),
            "Avg. Generation Time": f"{random.uniform(0.2, 1.0):.2f}s",
            "Response Rate": f"{random.uniform(80, 95):.1f}%",
        },
    )

    # Transformation Agent
    render_agent_info(
        "Transformation Agent",
        "Transforms data from various formats into a standardized structure for downstream processing.",
        [
            "Multi-format data parsing (CSV, Excel, JSON, Word, PDF)",
            "Schema mapping and normalization",
            "Data enrichment and augmentation",
            "Output formatting and validation",
        ],
        {
            "Files Transformed": len(st.session_state.processed_files),
            "Avg. Transform Time": f"{random.uniform(0.5, 2.0):.2f}s",
            "Formats Supported": 5,
        },
    )

    # Storage Agent
    render_agent_info(
        "Storage Agent",
        "Prepares and loads processed data into core systems and data warehouse.",
        [
            "Data partitioning and optimization",
            "System-specific formatting",
            "Load verification and validation",
            "Audit trail generation",
        ],
        {
            "Files Stored": len(st.session_state.processed_files),
            "Avg. Storage Time": f"{random.uniform(0.2, 1.0):.2f}s",
            "Storage Efficiency": f"{random.uniform(90, 99):.1f}%",
        },
    )
