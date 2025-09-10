import time
import random
from utils.file_utils import update_performance_metric

class ValidationAgent:
    """
    Agent responsible for validating incoming files and identifying issues.
    """
    
    def __init__(self):
        self.name = "Validation Agent"
        self.description = "Validates file structure, content, and identifies issues"
        self.capabilities = ["Format validation", "Schema validation", "Data quality checks"]
        self.performance_metrics = {
            "avg_processing_time": 1.5,  # seconds
            "issues_detected": 0,
            "files_validated": 0,
            "accuracy": 0.98
        }
    
    def validate_file(self, file_info):
        """
        Validates a file and identifies any issues.
        
        Args:
            file_info (dict): Information about the file to validate
            
        Returns:
            dict: Validation results including any issues found
        """
        # Simulate processing time
        processing_time = random.uniform(1.0, 3.0)
        time.sleep(0.1)  # Just a small delay for demo purposes
        
        # Update performance metrics
        self.performance_metrics["files_validated"] += 1
        self.performance_metrics["avg_processing_time"] = update_performance_metric(
            self.performance_metrics["avg_processing_time"],
            self.performance_metrics["files_validated"],
            processing_time
        )
        
        # Determine if file needs clarification based on complexity
        # More complex files are more likely to need clarification
        needs_clarification = False
        if file_info["complexity"] == "high":
            needs_clarification = random.random() < 0.7  # 70% chance
        elif file_info["complexity"] == "medium":
            needs_clarification = random.random() < 0.4  # 40% chance
        else:  # low complexity
            needs_clarification = random.random() < 0.1  # 10% chance
            
        if needs_clarification:
            self.performance_metrics["issues_detected"] += 1
            
        # Generate validation results
        validation_result = {
            "file_info": file_info,
            "is_valid": True,  # File is valid but may need clarification
            "needs_clarification": needs_clarification,
            "issues": [],
            "processing_time": processing_time
        }
        
        # Add simulated issues if clarification is needed
        if needs_clarification:
            possible_issues = [
                "Missing required fields",
                "Data type mismatch",
                "Invalid date format",
                "Inconsistent naming convention",
                "Duplicate records detected",
                "Invalid values in numeric fields",
                "Unexpected file structure",
                "Encoding issues detected"
            ]
            
            # Select 1-3 random issues
            num_issues = random.randint(1, 3)
            selected_issues = random.sample(possible_issues, num_issues)
            
            for issue in selected_issues:
                validation_result["issues"].append({
                    "type": issue,
                    "severity": random.choice(["low", "medium", "high"]),
                    "description": f"Found {issue.lower()} in the file"
                })
        
        return validation_result
    
    def get_performance_stats(self):
        """Returns the current performance metrics for this agent"""
        return self.performance_metrics
