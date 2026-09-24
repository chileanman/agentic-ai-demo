import random
import time


class StorageAgent:
    """
    Agent responsible for storing transformed data into the appropriate systems.
    """

    def __init__(self):
        self.name = "Storage Agent"
        self.description = (
            "Stores transformed data into core systems and data warehouse"
        )
        self.capabilities = [
            "Data warehouse integration",
            "Core system integration",
            "Data validation",
            "Schema mapping",
        ]
        self.performance_metrics = {
            "avg_processing_time": 1.8,  # seconds
            "records_stored": 0,
            "storage_success_rate": 0.995,
            "bytes_stored": 0,
        }

        # Define target systems
        self.target_systems = [
            {
                "name": "Data Warehouse",
                "type": "warehouse",
                "status": "online",
                "latency": 0.8,  # seconds
            },
            {
                "name": "Claims Processing System",
                "type": "core",
                "status": "online",
                "latency": 0.5,  # seconds
            },
            {
                "name": "Policy Management System",
                "type": "core",
                "status": "online",
                "latency": 0.6,  # seconds
            },
            {
                "name": "Customer Relationship Management",
                "type": "core",
                "status": "online",
                "latency": 0.7,  # seconds
            },
        ]

    def store_data(self, transformed_data):
        """
        Stores transformed data into appropriate systems.

        Args:
            transformed_data (dict): Data that has been transformed into a common structure

        Returns:
            dict: Results of the storage operation
        """
        # Simulate processing time
        processing_time = random.uniform(1.0, 3.0)
        time.sleep(0.1)  # Just a small delay for demo purposes

        # Determine which systems to store the data in based on file content
        file_info = transformed_data["file_info"]
        target_systems = self._determine_target_systems(file_info)

        # Simulate storing data in each target system
        storage_results = []
        total_records = transformed_data.get("record_count", 0)
        if total_records == 0:
            # For non-tabular data, estimate record count
            if transformed_data.get("data_format") == "hierarchical":
                total_records = transformed_data.get("object_count", 100)
            elif transformed_data.get("data_format") == "document":
                total_records = random.randint(10, 100)  # Estimate for documents

        for system in target_systems:
            # Simulate system latency
            system_latency = system["latency"] * random.uniform(0.8, 1.2)

            # Simulate success rate
            success = random.random() < self.performance_metrics["storage_success_rate"]

            # Calculate records stored in this system
            records_stored = (
                total_records
                if success
                else int(total_records * random.uniform(0.5, 0.95))
            )

            storage_results.append(
                {
                    "system": system["name"],
                    "success": success,
                    "records_stored": records_stored,
                    "latency": system_latency,
                    "timestamp": time.time(),
                }
            )

            # Update metrics
            self.performance_metrics["records_stored"] += records_stored

        # Update performance metrics
        self.performance_metrics["avg_processing_time"] = (
            (
                self.performance_metrics["avg_processing_time"]
                * (len(storage_results) - 1)
                + processing_time
            )
            / len(storage_results)
            if len(storage_results) > 0
            else processing_time
        )

        # Calculate total bytes stored
        bytes_stored = transformed_data.get("file_size", 0)
        self.performance_metrics["bytes_stored"] += bytes_stored

        # Generate storage result
        storage_result = {
            "file_info": file_info,
            "target_systems": target_systems,
            "storage_results": storage_results,
            "total_records": total_records,
            "bytes_stored": bytes_stored,
            "processing_time": processing_time,
            "overall_success": all(result["success"] for result in storage_results),
        }

        return storage_result

    def _determine_target_systems(self, file_info):
        """Determine which systems should receive this data"""
        # Select systems based on file content and type
        selected_systems = []

        # Always include data warehouse
        selected_systems.append(self.target_systems[0])

        # Select core systems based on file content
        filename = file_info["filename"].lower()
        subject = file_info["subject"].lower()

        if "claim" in filename or "claim" in subject:
            selected_systems.append(self.target_systems[1])  # Claims system

        if "policy" in filename or "policy" in subject:
            selected_systems.append(self.target_systems[2])  # Policy system

        if (
            "customer" in filename
            or "customer" in subject
            or "client" in filename
            or "client" in subject
        ):
            selected_systems.append(self.target_systems[3])  # CRM system

        # If no specific systems were selected, choose a random one
        if len(selected_systems) == 1:  # Only data warehouse was selected
            random_system = random.choice(self.target_systems[1:])
            if random_system not in selected_systems:
                selected_systems.append(random_system)

        return selected_systems

    def get_performance_stats(self):
        """Returns the current performance metrics for this agent"""
        return self.performance_metrics
