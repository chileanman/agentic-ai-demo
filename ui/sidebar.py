import streamlit as st
import pandas as pd
import random

def render_sidebar():
    """
    Renders the sidebar with example selection options.
    """
    st.sidebar.title("File Processing Demo")
    
    # If examples metadata is not loaded, generate it
    if "examples_metadata" not in st.session_state or not st.session_state.examples_metadata:
        st.session_state.examples_metadata = get_example_metadata()
    
    # Group examples by different criteria
    examples = st.session_state.examples_metadata
    
    # Add "Process All" buttons at the top
    st.sidebar.markdown("### Process Multiple Files")
    
    # Add a button to process all examples
    if st.sidebar.button("Process All Examples", key="process_all_top"):
        # Process all unprocessed examples
        if "process_queue" not in st.session_state:
            st.session_state.process_queue = []
        
        # Add all unprocessed examples to the queue
        unprocessed = [id for id in examples.keys() 
                      if id not in st.session_state.processing_status or 
                      st.session_state.processing_status[id] != "complete"]
        
        if unprocessed:
            st.session_state.process_queue.extend(unprocessed)
            st.session_state.selected_example = st.session_state.process_queue.pop(0)
            return
    
    # Add a reset button
    if st.sidebar.button("Reset Demo", key="reset_top"):
        # Clear session state
        for key in ["processed_files", "agent_logs", "questions_asked", "processing_status"]:
            st.session_state[key] = []
        st.session_state.processing_status = {}
        st.session_state.selected_example = None
        st.session_state.process_queue = []
        st.sidebar.success("Demo reset successfully!")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("Select examples to process:")
    
    # Create tabs for different selection methods
    tab1, tab2, tab3, tab4 = st.sidebar.tabs(["Individual", "By Sender", "By Complexity", "By Type"])
    
    with tab1:
        # Individual example selection
        st.markdown("### Select Individual Example")
        for example_id, example in examples.items():
            # Add status indicator (tick mark or processing icon)
            status = ""
            if example_id in st.session_state.processing_status:
                status = " ✓" if st.session_state.processing_status[example_id] == "complete" else " ⏳"
            
            if st.button(f"{example_id}: {example['filename']}{status}", key=f"btn_{example_id}"):
                st.session_state.selected_example = example_id
                return
    
    with tab2:
        # Group by sender
        st.markdown("### Select by Sender")
        senders = set(example["sender"] for example in examples.values())
        
        for sender in sorted(senders):
            sender_examples = {id: ex for id, ex in examples.items() if ex["sender"] == sender}
            with st.expander(f"{sender} ({len(sender_examples)} files)"):
                if st.button(f"Process all from {sender}", key=f"sender_{sender}"):
                    # Process all examples from this sender
                    if "process_queue" not in st.session_state:
                        st.session_state.process_queue = []
                    
                    # Add all unprocessed examples from this sender to the queue
                    unprocessed = [id for id in sender_examples.keys() 
                                  if id not in st.session_state.processing_status or 
                                  st.session_state.processing_status[id] != "complete"]
                    
                    if unprocessed:
                        st.session_state.process_queue.extend(unprocessed)
                        st.session_state.selected_example = st.session_state.process_queue.pop(0)
                        return
                
                # List individual files from this sender
                for example_id, example in sender_examples.items():
                    status = ""
                    if example_id in st.session_state.processing_status:
                        status = " ✓" if st.session_state.processing_status[example_id] == "complete" else " ⏳"
                    
                    if st.button(f"{example['filename']}{status}", key=f"btn_sender_{example_id}"):
                        st.session_state.selected_example = example_id
                        return
    
    with tab3:
        # Group by complexity
        st.markdown("### Select by Complexity")
        complexities = ["low", "medium", "high"]
        
        for complexity in complexities:
            complexity_examples = {id: ex for id, ex in examples.items() if ex["complexity"] == complexity}
            with st.expander(f"{complexity.title()} Complexity ({len(complexity_examples)} files)"):
                if st.button(f"Process all {complexity} complexity", key=f"complexity_{complexity}"):
                    # Process all examples of this complexity
                    if "process_queue" not in st.session_state:
                        st.session_state.process_queue = []
                    
                    # Add all unprocessed examples of this complexity to the queue
                    unprocessed = [id for id in complexity_examples.keys() 
                                  if id not in st.session_state.processing_status or 
                                  st.session_state.processing_status[id] != "complete"]
                    
                    if unprocessed:
                        st.session_state.process_queue.extend(unprocessed)
                        st.session_state.selected_example = st.session_state.process_queue.pop(0)
                        return
                
                # List individual files of this complexity
                for example_id, example in complexity_examples.items():
                    status = ""
                    if example_id in st.session_state.processing_status:
                        status = " ✓" if st.session_state.processing_status[example_id] == "complete" else " ⏳"
                    
                    if st.button(f"{example['filename']}{status}", key=f"btn_complexity_{example_id}"):
                        st.session_state.selected_example = example_id
                        return
    
    with tab4:
        # Group by file type
        st.markdown("### Select by File Type")
        file_types = set(example["file_type"] for example in examples.values())
        
        for file_type in sorted(file_types):
            type_examples = {id: ex for id, ex in examples.items() if ex["file_type"] == file_type}
            with st.expander(f"{file_type.upper()} Files ({len(type_examples)} files)"):
                if st.button(f"Process all {file_type.upper()} files", key=f"type_{file_type}"):
                    # Process all examples of this file type
                    if "process_queue" not in st.session_state:
                        st.session_state.process_queue = []
                    
                    # Add all unprocessed examples of this file type to the queue
                    unprocessed = [id for id in type_examples.keys() 
                                  if id not in st.session_state.processing_status or 
                                  st.session_state.processing_status[id] != "complete"]
                    
                    if unprocessed:
                        st.session_state.process_queue.extend(unprocessed)
                        st.session_state.selected_example = st.session_state.process_queue.pop(0)
                        return
                
                # List individual files of this type
                for example_id, example in type_examples.items():
                    status = ""
                    if example_id in st.session_state.processing_status:
                        status = " ✓" if st.session_state.processing_status[example_id] == "complete" else " ⏳"
                    
                    if st.button(f"{example['filename']}{status}", key=f"btn_type_{example_id}"):
                        st.session_state.selected_example = example_id
                        return
    
    # These buttons have been moved to the top of the sidebar
        
    # Add deployment information section
    with st.sidebar.expander("Deployment Information"):
        st.markdown("""
        ### Deployment Options
        
        This demo can be deployed in various ways:
        
        1. **Local Deployment**
           - Zero cloud costs
           - Limited scalability
           - For demonstration purposes only
        
        2. **Cloud Deployment (AWS/Azure/GCP)**
           - Containerized with Docker
           - Kubernetes for orchestration
           - Estimated monthly cost: $500-$2,000
        
        3. **Enterprise Deployment**
           - High availability setup
           - Auto-scaling capabilities
           - Integrated with existing systems
           - Estimated monthly cost: $3,000-$10,000
        
        ### Production Cost Factors
        
        - **Infrastructure**: $300-$1,500/month
        - **AI Processing**: $0.10-$0.50 per file
        - **Storage**: $50-$200/month
        - **Monitoring & Support**: $500-$2,000/month
        - **Integration**: One-time cost of $5,000-$20,000
        
        Contact us for a detailed cost estimate based on your specific requirements.
        """)

