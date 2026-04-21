import pytest
from httpx import AsyncClient
from app.main import TaskStatus, DeveloperTask


@pytest.mark.asyncio
@pytest.mark.integration
class TestStatusEndpoint:
    """Integration tests for the /status endpoint."""

    async def test_status_returns_200(self, client: AsyncClient):
        """Test that /status endpoint returns 200 status code."""
        response = await client.get("/status")
        assert response.status_code == 200

    async def test_status_returns_json(self, client: AsyncClient):
        """Test that /status endpoint returns JSON response."""
        response = await client.get("/status")
        data = response.json()
        assert isinstance(data, dict)

    async def test_status_returns_ok(self, client: AsyncClient):
        """Test that /status endpoint returns ok status."""
        response = await client.get("/status")
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
@pytest.mark.integration
class TestTasksEndpoint:
    """Integration tests for the /tasks endpoint."""

    async def test_tasks_returns_200(self, client: AsyncClient):
        """Test that /tasks endpoint returns 200 status code."""
        response = await client.get("/tasks")
        assert response.status_code == 200

    async def test_tasks_returns_list(self, client: AsyncClient):
        """Test that /tasks endpoint returns a list."""
        response = await client.get("/tasks")
        data = response.json()
        assert isinstance(data, list)

    async def test_tasks_returns_non_empty_list(self, client: AsyncClient):
        """Test that /tasks endpoint returns non-empty list of mock tasks."""
        response = await client.get("/tasks")
        data = response.json()
        assert len(data) > 0

    async def test_tasks_returns_valid_task_objects(self, client: AsyncClient):
        """Test that /tasks endpoint returns valid DeveloperTask objects."""
        response = await client.get("/tasks")
        data = response.json()
        for task in data:
            assert "task_id" in task
            assert "title" in task
            assert "status" in task
            assert "hours_spent" in task
            assert task["status"] in ["pending", "in_progress", "complete"]

    async def test_tasks_task_ids_are_integers(self, client: AsyncClient):
        """Test that task IDs are integers."""
        response = await client.get("/tasks")
        data = response.json()
        for task in data:
            assert isinstance(task["task_id"], int)
            assert task["task_id"] > 0

    async def test_tasks_hours_spent_are_numeric(self, client: AsyncClient):
        """Test that hours_spent values are numeric."""
        response = await client.get("/tasks")
        data = response.json()
        for task in data:
            assert isinstance(task["hours_spent"], (int, float))
            assert task["hours_spent"] >= 0


@pytest.mark.asyncio
@pytest.mark.integration
class TestReportEndpoint:
    """Integration tests for the /report endpoint."""

    async def test_report_returns_200(self, client: AsyncClient):
        """Test that /report endpoint returns 200 status code."""
        response = await client.get("/report")
        assert response.status_code == 200

    async def test_report_returns_json(self, client: AsyncClient):
        """Test that /report endpoint returns JSON response."""
        response = await client.get("/report")
        data = response.json()
        assert isinstance(data, dict)

    async def test_report_contains_total_tasks(self, client: AsyncClient):
        """Test that report contains total_tasks field."""
        response = await client.get("/report")
        data = response.json()
        assert "total_tasks" in data
        assert isinstance(data["total_tasks"], int)

    async def test_report_contains_completed_tasks(self, client: AsyncClient):
        """Test that report contains completed_tasks field."""
        response = await client.get("/report")
        data = response.json()
        assert "completed_tasks" in data
        assert isinstance(data["completed_tasks"], int)

    async def test_report_contains_total_hours_spent(self, client: AsyncClient):
        """Test that report contains total_hours_spent field."""
        response = await client.get("/report")
        data = response.json()
        assert "total_hours_spent" in data
        assert isinstance(data["total_hours_spent"], (int, float))

    async def test_report_contains_completion_rate(self, client: AsyncClient):
        """Test that report contains completion_rate field."""
        response = await client.get("/report")
        data = response.json()
        assert "completion_rate" in data
        assert isinstance(data["completion_rate"], (int, float))

    async def test_report_completed_tasks_not_exceeds_total(self, client: AsyncClient):
        """Test that completed_tasks does not exceed total_tasks."""
        response = await client.get("/report")
        data = response.json()
        assert data["completed_tasks"] <= data["total_tasks"]

    async def test_report_completion_rate_between_0_and_1(self, client: AsyncClient):
        """Test that completion_rate is between 0 and 1."""
        response = await client.get("/report")
        data = response.json()
        assert 0.0 <= data["completion_rate"] <= 1.0

    async def test_report_completion_rate_calculation(self, client: AsyncClient):
        """Test that completion_rate matches expected calculation."""
        response = await client.get("/report")
        data = response.json()
        if data["total_tasks"] > 0:
            expected_rate = round(data["completed_tasks"] / data["total_tasks"], 2)
            assert data["completion_rate"] == expected_rate

    async def test_report_total_hours_non_negative(self, client: AsyncClient):
        """Test that total_hours_spent is non-negative."""
        response = await client.get("/report")
        data = response.json()
        assert data["total_hours_spent"] >= 0


