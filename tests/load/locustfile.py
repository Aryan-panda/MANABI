import random
from locust import HttpUser, task, between


class ManabiPlatformUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def check_health(self):
        self.client.get("/health")
        self.client.get("/metrics")

    @task(5)
    def test_engineering_calculator(self):
        calc_payloads = [
            {
                "calculation_type": "qps",
                "parameters": {
                    "daily_active_users": 100000,
                    "actions_per_user_day": 50,
                    "peak_multiplier": 2.5,
                    "read_ratio": 0.8
                }
            },
            {
                "calculation_type": "storage",
                "parameters": {
                    "daily_records": 1000000,
                    "average_record_size_bytes": 500,
                    "retention_years": 3,
                    "indexing_overhead_percent": 25,
                    "replication_factor": 3
                }
            },
            {
                "calculation_type": "bandwidth",
                "parameters": {
                    "peak_qps": 1500,
                    "average_request_payload_bytes": 1024,
                    "average_response_payload_bytes": 8192
                }
            }
        ]
        payload = random.choice(calc_payloads)
        self.client.post("/api/v1/engineering/calculate", json=payload)

    @task(3)
    def test_mermaid_diagram_generation(self):
        self.client.get("/api/v1/engineering/diagram?diagram_type=system&title=LoadTestArchitecture")

    @task(2)
    def test_academic_plan_review(self):
        review_payload = {
            "student_id": "STU1001",
            "proposed_plan": "1. CS301: Distributed Systems (4 credits)\n2. CS304: Database Engines (4 credits)\n3. CS308: Machine Learning Systems (3 credits)\nTotal: 11 credits"
        }
        self.client.post("/api/v1/academic/plan/review", json=review_payload)