def get_example_metadata():
    """
    Generate metadata for example files.
    In a real application, this would load from a configuration file.
    """
    # Define senders
    senders = [
        {"name": "Acme Insurance", "email": "data@acmeinsurance.com"},
        {"name": "Global Reinsurance", "email": "reports@globalre.com"},
        {"name": "City Benefits Corp", "email": "analytics@citybenefits.com"},
        {"name": "Metro Health Partners", "email": "claims@metrohealth.org"},
        {"name": "Secure Financial", "email": "data@securefinancial.com"}
    ]
    
    # Define file types and their templates
    file_templates = {
        "csv": [
            "monthly_claims_{}.csv",
            "customer_data_{}.csv",
            "policy_renewals_{}.csv",
            "transaction_log_{}.csv",
            "risk_assessment_{}.csv"
        ],
        "excel": [
            "financial_report_{}.xlsx",
            "claims_analysis_{}.xlsx",
            "customer_portfolio_{}.xlsx",
            "underwriting_summary_{}.xlsx",
            "market_trends_{}.xlsx"
        ],
        "json": [
            "api_response_{}.json",
            "system_integration_{}.json",
            "customer_profile_{}.json",
            "policy_details_{}.json",
            "claim_events_{}.json"
        ],
        "word": [
            "legal_document_{}.docx",
            "policy_terms_{}.docx",
            "compliance_report_{}.docx",
            "customer_correspondence_{}.docx",
            "executive_summary_{}.docx"
        ],
        "pdf": [
            "signed_agreement_{}.pdf",
            "regulatory_filing_{}.pdf",
            "claim_documentation_{}.pdf",
            "benefit_statement_{}.pdf",
            "annual_report_{}.pdf"
        ]
    }
    
    # Define subjects
    subjects = {
        "csv": [
            "Monthly Claims Data for {}",
            "Customer Data Update - {}",
            "Policy Renewals for Q{}",
            "Transaction Log for {}",
            "Risk Assessment Results - {}"
        ],
        "excel": [
            "Financial Report - Q{} 2025",
            "Claims Analysis for {}",
            "Customer Portfolio Review - {}",
            "Underwriting Summary - {}",
            "Market Trends Analysis - Q{} 2025"
        ],
        "json": [
            "API Integration Data - {}",
            "System Integration Payload - {}",
            "Customer Profiles - Batch {}",
            "Policy Details Export - {}",
            "Claim Events Log - {}"
        ],
        "word": [
            "Legal Document Review - {}",
            "Updated Policy Terms - {}",
            "Compliance Report - Q{} 2025",
            "Customer Correspondence - {}",
            "Executive Summary - {}"
        ],
        "pdf": [
            "Signed Agreement - {} Partnership",
            "Regulatory Filing - {} Submission",
            "Claim Documentation - Case {}",
            "Benefit Statement - {} Plan",
            "Annual Report - {} Division"
        ]
    }
    
    # Generate examples
    examples = {}
    example_id = 1
    
    # For each sender, generate examples of each file type with varying complexity
    for sender in senders:
        for file_type, templates in file_templates.items():
            for complexity in ["low", "medium", "high"]:
                # Generate 5 examples per sender per file type per complexity
                for i in range(5):
                    # Select a random template
                    template = random.choice(templates)
                    subject_template = random.choice(subjects[file_type])
                    
                    # Generate a random identifier
                    identifier = random.choice(["A", "B", "C", "D", "E"]) + str(random.randint(100, 999))
                    
                    # Create the filename and subject
                    filename = template.format(identifier)
                    subject = subject_template.format(identifier)
                    
                    # Add to examples
                    examples[f"example_{example_id}"] = {
                        "filename": filename,
                        "file_type": file_type,
                        "sender": sender["name"],
                        "sender_email": sender["email"],
                        "subject": subject,
                        "complexity": complexity,
                        "email_body": f"Please find attached the {subject.lower()}. Let me know if you need any clarification."
                    }
                    
                    example_id += 1
    
    return examples
