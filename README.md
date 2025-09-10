# Agentic AI File Processing Demo

This demo showcases a team of AI agents working together to process files from partners and suppliers. The agents receive files via email, validate them, ask clarifying questions when needed, transform the data into a common format, and prepare it for storage in core systems and data warehouses.

## Overview

The demo simulates the following workflow:

1. **Email Agent** receives files from partners and suppliers
2. **Validation Agent** checks the files for issues and validates their structure
3. **Question Agent** generates clarifying questions when issues are detected
4. **Transformation Agent** converts data from various formats into a common structure
5. **Storage Agent** prepares the data for storage in core systems and data warehouses

## Features

- **Interactive UI** showing agent activities and file processing in real-time
- **125 example scenarios** with varying complexity levels
- **Support for multiple file types**: CSV, Excel, JSON, Word, and PDF
- **Detailed metrics** showing agent performance and processing statistics
- **Visualization** of agent activities and file processing timelines
- **Deployment information** with cost estimates for production environments

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Install pre-commit hooks (recommended for development):

```bash
pre-commit install
```

### Running the Demo

To start the demo, run the following command from the project directory:

```bash
streamlit run app.py
```

This will start the Streamlit server and open the demo in your default web browser.

## Using the Demo

1. **Select examples to process** from the sidebar:
   - Choose individual files
   - Process files by sender
   - Process files by complexity level
   - Process files by file type
   - Process all files at once

2. **View the dashboard** to see:
   - Key metrics about processed files
   - File type and complexity distribution
   - Agent activity timeline
   - Recently processed files

3. **Explore agent details** to understand:
   - Each agent's capabilities
   - Performance metrics
   - Processing steps
   - Questions generated for files with issues

4. **View file details** to see:
   - File information
   - Processing timeline
   - Clarification questions (if any)
   - Respond to questions (simulated)

5. **Reset the demo** at any time using the "Reset Demo" button in the sidebar

## Code Quality and Linting

This project uses comprehensive linting tools to maintain code quality and consistency:

### Linting Tools

- **Black**: Automatic code formatting with 88 character line length
- **Flake8**: Style checking and error detection
- **isort**: Import sorting and organization
- **Pre-commit hooks**: Automated linting before each commit

### Running Linting Tools

```bash
# Format code with Black
black .

# Check code style with Flake8
flake8 .

# Sort imports with isort
isort .

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Configuration Files

- `.flake8`: Flake8 configuration with Black-compatible settings
- `pyproject.toml`: Black and isort configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration

The pre-commit hooks will automatically run these tools before each commit to ensure code quality.

## Code Structure

- `app.py`: Main application file
- `agents/`: Contains the agent modules
  - `email_agent.py`: Handles email receiving and file extraction
  - `validation_agent.py`: Validates file structure and content
  - `question_agent.py`: Generates clarifying questions
  - `transformation_agent.py`: Transforms data into common format
  - `storage_agent.py`: Handles data storage in target systems
- `ui/`: Contains UI components
  - `dashboard.py`: Main dashboard and visualization components
  - `sidebar.py`: Sidebar with example selection options
- `utils/`: Utility functions
  - `file_utils.py`: File handling utilities
- `examples/`: Example files (simulated)
- `data/`: Processed data (simulated)

## Deployment Information

The demo includes information about deployment options and cost estimates for production environments:

### Deployment Options

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

## Customization

This demo can be extended and customized in various ways:

1. **Add real file processing**: Replace the simulated file processing with actual file parsing
2. **Integrate with real AI services**: Connect to OpenAI, Azure AI, or other AI services
3. **Add authentication**: Implement user authentication for secure access
4. **Connect to real email systems**: Integrate with email APIs to process real emails
5. **Implement real storage**: Connect to databases or data warehouses for actual data storage

## License

This project is for demonstration purposes only.

## Contact

For questions or support, please contact your project representative.
