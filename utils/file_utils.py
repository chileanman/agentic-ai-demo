import json
import random
from datetime import datetime

import pandas as pd


def load_example_files():
    """
    In a real application, this would load actual example files.
    For this demo, we'll simulate the file loading.
    """
    # This is a placeholder function that would normally load real files
    return True


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
        {"name": "Secure Financial", "email": "data@securefinancial.com"},
    ]

    # Define file types and their templates
    file_templates = {
        "csv": [
            "monthly_claims_{}.csv",
            "customer_data_{}.csv",
            "policy_renewals_{}.csv",
            "transaction_log_{}.csv",
            "risk_assessment_{}.csv",
        ],
        "excel": [
            "financial_report_{}.xlsx",
            "claims_analysis_{}.xlsx",
            "customer_portfolio_{}.xlsx",
            "underwriting_summary_{}.xlsx",
            "market_trends_{}.xlsx",
        ],
        "json": [
            "api_response_{}.json",
            "system_integration_{}.json",
            "customer_profile_{}.json",
            "policy_details_{}.json",
            "claim_events_{}.json",
        ],
        "word": [
            "legal_document_{}.docx",
            "policy_terms_{}.docx",
            "compliance_report_{}.docx",
            "customer_correspondence_{}.docx",
            "executive_summary_{}.docx",
        ],
        "pdf": [
            "signed_agreement_{}.pdf",
            "regulatory_filing_{}.pdf",
            "claim_documentation_{}.pdf",
            "benefit_statement_{}.pdf",
            "annual_report_{}.pdf",
        ],
    }

    # Define subjects
    subjects = {
        "csv": [
            "Monthly Claims Data for {}",
            "Customer Data Update - {}",
            "Policy Renewals for Q{}",
            "Transaction Log for {}",
            "Risk Assessment Results - {}",
        ],
        "excel": [
            "Financial Report - Q{} 2025",
            "Claims Analysis for {}",
            "Customer Portfolio Review - {}",
            "Underwriting Summary - {}",
            "Market Trends Analysis - Q{} 2025",
        ],
        "json": [
            "API Integration Data - {}",
            "System Integration Payload - {}",
            "Customer Profiles - Batch {}",
            "Policy Details Export - {}",
            "Claim Events Log - {}",
        ],
        "word": [
            "Legal Document Review - {}",
            "Updated Policy Terms - {}",
            "Compliance Report - Q{} 2025",
            "Customer Correspondence - {}",
            "Executive Summary - {}",
        ],
        "pdf": [
            "Signed Agreement - {} Partnership",
            "Regulatory Filing - {} Submission",
            "Claim Documentation - Case {}",
            "Benefit Statement - {} Plan",
            "Annual Report - {} Division",
        ],
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
                    identifier = random.choice(["A", "B", "C", "D", "E"]) + str(
                        random.randint(100, 999)
                    )

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
                        "email_body": f"Please find attached the {subject.lower()}. Let me know if you need any clarification.",
                    }

                    example_id += 1

    return examples


def create_sample_csv(filename, complexity="low"):
    """
    Create a sample CSV file with varying complexity.
    """
    # Define number of rows and columns based on complexity
    if complexity == "low":
        rows = 50
        columns = 5
        missing_rate = 0.05
    elif complexity == "medium":
        rows = 200
        columns = 10
        missing_rate = 0.1
    else:  # high
        rows = 500
        columns = 15
        missing_rate = 0.2

    # Create a DataFrame with random data
    data = {}

    # Add ID column
    data["id"] = [f"ID{i:04d}" for i in range(1, rows + 1)]

    # Add date column
    start_date = datetime(2025, 1, 1)
    data["date"] = pd.date_range(start=start_date, periods=rows)

    # Add numeric columns
    for i in range(columns - 3):  # -3 for id, date, and category
        data[f"value_{i+1}"] = [random.uniform(100, 10000) for _ in range(rows)]

    # Add category column
    categories = ["A", "B", "C", "D", "E"]
    data["category"] = [random.choice(categories) for _ in range(rows)]

    # Create DataFrame
    df = pd.DataFrame(data)

    # Introduce missing values based on complexity
    for col in df.columns:
        if col != "id":  # Don't mess with the ID column
            mask = pd.Series([random.random() < missing_rate for _ in range(rows)])
            df.loc[mask, col] = None

    # Save to file
    df.to_csv(filename, index=False)

    return {"rows": rows, "columns": columns, "missing_rate": missing_rate}


def create_sample_json(filename, complexity="low"):
    """
    Create a sample JSON file with varying complexity.
    """
    # Define structure complexity based on complexity level
    if complexity == "low":
        records = 10
        depth = 2
        fields_per_level = 3
    elif complexity == "medium":
        records = 30
        depth = 3
        fields_per_level = 5
    else:  # high
        records = 50
        depth = 4
        fields_per_level = 8

    # Create a nested structure
    def create_nested(current_depth, max_depth, fields):
        if current_depth >= max_depth:
            return random.choice(
                [
                    random.randint(1, 1000),
                    random.uniform(1, 1000),
                    "".join(
                        random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(5)
                    ),
                    random.choice([True, False]),
                ]
            )

        result = {}
        for i in range(fields):
            if random.random() < 0.3 and current_depth < max_depth - 1:
                # Create an array of objects
                result[f"array_{i}"] = [
                    create_nested(current_depth + 1, max_depth, max(2, fields // 2))
                    for _ in range(random.randint(2, 5))
                ]
            else:
                # Create a nested object
                result[f"field_{i}"] = create_nested(
                    current_depth + 1, max_depth, fields
                )

        return result

    # Create the root object with multiple records
    data = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "version": "1.0",
            "record_count": records,
        },
        "records": [create_nested(0, depth, fields_per_level) for _ in range(records)],
    }

    # Save to file
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    return {"records": records, "depth": depth, "fields_per_level": fields_per_level}


def update_performance_metric(current_avg, current_count, new_value):
    """
    Efficiently update a running average performance metric.

    Args:
        current_avg (float): Current average value
        current_count (int): Current count of items
        new_value (float): New value to incorporate

    Returns:
        float: Updated average
    """
    if current_count == 0:
        return new_value
    return (current_avg * (current_count - 1) + new_value) / current_count
