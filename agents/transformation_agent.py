import time
import random
import json

class TransformationAgent:
    """
    Agent responsible for transforming data from various file formats into a common structure.
    """
    
    def __init__(self):
        self.name = "Transformation Agent"
        self.description = "Transforms data from various formats into a common structure"
        self.capabilities = ["CSV processing", "Excel processing", "JSON processing", "Word processing", "PDF extraction"]
        self.performance_metrics = {
            "avg_processing_time": 2.5,  # seconds
            "files_processed": 0,
            "transformation_accuracy": 0.97,
            "bytes_processed": 0
        }
        
        # Define processors for different file types
        self.processors = {
            "csv": self._process_csv,
            "excel": self._process_excel,
            "json": self._process_json,
            "word": self._process_word,
            "pdf": self._process_pdf
        }
    
    def transform_data(self, file_info, validation_result):
        """
        Transforms file data into a common structure.
        
        Args:
            file_info (dict): Information about the file to transform
            validation_result (dict): Results from the validation agent
            
        Returns:
            dict: Transformed data in a common structure
        """
        # Simulate processing time based on complexity
        complexity_factor = {"low": 1.0, "medium": 2.0, "high": 3.5}
        base_time = random.uniform(1.0, 2.0)
        processing_time = base_time * complexity_factor.get(file_info["complexity"], 1.0)
        time.sleep(0.1)  # Just a small delay for demo purposes
        
        # Update performance metrics
        self.performance_metrics["files_processed"] += 1
        self.performance_metrics["avg_processing_time"] = (
            (self.performance_metrics["avg_processing_time"] * (self.performance_metrics["files_processed"] - 1) + processing_time) / 
            self.performance_metrics["files_processed"]
        )
        
        # Simulate file size based on complexity
        file_size = random.randint(10, 100) * complexity_factor.get(file_info["complexity"], 1.0) * 1024  # in bytes
        self.performance_metrics["bytes_processed"] += file_size
        
        # Process the file based on its type
        file_type = file_info["file_type"].lower()
        processor = self.processors.get(file_type, self._process_unknown)
        
        # Call the appropriate processor
        transformed_data = processor(file_info, validation_result)
        transformed_data["processing_time"] = processing_time
        transformed_data["file_size"] = file_size
        
        return transformed_data
    
    def _process_csv(self, file_info, validation_result):
        """Process CSV files"""
        # Simulate CSV processing
        return {
            "file_info": file_info,
            "data_format": "tabular",
            "record_count": random.randint(50, 5000),
            "column_count": random.randint(5, 30),
            "schema": self._generate_schema("tabular"),
            "sample_data": self._generate_sample_data("tabular"),
            "transformation_steps": [
                "Header normalization",
                "Data type conversion",
                "Missing value handling",
                "Duplicate removal" if random.random() > 0.7 else None,
                "Date format standardization" if "date" in file_info["filename"].lower() else None
            ],
            "issues_resolved": len(validation_result.get("issues", [])),
            "format": "csv"
        }
    
    def _process_excel(self, file_info, validation_result):
        """Process Excel files"""
        # Simulate Excel processing
        sheet_count = random.randint(1, 5)
        sheets = []
        
        for i in range(sheet_count):
            sheets.append({
                "name": f"Sheet{i+1}",
                "record_count": random.randint(20, 1000),
                "column_count": random.randint(5, 20)
            })
            
        return {
            "file_info": file_info,
            "data_format": "multi_sheet",
            "sheet_count": sheet_count,
            "sheets": sheets,
            "schema": self._generate_schema("tabular"),
            "sample_data": self._generate_sample_data("tabular"),
            "transformation_steps": [
                "Sheet consolidation" if sheet_count > 1 else None,
                "Formula evaluation",
                "Header normalization",
                "Data type conversion",
                "Missing value handling"
            ],
            "issues_resolved": len(validation_result.get("issues", [])),
            "format": "excel"
        }
    
    def _process_json(self, file_info, validation_result):
        """Process JSON files"""
        # Simulate JSON processing
        return {
            "file_info": file_info,
            "data_format": "hierarchical",
            "depth": random.randint(2, 6),
            "object_count": random.randint(10, 1000),
            "schema": self._generate_schema("hierarchical"),
            "sample_data": self._generate_sample_data("hierarchical"),
            "transformation_steps": [
                "Flattening nested structures",
                "Array normalization",
                "Key standardization",
                "Type conversion"
            ],
            "issues_resolved": len(validation_result.get("issues", [])),
            "format": "json"
        }
    
    def _process_word(self, file_info, validation_result):
        """Process Word documents"""
        # Simulate Word document processing
        return {
            "file_info": file_info,
            "data_format": "document",
            "page_count": random.randint(1, 50),
            "word_count": random.randint(100, 10000),
            "tables_extracted": random.randint(0, 5),
            "schema": self._generate_schema("document"),
            "sample_data": self._generate_sample_data("document"),
            "transformation_steps": [
                "Text extraction",
                "Table detection and extraction",
                "Structure identification",
                "Content classification",
                "Metadata extraction"
            ],
            "issues_resolved": len(validation_result.get("issues", [])),
            "format": "word"
        }
    
    def _process_pdf(self, file_info, validation_result):
        """Process PDF files"""
        # Simulate PDF processing
        return {
            "file_info": file_info,
            "data_format": "document",
            "page_count": random.randint(1, 100),
            "is_scanned": random.choice([True, False]),
            "tables_extracted": random.randint(0, 10),
            "schema": self._generate_schema("document"),
            "sample_data": self._generate_sample_data("document"),
            "transformation_steps": [
                "OCR processing" if random.random() > 0.5 else None,
                "Text extraction",
                "Layout analysis",
                "Table detection and extraction",
                "Form field identification",
                "Content classification"
            ],
            "issues_resolved": len(validation_result.get("issues", [])),
            "format": "pdf"
        }
    
    def _process_unknown(self, file_info, validation_result):
        """Process unknown file types"""
        return {
            "file_info": file_info,
            "data_format": "unknown",
            "error": "Unsupported file format",
            "issues_resolved": 0,
            "format": "unknown"
        }
    
    def _generate_schema(self, data_format):
        """Generate a sample schema based on data format"""
        if data_format == "tabular":
            return {
                "fields": [
                    {"name": "id", "type": "string", "required": True},
                    {"name": "date", "type": "date", "required": True},
                    {"name": "amount", "type": "decimal", "required": True},
                    {"name": "category", "type": "string", "required": False},
                    {"name": "description", "type": "string", "required": False}
                ]
            }
        elif data_format == "hierarchical":
            return {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string"},
                                "value": {"type": "number"}
                            }
                        }
                    }
                }
            }
        elif data_format == "document":
            return {
                "sections": [
                    {"name": "header", "type": "metadata"},
                    {"name": "body", "type": "content"},
                    {"name": "tables", "type": "structured_data"}
                ]
            }
        else:
            return {"error": "Unknown format"}
    
    def _generate_sample_data(self, data_format):
        """Generate sample data based on data format"""
        if data_format == "tabular":
            return [
                {"id": "A001", "date": "2025-01-15", "amount": 1250.00, "category": "Insurance", "description": "Annual premium"},
                {"id": "A002", "date": "2025-01-16", "amount": 750.50, "category": "Claims", "description": "Property damage"}
            ]
        elif data_format == "hierarchical":
            return {
                "id": "TX123456",
                "timestamp": "2025-01-15T14:30:00Z",
                "data": [
                    {"key": "premium", "value": 1250.00},
                    {"key": "coverage", "value": 500000.00}
                ]
            }
        elif data_format == "document":
            return {
                "header": {"title": "Insurance Policy", "date": "2025-01-15"},
                "body": "This document contains policy information...",
                "tables": [{"name": "Coverage", "rows": 5, "columns": 3}]
            }
        else:
            return {"error": "Unknown format"}
    
    def get_performance_stats(self):
        """Returns the current performance metrics for this agent"""
        return self.performance_metrics
