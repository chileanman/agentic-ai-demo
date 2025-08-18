import streamlit as st
import pandas as pd
import random
import json
import io
from datetime import datetime

def render_validation_tab(selected_file):
    """
    Renders the validation details tab.
    """
    if not st.session_state.processed_files:
        st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        return
    
    if selected_file:
        file_id = selected_file.split(":")[0].strip()
        file = next((f for f in st.session_state.processed_files if f["example_id"] == file_id), None)
        
        if file:
            st.subheader("Validation Details")
            
            # Get example metadata
            example_data = st.session_state.examples_metadata[file_id]
            file_type = example_data["file_type"]
            complexity = example_data["complexity"]
            
            # Create simulated validation results based on file type and complexity
            validation_issues = []
            
            if complexity == "high":
                validation_issues = [
                    {"severity": "high", "field": "customer_id", "issue": "Missing values in required field", "count": random.randint(5, 15)},
                    {"severity": "medium", "field": "transaction_date", "issue": "Invalid date format", "count": random.randint(3, 10)},
                    {"severity": "low", "field": "amount", "issue": "Suspicious outlier values", "count": random.randint(1, 5)}
                ]
            elif complexity == "medium":
                validation_issues = [
                    {"severity": "medium", "field": "product_code", "issue": "Unknown product codes", "count": random.randint(2, 8)},
                    {"severity": "low", "field": "customer_name", "issue": "Inconsistent formatting", "count": random.randint(1, 6)}
                ]
            else:  # low complexity
                if random.random() < 0.3:  # 30% chance of having a minor issue
                    validation_issues = [
                        {"severity": "low", "field": "description", "issue": "Truncated text", "count": random.randint(1, 3)}
                    ]
            
            # Display validation summary
            if validation_issues:
                total_issues = sum(issue["count"] for issue in validation_issues)
                st.warning(f"Found {total_issues} validation issues in {file['filename']}")
                
                # Create a dataframe for the issues
                issues_df = pd.DataFrame(validation_issues)
                
                # Add color coding for severity
                def highlight_severity(val):
                    if val == "high":
                        return 'background-color: #ffcccc'
                    elif val == "medium":
                        return 'background-color: #ffffcc'
                    else:
                        return 'background-color: #e6ffcc'
                
                # Display the issues table
                st.dataframe(issues_df.style.applymap(highlight_severity, subset=["severity"]), use_container_width=True)
                
                # Show sample data with issues highlighted
                st.subheader("Sample Data with Issues Highlighted")
                
                # Create sample data based on file type
                if file_type == "csv":
                    sample_data = """
                    customer_id,transaction_date,product_code,amount,description
                    1001,2025-01-15,PRD-001,150.00,Standard subscription
                    ,2025-01-16,PRD-002,75.50,Basic plan
                    1003,01/15/2025,PRD-003,200.00,Premium subscription
                    1004,2025-01-17,UNKNOWN,50.25,Trial subscription
                    1005,2025-01-18,PRD-005,999999.99,Enterprise plan
                    """
                    st.code(sample_data, language="csv")
                elif file_type == "json":
                    sample_data = """
                    [
                      {
                        "customer_id": 1001,
                        "transaction_date": "2025-01-15",
                        "product_code": "PRD-001",
                        "amount": 150.00,
                        "description": "Standard subscription"
                      },
                      {
                        "customer_id": null,
                        "transaction_date": "2025-01-16",
                        "product_code": "PRD-002",
                        "amount": 75.50,
                        "description": "Basic plan"
                      },
                      {
                        "customer_id": 1003,
                        "transaction_date": "01/15/2025",
                        "product_code": "PRD-003",
                        "amount": 200.00,
                        "description": "Premium subscription"
                      }
                    ]
                    """
                    st.code(sample_data, language="json")
                else:
                    st.info(f"Sample data preview not available for {file_type.upper()} files")
            else:
                st.success(f"No validation issues found in {file['filename']}")
                
            # Show validation process details
            with st.expander("Validation Process Details"):
                st.markdown("**Validation Rules Applied:**")
                st.markdown("- Required fields check: Ensure all mandatory fields have values")
                st.markdown("- Data type validation: Verify correct data types for each field")
                st.markdown("- Format validation: Check date formats, numeric ranges, etc.")
                st.markdown("- Business rule validation: Apply domain-specific validation rules")
                st.markdown("- Outlier detection: Identify statistical outliers in numeric fields")
                
                st.markdown("**Validation Performance:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Processing Time", f"{random.uniform(0.2, 1.5):.2f}s")
                with col2:
                    st.metric("Rules Applied", random.randint(10, 25))
                with col3:
                    st.metric("Fields Validated", random.randint(5, 15))
