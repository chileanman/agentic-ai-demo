import time
import random
from utils.file_utils import update_performance_metric

class QuestionAgent:
    """
    Agent responsible for generating clarifying questions about files with issues.
    """
    
    def __init__(self):
        self.name = "Question Agent"
        self.description = "Generates clarifying questions for files with issues"
        self.capabilities = ["Question generation", "Context analysis", "Priority determination"]
        self.performance_metrics = {
            "avg_processing_time": 0.8,  # seconds
            "questions_generated": 0,
            "response_rate": 0.85,
            "question_quality": 0.92
        }
    
    def generate_questions(self, validation_result):
        """
        Generates clarifying questions based on validation issues.
        
        Args:
            validation_result (dict): Results from the validation agent
            
        Returns:
            list: List of questions to ask about the file
        """
        # Simulate processing time
        processing_time = random.uniform(0.5, 1.5)
        time.sleep(0.1)  # Just a small delay for demo purposes
        
        questions = []
        file_info = validation_result["file_info"]
        
        # Generate questions based on issues
        for issue in validation_result.get("issues", []):
            if issue["type"] == "Missing required fields":
                fields = ["customer_id", "transaction_date", "amount", "product_code"]
                field = random.choice(fields)
                questions.append({
                    "question": f"The {field} field appears to be missing in some records. Is this expected or should we use a default value?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "high" if issue["severity"] == "high" else "medium",
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Data type mismatch":
                fields = ["date", "numeric_value", "category", "identifier"]
                field = random.choice(fields)
                questions.append({
                    "question": f"We found inconsistent data types in the {field} column. What is the expected format for this field?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": issue["severity"],
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Invalid date format":
                questions.append({
                    "question": "We noticed multiple date formats in your file. Should we standardize to YYYY-MM-DD format or maintain the original formats?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": issue["severity"],
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Inconsistent naming convention":
                questions.append({
                    "question": "The column naming convention is inconsistent. Should we convert all to snake_case or maintain the original names?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "low",
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Duplicate records detected":
                questions.append({
                    "question": "We found duplicate records in the file. Should we remove duplicates or keep all records?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "medium",
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Invalid values in numeric fields":
                questions.append({
                    "question": "Some numeric fields contain non-numeric values. Should we convert these to zero, null, or exclude these records?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "high",
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Unexpected file structure":
                questions.append({
                    "question": f"The structure of {file_info['filename']} differs from what we expected. Can you confirm if this is the latest template?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "high",
                    "sender": file_info["sender"]
                })
                
            elif issue["type"] == "Encoding issues detected":
                questions.append({
                    "question": "We detected character encoding issues in the file. Should we proceed with UTF-8 encoding or maintain the original encoding?",
                    "context": f"Issue detected in {file_info['filename']}",
                    "priority": "medium",
                    "sender": file_info["sender"]
                })
        
        # Update performance metrics
        self.performance_metrics["questions_generated"] += len(questions)
        self.performance_metrics["avg_processing_time"] = update_performance_metric(
            self.performance_metrics["avg_processing_time"],
            self.performance_metrics["questions_generated"],
            processing_time
        )
        
        return questions
    
    def get_performance_stats(self):
        """Returns the current performance metrics for this agent"""
        return self.performance_metrics
