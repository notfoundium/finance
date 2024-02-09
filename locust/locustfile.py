from locust import HttpUser, task, between, LoadTestShape


class HealthCheck(HttpUser):
    wait_time = between(10, 15)
    host = 'http://localhost:8000'

    @task
    def test_hc(self):
        self.client.get("/courses")
