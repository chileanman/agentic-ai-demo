import streamlit as st
import pandas as pd
import random
import json
import io
from datetime import datetime

def render_transformation_tab(selected_file):
    """
    Renders the data transformation tab.
    """
    if not st.session_state.processed_files:
        st.info("No files have been processed yet. Select an example from the sidebar to begin.")
        return
    
    if selected_file:
        file_id = selected_file.split(":")[0].strip()
        file = next((f for f in st.session_state.processed_files if f["example_id"] == file_id), None)
        
        if file:
            st.subheader("Data Transformation")
            
            # Get example metadata
            example_data = st.session_state.examples_metadata[file_id]
            file_type = example_data["file_type"]
            
            # Create tabs for input and output data
            input_tab, output_tab = st.tabs(["Input Data", "Transformed Output"])
            
            # Input Data Tab
            with input_tab:
                st.subheader("Original Input Data")
                st.markdown(f"**File Type:** {file_type.upper()}")
                
                # Show sample input data based on file type
                if file_type == "csv":
                    input_data = """
                    customer_id,transaction_date,product_code,amount,description
                    1001,2025-01-15,PRD-001,150.00,Standard subscription
                    1002,2025-01-16,PRD-002,75.50,Basic plan
                    1003,01/15/2025,PRD-003,200.00,Premium subscription
                    1004,2025-01-17,PRD-004,50.25,Trial subscription
                    1005,2025-01-18,PRD-005,999.99,Enterprise plan
                    """
                    st.code(input_data, language="csv")
                    
                    # Show as table
                    st.subheader("Data Preview")
                    try:
                        df = pd.read_csv(io.StringIO(input_data))
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error parsing CSV data: {str(e)}")
                        
                elif file_type == "json":
                    input_data = """
                    [
                      {
                        "customer_id": 1001,
                        "transaction_date": "2025-01-15",
                        "product_code": "PRD-001",
                        "amount": 150.00,
                        "description": "Standard subscription"
                      },
                      {
                        "customer_id": 1002,
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
                    st.code(input_data, language="json")
                    
                    # Show as table
                    st.subheader("Data Preview")
                    try:
                        df = pd.DataFrame(json.loads(input_data.strip()))
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error parsing JSON data: {str(e)}")
                        
                elif file_type == "excel":
                    st.info("Excel file preview - showing sample data")
                    # Create sample Excel-like data
                    data = {
                        "customer_id": [1001, 1002, 1003, 1004, 1005],
                        "transaction_date": ["2025-01-15", "2025-01-16", "01/15/2025", "2025-01-17", "2025-01-18"],
                        "product_code": ["PRD-001", "PRD-002", "PRD-003", "PRD-004", "PRD-005"],
                        "amount": [150.00, 75.50, 200.00, 50.25, 999.99],
                        "description": ["Standard subscription", "Basic plan", "Premium subscription", "Trial subscription", "Enterprise plan"]
                    }
                    
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                elif file_type == "pdf":
                    st.info("PDF file preview - showing extracted text")
                    st.code("""
                    INVOICE
                    
                    Customer ID: 1001
                    Date: 2025-01-15
                    
                    Product: PRD-001
                    Description: Standard subscription
                    Amount: $150.00
                    
                    Thank you for your business!
                    """, language="text")
                    
                elif file_type == "word":
                    st.info("Word document preview - showing extracted text")
                    st.code("""
                    TRANSACTION RECORD
                    
                    Customer Information:
                    ID: 1001
                    Date: January 15, 2025
                    
                    Transaction Details:
                    Product Code: PRD-001
                    Description: Standard subscription
                    Amount: $150.00
                    
                    Additional Notes:
                    This is a monthly subscription that will renew automatically.
                    """, language="text")
                    
                else:
                    st.info(f"Sample data preview not available for {file_type.upper()} files")
            
            # Output Data Tab
            with output_tab:
                st.subheader("Standardized Output Format")
                
                # Show the transformed data in a standard format
                transformed_data = """
                {
                  "metadata": {
                    "source_file": "EXAMPLE_FILE.FILE_EXTENSION",
                    "source_format": "FILE_TYPE",
                    "processing_timestamp": "2025-08-11T17:30:00+10:00",
                    "record_count": 5,
                    "processing_time_ms": 1250
                  },
                  "data": [
                    {
                      "customer": {
                        "id": "1001",
                        "type": "individual"
                      },
                      "transaction": {
                        "date": "2025-01-15T00:00:00",
                        "product": "PRD-001",
                        "amount": 150.00,
                        "currency": "USD",
                        "description": "Standard subscription"
                      }
                    },
                    {
                      "customer": {
                        "id": "1002",
                        "type": "individual"
                      },
                      "transaction": {
                        "date": "2025-01-16T00:00:00",
                        "product": "PRD-002",
                        "amount": 75.50,
                        "currency": "USD",
                        "description": "Basic plan"
                      }
                    }
                  ]
                }
                """.replace("EXAMPLE_FILE", file['filename']).replace("FILE_EXTENSION", file_type).replace("FILE_TYPE", file_type.upper())
                
                st.code(transformed_data, language="json")
                
                # Show transformed data as table
                st.subheader("Transformed Data Preview")
                try:
                    # Parse the JSON string
                    transformed_json = json.loads(transformed_data.strip())
                    
                    # Extract the data array
                    data_array = transformed_json.get("data", [])
                    
                    # Flatten the nested structure for display
                    flattened_data = []
                    for item in data_array:
                        flat_item = {
                            "customer_id": item["customer"]["id"],
                            "customer_type": item["customer"]["type"],
                            "transaction_date": item["transaction"]["date"],
                            "product": item["transaction"]["product"],
                            "amount": item["transaction"]["amount"],
                            "currency": item["transaction"]["currency"],
                            "description": item["transaction"]["description"]
                        }
                        flattened_data.append(flat_item)
                    
                    # Create and display the dataframe
                    df = pd.DataFrame(flattened_data)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error parsing transformed data: {str(e)}")
                
                # Show transformation details
                with st.expander("Transformation Process Details"):
                    st.markdown("**Transformation Steps:**")
                    st.markdown("1. Parse input file based on format")
                    st.markdown("2. Extract and normalize field names")
                    st.markdown("3. Convert data types to standard formats")
                    st.markdown("4. Apply business rules and enrichment")
                    st.markdown("5. Structure data in common output format")
                    
                    st.markdown("**Transformation Performance:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Processing Time", f"{random.uniform(0.5, 2.0):.2f}s")
                    with col2:
                        st.metric("Records Processed", random.randint(5, 20))
                    with col3:
                        st.metric("Fields Transformed", random.randint(10, 30))
