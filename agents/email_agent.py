import time
from datetime import datetime
import random
from utils.file_utils import update_performance_metric

class EmailAgent:
    """
    Agent responsible for receiving and processing incoming emails with file attachments.
    """
    
    def __init__(self):
        self.name = "Email Agent"
        self.description = "Monitors incoming emails and extracts file attachments"
        self.capabilities = ["Email monitoring", "File extraction", "Sender verification"]
        self.performance_metrics = {
            "avg_processing_time": 1.2,  # seconds
            "success_rate": 0.99,
            "emails_processed": 0
        }
    
    def receive_email(self, email_data):
        """
        Simulates receiving an email with a file attachment.
        
        Args:
            email_data (dict): Contains email metadata and file information
            
        Returns:
            dict: File information extracted from the email
        """
        # Simulate processing time
        processing_time = random.uniform(0.8, 2.0)
        time.sleep(0.1)  # Just a small delay for demo purposes
        
        # Update performance metrics
        self.performance_metrics["emails_processed"] += 1
        self.performance_metrics["avg_processing_time"] = update_performance_metric(
            self.performance_metrics["avg_processing_time"],
            self.performance_metrics["emails_processed"],
            processing_time
        )
        
        # Extract file information
        file_info = {
            "filename": email_data["filename"],
            "file_type": email_data["file_type"],
            "sender": email_data["sender"],
            "sender_email": email_data["sender_email"],
            "subject": email_data["subject"],
            "received_time": datetime.now(),
            "email_body": email_data.get("email_body", ""),
            "file_path": f"examples/{email_data['filename']}",
            "processing_time": processing_time,
            "complexity": email_data["complexity"]
        }
        
        return file_info
    
    def get_performance_stats(self):
        """Returns the current performance metrics for this agent"""
        return self.performance_metrics