@pytest.mark.asyncio
@pytest.mark.integration
class TestLogTaskEndpoint:
    """Integration tests for the /log_task endpoint."""

    async def test_log_task_returns_200(self, client: AsyncClient):
        """Test that /log_task endpoint returns 200 status code on valid input."""
        task_data = {
            "title": "New Test Task",
            "status": "pending",
            "hours_spent": 2.5
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_returns_string_response(self, client: AsyncClient):
        """Test that /log_task returns a string response."""
        task_data = {
            "title": "New Test Task",
            "status": "pending",
            "hours_spent": 2.5
        }
        response = await client.post("/log_task", json=task_data)
        data = response.json()
        assert isinstance(data, str)

    async def test_log_task_confirms_task_id(self, client: AsyncClient):
        """Test that /log_task response mentions task ID."""
        task_data = {
            "title": "New Test Task",
            "status": "pending",
            "hours_spent": 2.5
        }
        response = await client.post("/log_task", json=task_data)
        data = response.json()
        assert "Task ID" in data
        assert "logged successfully" in data

    async def test_log_task_with_pending_status(self, client: AsyncClient):
        """Test logging a task with pending status."""
        task_data = {
            "title": "Pending Task",
            "status": "pending",
            "hours_spent": 0.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_with_in_progress_status(self, client: AsyncClient):
        """Test logging a task with in_progress status."""
        task_data = {
            "title": "In Progress Task",
            "status": "in_progress",
            "hours_spent": 5.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_with_complete_status(self, client: AsyncClient):
        """Test logging a task with complete status."""
        task_data = {
            "title": "Complete Task",
            "status": "complete",
            "hours_spent": 10.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_with_high_hours(self, client: AsyncClient):
        """Test logging a task with high hours spent."""
        task_data = {
            "title": "Long Task",
            "status": "in_progress",
            "hours_spent": 100.5
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_minimal_required_fields(self, client: AsyncClient):
        """Test logging a task with only required fields."""
        task_data = {
            "title": "Minimal Task"
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 200

    async def test_log_task_missing_title(self, client: AsyncClient):
        """Test that logging a task without title returns validation error."""
        task_data = {
            "status": "pending",
            "hours_spent": 1.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 422

    async def test_log_task_invalid_status(self, client: AsyncClient):
        """Test that invalid status returns validation error."""
        task_data = {
            "title": "Invalid Task",
            "status": "invalid_status",
            "hours_spent": 1.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 422

    async def test_log_task_negative_hours(self, client: AsyncClient):
        """Test that negative hours returns validation error."""
        task_data = {
            "title": "Negative Hours Task",
            "status": "pending",
            "hours_spent": -5.0
        }
        response = await client.post("/log_task", json=task_data)
        assert response.status_code == 422
